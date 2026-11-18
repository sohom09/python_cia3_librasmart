"""
Builds every dataset used by the LibraSmart dashboard.

REAL data      : the book catalogue (Kaggle "7k Books with Metadata" CSV).
SIMULATED data : library entries, seat occupancy, borrowing, returns and fines
                 (the library does not publish live data).

Usage
-----
    python generate_data.py                      # looks for data/kaggle_books.csv or data/books.csv
    python generate_data.py path/to/books.csv    # use a specific Kaggle CSV

If no Kaggle CSV is found, a synthetic catalogue is created so the app still runs.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from common import (
    DAY_FACTOR, DEPARTMENTS, DEPT_CODE, FINE_PER_DAY, HOUR_PROFILE, LOAN_DAYS,
    OPEN_HOURS, SUNDAY_HOURS, TECH_DEPTS, TOTAL_SEATS, ZONE_BIAS, ZONE_FLOOR,
    ZONE_NAMES, ZONE_SEATS, ZONES,
)

ROOT = Path(__file__).parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
RNG = np.random.default_rng(42)

N_DAYS = 35            # days of history
PEAK_ARRIVALS = 100    # students arriving in the busiest hour of a normal day
EXAM_MULT = 1.45       # extra footfall during exam week
BORROWS_PER_DAY = 140  # book issues on a normal weekday

# Column names used by different Kaggle book datasets -> our names
COLUMN_MAP = {
    "name": "title", "book_title": "title", "book_name": "title",
    "author": "authors", "book_author": "authors",
    "genre": "categories", "category": "categories",
    "rating": "average_rating", "avg_rating": "average_rating",
    "year": "published_year", "year_of_publication": "published_year",
    "original_publication_year": "published_year",
    "pages": "num_pages", "reviews": "ratings_count", "ratings": "ratings_count",
}

# Which categories each department prefers (keyword in category -> weight multiplier)
DEPT_PREFS = {
    "MCA": {"comput": 3, "technolog": 2, "science": 1.6, "business": 1.2},
    "BTech CSE": {"comput": 3, "technolog": 2.5, "science": 1.8, "mathem": 1.5},
    "BCA": {"comput": 3, "technolog": 1.8},
    "MSc": {"science": 2.5, "mathem": 2, "comput": 1.5, "technolog": 1.3},
    "MBA": {"business": 3, "economics": 2, "biograph": 1.6, "self": 1.5},
    "BBA": {"business": 2.5, "self": 1.5},
    "BCom": {"business": 2.5, "economics": 2},
    "BA English": {"fiction": 2.5, "literary": 3, "poetry": 3, "drama": 2, "biograph": 1.5, "histor": 1.4},
}


# --------------------------------------------------------------------------- catalogue
def synthetic_catalogue(n=1500):
    topics = {
        "Computers": ["Python", "Data Structures", "Machine Learning", "Databases", "Operating Systems",
                      "Web Development", "Algorithms", "Cloud Computing", "Computer Networks", "Cyber Security"],
        "Technology & Engineering": ["Electronics", "Embedded Systems", "Robotics", "Thermodynamics", "Control Systems"],
        "Science": ["Physics", "Chemistry", "Biology", "Astronomy", "Environmental Science"],
        "Mathematics": ["Calculus", "Linear Algebra", "Statistics", "Probability", "Discrete Mathematics"],
        "Business & Economics": ["Marketing", "Finance", "Economics", "Entrepreneurship", "Accounting", "Management"],
        "Self-Help": ["Productivity", "Mindfulness", "Leadership", "Habits"],
        "History": ["Ancient India", "World War II", "Modern Europe", "The Mughal Empire"],
        "Philosophy": ["Ethics", "Logic", "Eastern Thought", "Existentialism"],
    }
    story_cats = ["Fiction", "Biography & Autobiography", "Poetry", "Literary Criticism", "Juvenile Fiction"]
    templates = ["Introduction to {t}", "{t}: A Practical Guide", "Essentials of {t}", "Advanced {t}",
                 "{t} Made Simple", "Principles of {t}", "The {t} Handbook", "Fundamentals of {t}"]
    adj = ["Silent", "Golden", "Lost", "Hidden", "Last", "Midnight", "Broken", "Distant", "Burning", "Quiet"]
    noun = ["River", "Garden", "Promise", "Kingdom", "Letter", "Mirror", "Journey", "Season", "Harbor", "Thread"]
    first = ["Anita", "Ravi", "Meera", "Karan", "Sara", "Arjun", "Priya", "Daniel", "Nisha", "Omar"]
    last = ["Sharma", "Iyer", "Fernandes", "Patel", "Nair", "Menon", "Reddy", "Thomas", "Khan", "Das"]
    rows = []
    for _ in range(n):
        if RNG.random() < 0.7:
            cat = RNG.choice(list(topics))
            title = RNG.choice(templates).format(t=RNG.choice(topics[cat]))
        else:
            cat = RNG.choice(story_cats)
            title = f"The {RNG.choice(adj)} {RNG.choice(noun)}"
        rows.append({
            "title": f"{title} (Vol. {RNG.integers(1, 4)})" if RNG.random() < 0.25 else title,
            "authors": f"{RNG.choice(first)} {RNG.choice(last)}",
            "categories": cat,
            "published_year": int(RNG.integers(1995, 2024)),
            "average_rating": round(float(np.clip(RNG.normal(3.9, 0.4), 2.2, 5.0)), 2),
            "num_pages": int(RNG.integers(120, 700)),
            "ratings_count": int(RNG.lognormal(5.5, 1.6)),
        })
    return pd.DataFrame(rows)


def load_catalogue():
    candidates = [Path(sys.argv[1])] if len(sys.argv) > 1 else [DATA / "kaggle_books.csv", DATA / "books.csv"]
    raw = next((p for p in candidates if p.exists()), None)
    if raw is None:
        print("No Kaggle CSV found -> using a synthetic catalogue (add data/kaggle_books.csv for real data).")
        return synthetic_catalogue(), "Synthetic catalogue (no Kaggle file provided)"

    df = pd.read_csv(raw, on_bad_lines="skip")
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns and v not in df.columns})
    if "title" not in df.columns:
        raise SystemExit(f"{raw.name}: could not find a title column. Columns: {list(df.columns)}")
    print(f"Loaded Kaggle catalogue: {raw.name} ({len(df)} rows)")

    df = df.dropna(subset=["title"]).copy()
    df["title"] = df["title"].astype(str).str.strip()
    df["authors"] = df.get("authors", pd.Series("Unknown", index=df.index)).fillna("Unknown").astype(str)
    df["authors"] = df["authors"].str.split(";").str[0].str.strip()
    cats = df.get("categories", pd.Series("Other", index=df.index)).fillna("Other").astype(str)
    df["categories"] = cats.str.split(r"[;,/]").str[0].str.strip().replace("", "Other")
    df["average_rating"] = pd.to_numeric(df.get("average_rating"), errors="coerce")
    df["average_rating"] = df["average_rating"].fillna(df["average_rating"].median()).clip(0, 5).round(2)
    if "ratings_count" in df.columns:
        df["ratings_count"] = pd.to_numeric(df["ratings_count"], errors="coerce")
    else:
        df["ratings_count"] = np.nan
    df["ratings_count"] = df["ratings_count"].fillna(pd.Series(RNG.lognormal(5.5, 1.6, len(df)), index=df.index)).astype(int)
    df["num_pages"] = pd.to_numeric(df.get("num_pages"), errors="coerce")
    df["num_pages"] = df["num_pages"].fillna(df["num_pages"].median() if df["num_pages"].notna().any() else 300).astype(int)
    df["published_year"] = pd.to_numeric(df.get("published_year"), errors="coerce")
    df["published_year"] = df["published_year"].fillna(df["published_year"].median() if df["published_year"].notna().any() else 2005).astype(int)
    df = df.drop_duplicates(subset="title")
    return df[["title", "authors", "categories", "published_year", "average_rating", "num_pages", "ratings_count"]], \
        "Kaggle: 7k Books with Metadata"


ACADEMIC = ["Computers", "Science", "Business & Economics", "Social Science", "Psychology", "Self-Help",
            "Education", "Mathematics", "Technology & Engineering", "Medical"]


def prepare_catalogue():
    cat, source = load_catalogue()
    present = set(cat["categories"])
    keep = list(cat["categories"].value_counts().head(8).index) + [c for c in ACADEMIC if c in present]
    cat["category"] = np.where(cat["categories"].isin(keep), cat["categories"], "Other")
    cat = cat.drop(columns="categories").reset_index(drop=True)
    cat.insert(0, "book_id", np.arange(1, len(cat) + 1))
    cat.to_csv(DATA / "catalogue.csv", index=False)
    return cat, source


# --------------------------------------------------------------------------- visits
def zone_probs(dept):
    base = np.array([ZONE_SEATS[z] * ZONE_BIAS[z] for z in ZONE_NAMES], dtype=float)
    mult = np.ones(len(ZONE_NAMES))
    if dept in TECH_DEPTS:
        mult[ZONE_NAMES.index("Computer Lab")] = 1.5
    else:
        mult[ZONE_NAMES.index("Computer Lab")] = 0.6
    if dept in {"MBA", "BBA", "BCom"}:
        mult[ZONE_NAMES.index("Group Study")] = 1.8
    if dept == "BA English":
        mult[ZONE_NAMES.index("Silent Zone")] = 1.8
        mult[ZONE_NAMES.index("Reading Hall")] = 1.4
    p = base * mult
    return p / p.sum()


def generate_entries(days, exam_days):
    dept_names = list(DEPARTMENTS)
    dept_p = np.array(list(DEPARTMENTS.values()))
    dept_p = dept_p / dept_p.sum()
    zp = {d: zone_probs(d) for d in dept_names}
    parts = []
    for day in days:
        dow = day.dayofweek
        hours = SUNDAY_HOURS if dow == 6 else OPEN_HOURS
        close = 16 if dow == 6 else 20
        exam = day in exam_days
        for h in hours:
            lam = PEAK_ARRIVALS * HOUR_PROFILE[h] * DAY_FACTOR[dow] * (EXAM_MULT if exam else 1) * RNG.uniform(0.9, 1.1)
            n = int(RNG.poisson(lam))
            if n == 0:
                continue
            depts = RNG.choice(dept_names, size=n, p=dept_p)
            zones = np.array([RNG.choice(ZONE_NAMES, p=zp[d]) for d in depts])
            entry = day + pd.Timedelta(hours=h) + pd.to_timedelta(RNG.integers(0, 60, size=n), unit="m")
            mean = 100 * (1.2 if exam else 1.0)
            dur = np.clip(RNG.lognormal(np.log(mean) - 0.1, 0.45, size=n), 15, 240)
            exit_ = entry + pd.to_timedelta(dur, unit="m")
            close_ts = day + pd.Timedelta(hours=close)
            exit_ = exit_.round("min")
            exit_ = exit_.where(exit_ <= close_ts, close_ts)
            sid = [f"{DEPT_CODE[d]}-{RNG.integers(1, 300):03d}" for d in depts]
            parts.append(pd.DataFrame({
                "student_id": sid, "department": depts, "zone": zones,
                "entry_time": entry, "exit_time": exit_, "exam_week": exam,
            }))
    df = pd.concat(parts, ignore_index=True)
    df["duration_min"] = ((df["exit_time"] - df["entry_time"]).dt.total_seconds() / 60).round().astype(int)
    df = df[df["duration_min"] >= 5].sort_values("entry_time").reset_index(drop=True)
    df["floor"] = df["zone"].map(ZONE_FLOOR)
    df.insert(0, "entry_id", np.arange(1, len(df) + 1))
    return df[["entry_id", "student_id", "department", "floor", "zone",
               "entry_time", "exit_time", "duration_min", "exam_week"]]


def hourly_occupancy(entries, days):
    """Average number of students present in each zone during each hour."""
    start = entries["entry_time"].dt.floor("h")
    frames = []
    for k in range(5):
        bs = start + pd.Timedelta(hours=k)
        be = bs + pd.Timedelta(hours=1)
        overlap = (np.minimum(entries["exit_time"], be) - np.maximum(entries["entry_time"], bs)).dt.total_seconds() / 60
        keep = overlap > 0
        frames.append(pd.DataFrame({"timestamp": bs[keep], "zone": entries.loc[keep, "zone"], "minutes": overlap[keep]}))
    occ = pd.concat(frames).groupby(["timestamp", "zone"], as_index=False)["minutes"].sum()
    occ["occupied"] = occ["minutes"] / 60

    stamps = []
    for day in days:
        hours = SUNDAY_HOURS if day.dayofweek == 6 else OPEN_HOURS
        stamps += [day + pd.Timedelta(hours=h) for h in hours]
    grid = pd.MultiIndex.from_product([stamps, ZONE_NAMES], names=["timestamp", "zone"]).to_frame(index=False)
    out = grid.merge(occ[["timestamp", "zone", "occupied"]], on=["timestamp", "zone"], how="left").fillna({"occupied": 0})
    out["floor"] = out["zone"].map(ZONE_FLOOR)
    out["capacity"] = out["zone"].map(ZONE_SEATS)
    out["occupied"] = out["occupied"].round(1)
    out["occupancy_pct"] = (out["occupied"] / out["capacity"] * 100).clip(upper=100).round(1)
    return out[["timestamp", "floor", "zone", "occupied", "capacity", "occupancy_pct"]]


# --------------------------------------------------------------------------- borrowing
def book_probs(cat):
    """Pick a category first (by department taste), then a book inside it (popular books more likely)."""
    pop = np.log1p(cat["ratings_count"].to_numpy()) + 1.0
    cats = cat["category"].to_numpy().astype(str)
    counts = pd.Series(cats).value_counts()
    probs = {}
    for dept, prefs in DEPT_PREFS.items():
        cw = {}
        for c in counts.index:
            w = np.sqrt(counts[c])
            if c in ACADEMIC:
                w *= 4          # a university library lends more academic books
            if c == "Other":
                w *= 0.5
            for key, mult in prefs.items():
                if key in c.lower():
                    w *= mult
            cw[c] = w
        total = sum(cw.values())
        p = np.zeros(len(cat))
        for c in counts.index:
            m = cats == c
            p[m] = cw[c] / total * pop[m] / pop[m].sum()
        probs[dept] = p / p.sum()
    return probs


def generate_borrowing(cat, days, exam_days, end):
    probs = book_probs(cat)
    dept_names = list(DEPARTMENTS)
    dept_p = np.array(list(DEPARTMENTS.values()))
    dept_p = dept_p / dept_p.sum()
    parts = []
    for day in days:
        n = int(RNG.poisson(BORROWS_PER_DAY * DAY_FACTOR[day.dayofweek] * (1.25 if day in exam_days else 1.0)))
        if n == 0:
            continue
        depts = RNG.choice(dept_names, size=n, p=dept_p)
        book_idx = np.empty(n, dtype=int)
        for d in set(depts):
            m = depts == d
            book_idx[m] = RNG.choice(len(cat), size=int(m.sum()), p=probs[d])
        hour = RNG.integers(9, 19, size=n)
        parts.append(pd.DataFrame({
            "department": depts, "book_idx": book_idx,
            "borrow_date": day + pd.to_timedelta(hour, unit="h"),
        }))
    df = pd.concat(parts, ignore_index=True)
    n = len(df)
    bd = df["borrow_date"].dt.normalize()
    due = bd + pd.Timedelta(days=LOAN_DAYS)
    days_open = np.maximum((end - bd).dt.days.to_numpy(), 0)
    r = RNG.random(n)
    not_due = (due > end).to_numpy()

    ret_days = np.full(n, np.nan)
    early = not_due & (r < 0.45)
    ret_days[early] = RNG.integers(0, days_open[early] + 1)
    on_time = ~not_due & (r < 0.62)
    ret_days[on_time] = RNG.integers(2, LOAN_DAYS + 1, size=on_time.sum())
    late = ~not_due & (r >= 0.62) & (r < 0.87)
    ret_days[late] = LOAN_DAYS + RNG.integers(1, 19, size=late.sum())

    ret_date = bd + pd.to_timedelta(np.nan_to_num(ret_days, nan=0), unit="D")
    ret_date = ret_date.where(~np.isnan(ret_days) & (ret_date <= end), pd.NaT)
    returned = ret_date.notna()

    late_days = np.zeros(n, dtype=int)
    late_days[returned.to_numpy()] = np.maximum((ret_date[returned] - due[returned]).dt.days.to_numpy(), 0)
    overdue = ~returned & ~pd.Series(not_due)
    late_days[overdue.to_numpy()] = (end - due[overdue]).dt.days.to_numpy()
    status = np.where(returned, "Returned", np.where(overdue, "Overdue", "Borrowed"))

    out = pd.DataFrame({
        "txn_id": np.arange(1, n + 1),
        "student_id": [f"{DEPT_CODE[d]}-{RNG.integers(1, 300):03d}" for d in df["department"]],
        "department": df["department"],
        "book_id": cat.loc[df["book_idx"], "book_id"].to_numpy(),
        "title": cat.loc[df["book_idx"], "title"].to_numpy(),
        "author": cat.loc[df["book_idx"], "authors"].to_numpy(),
        "category": cat.loc[df["book_idx"], "category"].to_numpy(),
        "borrow_date": df["borrow_date"],
        "due_date": due,
        "return_date": ret_date,
        "status": status,
        "late_days": late_days,
        "fine_inr": late_days * FINE_PER_DAY,
    })
    return out


# --------------------------------------------------------------------------- main
def main():
    end = pd.Timestamp.today().normalize()
    days = pd.date_range(end=end, periods=N_DAYS, freq="D")
    exam_days = set(days[21:28])  # one exam week in the middle of the period

    cat, source = prepare_catalogue()
    entries = generate_entries(days, exam_days)
    occ = hourly_occupancy(entries, days)
    bor = generate_borrowing(cat, days, exam_days, end)

    pd.DataFrame(ZONES, columns=["floor", "zone", "seats"]).to_csv(DATA / "seat_capacity.csv", index=False)
    entries.to_csv(DATA / "library_entries.csv", index=False)
    occ.to_csv(DATA / "occupancy_hourly.csv", index=False)
    bor.to_csv(DATA / "book_borrowing.csv", index=False)
    (DATA / "meta.json").write_text(json.dumps({
        "catalogue_source": source,
        "generated_on": str(end.date()),
        "history_days": N_DAYS,
        "n_books": int(len(cat)),
        "total_seats": TOTAL_SEATS,
        "exam_week": [str(min(exam_days).date()), str(max(exam_days).date())],
    }, indent=2))

    peak = occ.groupby("timestamp").agg(o=("occupied", "sum")).o.max() / TOTAL_SEATS * 100
    print(f"books={len(cat)}  visits={len(entries)}  hourly rows={len(occ)}  borrowings={len(bor)}")
    print(f"peak library occupancy = {peak:.0f}%   max zone occupancy = {occ.occupancy_pct.max():.0f}%")
    print(bor["status"].value_counts().to_dict(), " total fines Rs", int(bor["fine_inr"].sum()))


if __name__ == "__main__":
    main()
