"""
CHRIST LibraSmart: Library Seat Occupancy & Book Demand Analytics Dashboard
MCA411-2 Python Programming | Component 3 (Assignment)

Run locally:  streamlit run app.py
"""
import html
import json
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from matplotlib.colors import LinearSegmentedColormap
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

from common import (
    DAY_FACTOR, DAY_NAMES, DEPARTMENTS, HOUR_PROFILE, OPEN_HOURS, SUNDAY_HOURS,
    TOTAL_SEATS, ZONE_BIAS, ZONE_FLOOR, ZONE_NAMES, ZONE_SEATS, hour_label,
)

DATA = Path(__file__).parent / "data"
IST = ZoneInfo("Asia/Kolkata")

st.set_page_config(page_title="CHRIST LibraSmart", page_icon="📚", layout="wide",
                   initial_sidebar_state="expanded")

# =============================================================================
# 1. THEMES (light + dark) and CSS
# =============================================================================
THEMES = {
    "light": dict(page="#F3F4F8", card="#FFFFFF", sidebar="#FFFFFF", text="#111827", muted="#6B7280",
                  border="#E5E7EB", accent="#4F46E5", teal="#0D9488", good="#16A34A", bad="#DC2626",
                  warn="#D97706", soft="#EEF2FF", cmap_lo="#EEF2FF", cmap_hi="#4338CA"),
    "dark": dict(page="#0B1120", card="#151E32", sidebar="#0F172A", text="#E5E7EB", muted="#94A3B8",
                 border="#27344D", accent="#818CF8", teal="#2DD4BF", good="#4ADE80", bad="#F87171",
                 warn="#FBBF24", soft="#1E2A47", cmap_lo="#1E2A47", cmap_hi="#A5B4FC"),
}
PALETTE = ["#6366F1", "#14B8A6", "#F59E0B", "#F43F5E", "#38BDF8", "#A78BFA", "#84CC16", "#FB923C", "#EC4899", "#22D3EE"]

STATIC_CSS = """
.stApp{background:var(--page);color:var(--text);}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stSidebar"]{background:var(--sidebar);border-right:1px solid var(--border);}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p,[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{color:var(--text);}
.block-container{padding-top:2.2rem;padding-bottom:3rem;max-width:1500px;}
.stApp p,.stApp label,.stApp li,.stApp h1,.stApp h2,.stApp h3,.stApp h4{color:var(--text);}
.stApp [data-testid="stMarkdownContainer"]{color:var(--text);}
.stApp [data-testid="stWidgetLabel"] p{color:var(--muted);font-size:.82rem;font-weight:600;}
.stApp hr{border-color:var(--border);}
[data-testid="stSidebar"] .stCaption,.stApp [data-testid="stCaptionContainer"]{color:var(--muted);}

div[data-baseweb="select"]>div,div[data-baseweb="input"]>div,div[data-baseweb="base-input"],
.stDateInput input,.stTextInput input{background:var(--card)!important;color:var(--text)!important;
 border-color:var(--border)!important;}
div[data-baseweb="select"] span,div[data-baseweb="select"] input{color:var(--text)!important;}
div[data-baseweb="select"] svg{fill:var(--muted);}
div[data-baseweb="select"] span[data-baseweb="tag"]{background:var(--accent)!important;}
div[data-baseweb="select"] span[data-baseweb="tag"] span{color:#fff!important;}
ul[role="listbox"],div[data-baseweb="menu"]{background:var(--card)!important;}
li[role="option"]{color:var(--text)!important;background:var(--card)!important;}
li[role="option"]:hover{background:var(--soft)!important;}
[data-testid="stTickBarMin"],[data-testid="stTickBarMax"]{color:var(--muted);}
.stButton button,.stDownloadButton button{background:var(--card);color:var(--text);border:1px solid var(--border);
 border-radius:10px;font-weight:600;}
.stButton button:hover,.stDownloadButton button:hover{border-color:var(--accent);color:var(--accent);}

.stTabs [data-baseweb="tab-list"]{gap:6px;border-bottom:1px solid var(--border);}
.stTabs button[data-baseweb="tab"]{color:var(--muted);font-weight:600;padding:10px 18px;}
.stTabs button[data-baseweb="tab"][aria-selected="true"]{color:var(--accent);}
.stTabs [data-baseweb="tab-highlight"]{background:var(--accent);}

div[class*="st-key-card"]{background:var(--card);border:1px solid var(--border);border-radius:14px;
 padding:16px 18px 12px 18px;}
.card-title{font-weight:700;font-size:1rem;color:var(--text);}
.card-sub{color:var(--muted);font-size:.8rem;margin:2px 0 8px 0;}
.insight{background:var(--soft);border-left:3px solid var(--accent);border-radius:8px;padding:8px 12px;
 font-size:.82rem;color:var(--text);margin-top:6px;}

.hero{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:14px;gap:12px;flex-wrap:wrap;}
.hero-title{font-size:1.65rem;font-weight:800;color:var(--text);line-height:1.2;}
.hero-sub{color:var(--muted);font-size:.9rem;margin-top:2px;}
.live-pill{display:inline-flex;align-items:center;gap:8px;background:var(--card);border:1px solid var(--border);
 border-radius:999px;padding:6px 14px;font-size:.8rem;font-weight:600;color:var(--text);}
.dot{width:9px;height:9px;border-radius:50%;background:var(--good);animation:pulse 1.6s infinite;}
.dot.off{background:var(--muted);animation:none;}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(34,197,94,.55);}70%{box-shadow:0 0 0 8px rgba(34,197,94,0);}100%{box-shadow:0 0 0 0 rgba(34,197,94,0);}}
@media (prefers-reduced-motion:reduce){.dot{animation:none;}}

.kpi{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:14px 16px;height:100%;}
.kpi-top{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:.78rem;font-weight:600;}
.kpi-ico{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;
 background:var(--soft);font-size:.95rem;}
.kpi-val{font-size:1.85rem;font-weight:800;color:var(--text);line-height:1.15;margin:8px 0 4px 0;}
.kpi-sub{font-size:.78rem;color:var(--muted);}
.chip{display:inline-block;padding:1px 8px;border-radius:999px;font-weight:700;font-size:.75rem;margin-right:4px;}
.chip.up{background:rgba(34,197,94,.15);color:var(--good);}
.chip.down{background:rgba(239,68,68,.15);color:var(--bad);}

.brand{font-size:1.15rem;font-weight:800;color:var(--text);line-height:1.2;margin-bottom:2px;}
.brand span{font-size:.75rem;font-weight:500;color:var(--muted);}
.mini{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border);
 font-size:.85rem;color:var(--text);}
.mini:last-child{border-bottom:none;}
.mini b{color:var(--accent);}

.tbl-wrap{overflow-x:auto;}
.tbl{width:100%;border-collapse:collapse;font-size:.84rem;}
.tbl th{color:var(--muted);text-align:left;font-weight:600;padding:8px 10px;border-bottom:1px solid var(--border);
 font-size:.75rem;white-space:nowrap;}
.tbl td{padding:9px 10px;border-bottom:1px solid var(--border);color:var(--text);white-space:nowrap;}
.badge{padding:3px 10px;border-radius:999px;font-size:.74rem;font-weight:700;}
.b-green{background:rgba(34,197,94,.15);color:var(--good);}
.b-blue{background:rgba(99,102,241,.18);color:var(--accent);}
.b-red{background:rgba(239,68,68,.15);color:var(--bad);}
.b-amber{background:rgba(245,158,11,.18);color:var(--warn);}
.foot{color:var(--muted);font-size:.78rem;text-align:center;margin-top:28px;}
"""


def inject_css(T):
    root = ":root{" + "".join(f"--{k}:{v};" for k, v in T.items()) + "}"
    st.markdown(f"<style>{root}{STATIC_CSS}</style>", unsafe_allow_html=True)


# =============================================================================
# 2. DATA LOADING
# =============================================================================
@st.cache_data(show_spinner="Loading library data...")
def load_data():
    ent = pd.read_csv(DATA / "library_entries.csv", parse_dates=["entry_time", "exit_time"])
    ent["date"] = ent["entry_time"].dt.normalize()
    ent["hour"] = ent["entry_time"].dt.hour
    ent["dow"] = ent["entry_time"].dt.dayofweek

    occ = pd.read_csv(DATA / "occupancy_hourly.csv", parse_dates=["timestamp"])
    occ["date"] = occ["timestamp"].dt.normalize()
    occ["hour"] = occ["timestamp"].dt.hour
    occ["dow"] = occ["timestamp"].dt.dayofweek

    bor = pd.read_csv(DATA / "book_borrowing.csv", parse_dates=["borrow_date", "due_date", "return_date"])
    bor["date"] = bor["borrow_date"].dt.normalize()

    cat = pd.read_csv(DATA / "catalogue.csv")
    meta = json.loads((DATA / "meta.json").read_text())
    return ent, occ, bor, cat, meta


ENT, OCC, BOR, CAT, META = load_data()
DATA_END = ENT["date"].max()


# =============================================================================
# 3. SMALL HELPERS (cards, KPIs, tables, matplotlib styling)
# =============================================================================
def stretch(fn, *args, **kwargs):
    """Call a Streamlit element so it fills the width (works across Streamlit versions)."""
    try:
        return fn(*args, width="stretch", **kwargs)
    except TypeError:
        return fn(*args, use_container_width=True, **kwargs)


@contextmanager
def card(title, sub=""):
    key = "card_" + "".join(c for c in title.lower() if c.isalnum())
    with st.container(key=key):
        st.markdown(f'<div class="card-title">{title}</div><div class="card-sub">{sub}</div>', unsafe_allow_html=True)
        yield


def insight(text):
    st.markdown(f'<div class="insight">💡 {text}</div>', unsafe_allow_html=True)


def pct_change(cur, prev):
    return (cur - prev) / prev * 100 if prev else float("nan")


def kpi(icon, label, value, sub="", delta=None, good_up=True):
    chip = ""
    if delta is not None and not np.isnan(delta):
        up = delta >= 0
        cls = "up" if up == good_up else "down"
        chip = f'<span class="chip {cls}">{"▲" if up else "▼"} {abs(delta):.1f}%</span>'
    return (f'<div class="kpi"><div class="kpi-top"><span class="kpi-ico">{icon}</span>{label}</div>'
            f'<div class="kpi-val">{value}</div><div class="kpi-sub">{chip}{sub}</div></div>')


def html_table(df, badge_col=None, empty="No records for the selected filters."):
    if df.empty:
        return f'<div class="card-sub">{empty}</div>'
    badge = {"Returned": "b-green", "Borrowed": "b-blue", "Overdue": "b-red", "IN": "b-green", "OUT": "b-amber"}
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, r in df.iterrows():
        tds = []
        for c in df.columns:
            v = html.escape(str(r[c]))
            if c == badge_col:
                v = f'<span class="badge {badge.get(str(r[c]), "b-blue")}">{v}</span>'
            tds.append(f"<td>{v}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def new_fig(T, w=6.2, h=3.3, nrows=1, ncols=1):
    fig, axes = plt.subplots(nrows, ncols, figsize=(w, h))
    fig.patch.set_facecolor(T["card"])
    for ax in np.atleast_1d(axes).ravel():
        ax.set_facecolor(T["card"])
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(T["border"])
        ax.tick_params(colors=T["muted"], labelsize=8)
        ax.xaxis.label.set_color(T["muted"])
        ax.yaxis.label.set_color(T["muted"])
        ax.title.set_color(T["text"])
        ax.grid(axis="y", color=T["border"], alpha=0.7, linewidth=0.6)
        ax.set_axisbelow(True)
    return fig, axes


def legend(ax, T, **kw):
    kw.setdefault("fontsize", 8)
    leg = ax.legend(frameon=False, **kw)
    for t in leg.get_texts():
        t.set_color(T["text"])
    return leg


def show(fig):
    stretch(st.pyplot, fig)
    plt.close(fig)


def overall(occ):
    """Library-wide occupancy per (date, hour) for the selected zones."""
    g = occ.groupby(["date", "hour", "dow"], as_index=False).agg(occupied=("occupied", "sum"), capacity=("capacity", "sum"))
    g["pct"] = (g["occupied"] / g["capacity"] * 100).clip(upper=100)
    return g


# =============================================================================
# 4. LIVE SIMULATION (real-time feel: occupancy updates every few seconds)
# =============================================================================
def is_open(clock):
    h, dow = clock.hour, clock.weekday()
    return (10 <= h < 16) if dow == 6 else (8 <= h < 20)


def target_pct(clock):
    """Expected library occupancy (%) at a given clock time."""
    if not is_open(clock):
        return 0.0
    h = clock.hour + clock.minute / 60
    lo = int(h)
    hi_val = HOUR_PROFILE.get(lo + 1, HOUR_PROFILE.get(lo, 0.2) * 0.6)
    prof = HOUR_PROFILE.get(lo, 0.2) * (1 - (h - lo)) + hi_val * (h - lo)
    return 72 * prof * DAY_FACTOR[clock.weekday()] ** 0.5


def _step(L, demo):
    if demo:
        L["clock"] = L["clock"] + timedelta(minutes=10)
        if L["clock"].hour >= 20:
            L["clock"] = (L["clock"] + timedelta(days=1)).replace(hour=8, minute=0)
    else:
        L["clock"] = datetime.now(IST).replace(tzinfo=None)
    tgt = target_pct(L["clock"])
    rng = np.random.default_rng()
    events = []
    for z in ZONE_NAMES:
        seats = ZONE_SEATS[z]
        old = L["occ"][z]
        new = old + (tgt / 100 * ZONE_BIAS[z] * seats - old) * 0.4 + rng.normal(0, 0.03 * seats)
        new = float(np.clip(new, 0, seats))
        L["occ"][z] = new
        for _ in range(min(int(abs(new - old)), 2)):
            events.append({"Time": L["clock"].strftime("%H:%M"), "Student": f"{rng.choice(['MCA', 'BTC', 'MBA', 'BCA', 'BBA', 'MSC'])}-{rng.integers(1, 300):03d}",
                           "Zone": z, "Action": "IN" if new > old else "OUT"})
    L["feed"] = (events + L["feed"])[:10]
    total = sum(L["occ"].values()) / TOTAL_SEATS * 100
    L["history"].append({"t": L["clock"].strftime("%H:%M"), "pct": total})
    L["history"] = L["history"][-30:]
    L["tick"] += 1


def _init_live(demo):
    now = datetime.now(IST).replace(tzinfo=None)
    clock = now.replace(hour=9, minute=0, second=0, microsecond=0) if demo else now
    L = {"demo": demo, "clock": clock - timedelta(minutes=10), "bucket": None, "tick": 0, "feed": [], "history": [],
         "occ": {z: ZONE_SEATS[z] * 0.15 for z in ZONE_NAMES}}
    for _ in range(12 if demo else 1):
        _step(L, demo)
    return L


def get_live(live_on, refresh, demo):
    s = st.session_state
    if "live" not in s or s["live"]["demo"] != demo:
        s["live"] = _init_live(demo)
    L = s["live"]
    if live_on:
        bucket = int(time.time() // refresh)
        if L["bucket"] != bucket:
            if L["bucket"] is not None:
                _step(L, demo)
            L["bucket"] = bucket
    return L


# =============================================================================
# 5. CHARTS (matplotlib / seaborn / plotly)
# =============================================================================
def chart_hourly_line(ov, T):
    fig, ax = new_fig(T)
    if ov.empty:
        return fig, "No data for these filters."
    g = ov.assign(kind=np.where(ov["dow"] < 5, "Weekdays", "Weekends")).groupby(["kind", "hour"])["pct"].mean().reset_index()
    for i, (k, d) in enumerate(g.groupby("kind")):
        ax.plot(d["hour"], d["pct"], marker="o", ms=4, lw=2, color=PALETTE[i], label=k)
        ax.fill_between(d["hour"], d["pct"], alpha=0.12, color=PALETTE[i])
    ax.axhline(80, color=T["bad"], ls="--", lw=1)
    ax.text(OPEN_HOURS[-1], 82, "Busy (80%)", color=T["bad"], fontsize=7, ha="right")
    ax.set_xticks(OPEN_HOURS[::2])
    ax.set_xticklabels([hour_label(h) for h in OPEN_HOURS[::2]])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Seats occupied (%)")
    legend(ax, T, loc="upper left")
    by_hour = ov.groupby("hour")["pct"].mean()
    return fig, (f"On average the library is busiest at <b>{hour_label(int(by_hour.idxmax()))}</b> "
                 f"({by_hour.max():.0f}% full) and quietest at <b>{hour_label(int(by_hour.idxmin()))}</b> ({by_hour.min():.0f}%).")


def chart_area_visits(ent, T):
    fig, ax = new_fig(T)
    if ent.empty:
        return fig, "No data for these filters."
    p = ent.groupby(["date", "floor"]).size().unstack(fill_value=0)
    ax.stackplot(p.index, p.T.values, labels=p.columns, colors=PALETTE[:len(p.columns)], alpha=0.85)
    ax.set_ylabel("Visitors per day")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.tick_params(axis="x", rotation=30)
    legend(ax, T, loc="upper left", ncol=3)
    daily = p.sum(axis=1)
    exam = ent.groupby("date")["exam_week"].max()
    txt = f"Busiest day: <b>{daily.idxmax():%a %d %b}</b> with {daily.max():,} visits."
    if exam.any() and (~exam).any():
        lift = (daily[exam[exam].index.intersection(daily.index)].mean() / daily[exam[~exam].index.intersection(daily.index)].mean() - 1) * 100
        txt += f" Exam-week days see about <b>{lift:.0f}% more</b> visitors than regular days."
    return fig, txt


def chart_heatmap(ov, T):
    fig, ax = new_fig(T, 6.2, 3.4)
    if ov.empty:
        return fig, "No data for these filters."
    pv = ov.groupby(["dow", "hour"])["pct"].mean().unstack().reindex(range(7))
    pv.index = DAY_NAMES
    pv.columns = [hour_label(h) for h in pv.columns]
    cmap = LinearSegmentedColormap.from_list("lib", [T["cmap_lo"], T["cmap_hi"]])
    sns.heatmap(pv, ax=ax, cmap=cmap, annot=True, fmt=".0f", annot_kws={"size": 6.5}, linewidths=0.6,
                linecolor=T["card"], cbar_kws={"shrink": 0.8}, vmin=0, vmax=100)
    ax.grid(False)
    ax.tick_params(colors=T["muted"], labelsize=7.5, length=0)
    ax.set_xlabel("")
    ax.set_ylabel("")
    cb = ax.collections[0].colorbar
    cb.ax.tick_params(colors=T["muted"], labelsize=7)
    cb.outline.set_visible(False)
    stack = pv.stack()
    d, h = stack.idxmax()
    q = stack.idxmin()
    return fig, f"Most crowded slot: <b>{d} {h}</b> ({stack.max():.0f}% full). Best time to visit: <b>{q[0]} {q[1]}</b> ({stack.min():.0f}%)."


def chart_histogram(ent, T):
    fig, ax = new_fig(T)
    if ent.empty:
        return fig, "No data for these filters."
    ax.hist(ent["duration_min"], bins=20, color=PALETTE[0], edgecolor=T["card"], alpha=0.9)
    m, md = ent["duration_min"].mean(), ent["duration_min"].median()
    ax.axvline(m, color=PALETTE[2], ls="--", lw=1.6, label=f"Mean {m:.0f} min")
    ax.axvline(md, color=PALETTE[3], ls=":", lw=1.6, label=f"Median {md:.0f} min")
    ax.set_xlabel("Time spent in library (minutes)")
    ax.set_ylabel("Visits")
    legend(ax, T)
    return fig, f"Students stay about <b>{m:.0f} minutes</b> on average; <b>{(ent['duration_min'] > 120).mean() * 100:.0f}%</b> stay longer than 2 hours."


def chart_hbar_dept(ent, T):
    fig, ax = new_fig(T)
    if ent.empty:
        return fig, "No data for these filters."
    c = ent["department"].value_counts().sort_values()
    bars = ax.barh(c.index, c.values, color=PALETTE[1])
    ax.bar_label(bars, padding=3, fontsize=7.5, color=T["muted"], fmt="%d")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=T["border"], alpha=0.7)
    ax.set_xlabel("Number of visits")
    top = c.index[-1]
    return fig, f"<b>{top}</b> students visit most ({c.iloc[-1] / c.sum() * 100:.0f}% of all visits)."


def chart_pie_zone(ent, T):
    fig, ax = new_fig(T)
    if ent.empty:
        return fig, "No data for these filters."
    c = ent["zone"].value_counts()
    w, _, at = ax.pie(c.values, labels=None, autopct="%1.0f%%", startangle=90, colors=PALETTE[:len(c)],
                      wedgeprops=dict(edgecolor=T["card"], linewidth=2), pctdistance=0.78, textprops=dict(color="white", fontsize=8))
    ax.legend(w, c.index, loc="center left", bbox_to_anchor=(1, 0.5), frameon=False, labelcolor=T["text"], fontsize=8)
    ax.grid(False)
    return fig, f"<b>{c.index[0]}</b> is the most used zone ({c.iloc[0] / c.sum() * 100:.0f}% of visits); <b>{c.index[-1]}</b> is the least used."


def chart_bar_categories(bor, T):
    fig, ax = new_fig(T)
    if bor.empty:
        return fig, "No data for these filters."
    c = bor["category"].value_counts().head(8)
    bars = ax.bar(c.index, c.values, color=PALETTE[:len(c)])
    ax.bar_label(bars, padding=2, fontsize=7.5, color=T["muted"])
    ax.set_ylabel("Books borrowed")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return fig, f"<b>{c.index[0]}</b> books are in highest demand ({c.iloc[0]:,} borrowings), followed by <b>{c.index[1] if len(c) > 1 else '-'}</b>."


def chart_scatter_books(cat, bor, T):
    fig, ax = new_fig(T)
    s = cat[cat["ratings_count"] > 0].sample(min(1500, len(cat)), random_state=1)
    top = bor["category"].value_counts().head(4).index.tolist() if not bor.empty else []
    others = s[~s["category"].isin(top)]
    ax.scatter(others["ratings_count"], others["average_rating"], s=9, color=T["muted"], alpha=0.3, label="Other categories")
    for i, c in enumerate(top):
        d = s[s["category"] == c]
        ax.scatter(d["ratings_count"], d["average_rating"], s=12, color=PALETTE[i], alpha=0.75, label=c)
    ax.set_xscale("log")
    ax.set_xlabel("Number of ratings (log scale)")
    ax.set_ylabel("Average rating")
    ax.grid(axis="x", color=T["border"], alpha=0.5)
    legend(ax, T, loc="lower right", fontsize=7)
    r = np.corrcoef(np.log10(s["ratings_count"]), s["average_rating"])[0, 1]
    strength = "weak" if abs(r) < 0.3 else "moderate"
    return fig, f"Correlation between popularity and rating is <b>{strength} (r = {r:.2f})</b>: books with many ratings are not always rated higher."


def chart_box_fines(bor, T):
    fig, ax = new_fig(T)
    f = bor[bor["fine_inr"] > 0]
    if f.empty:
        return fig, "No fines for these filters."
    order = f.groupby("department")["fine_inr"].median().sort_values(ascending=False).index
    sns.boxplot(data=f, x="department", y="fine_inr", order=order, hue="department", hue_order=order, palette=PALETTE[:len(order)],
                legend=False, ax=ax, linewidth=1, fliersize=2, linecolor=T["muted"])
    ax.set_xlabel("")
    ax.set_ylabel("Fine (Rs)")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    top = f.groupby("department")["fine_inr"].median().idxmax()
    return fig, f"<b>{top}</b> has the highest median fine (Rs {f.groupby('department')['fine_inr'].median().max():.0f}); the largest single fine is <b>Rs {f['fine_inr'].max():.0f}</b>."


def chart_donut_status(bor, T):
    fig, ax = new_fig(T)
    if bor.empty:
        return fig, "No data for these filters."
    ret = bor["status"] == "Returned"
    parts = {
        "Returned on time": int((ret & (bor["late_days"] == 0)).sum()),
        "Returned late": int((ret & (bor["late_days"] > 0)).sum()),
        "Overdue": int((bor["status"] == "Overdue").sum()),
        "Still within due date": int((bor["status"] == "Borrowed").sum()),
    }
    cols = [T["good"], T["warn"], T["bad"], T["accent"]]
    w, _ = ax.pie(parts.values(), startangle=90, colors=cols, wedgeprops=dict(width=0.38, edgecolor=T["card"], linewidth=2))
    ax.text(0, 0, f"{sum(parts.values()):,}\nissues", ha="center", va="center", color=T["text"], fontsize=11, fontweight="bold")
    ax.legend(w, [f"{k} ({v})" for k, v in parts.items()], loc="center left", bbox_to_anchor=(1, 0.5), frameon=False,
              labelcolor=T["text"], fontsize=8)
    ax.grid(False)
    due_pool = parts["Returned on time"] + parts["Returned late"] + parts["Overdue"]
    return fig, f"<b>{(parts['Returned late'] + parts['Overdue']) / due_pool * 100:.0f}%</b> of books past their due date came back late or are still overdue."


def gauge(pct, T):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=pct, number={"suffix": "%", "font": {"size": 42, "color": T["text"]}},
        gauge={"axis": {"range": [0, 100], "tickcolor": T["muted"], "tickfont": {"color": T["muted"], "size": 10}},
               "bar": {"color": T["accent"], "thickness": 0.3}, "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
               "steps": [{"range": [0, 50], "color": "rgba(34,197,94,.28)"},
                         {"range": [50, 80], "color": "rgba(245,158,11,.28)"},
                         {"range": [80, 100], "color": "rgba(239,68,68,.30)"}]}))
    fig.update_layout(height=240, margin=dict(l=24, r=24, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)",
                      font={"color": T["text"]})
    return fig


def chart_live_zones(L, T):
    fig, ax = new_fig(T, 6.2, 3.0)
    seats = [ZONE_SEATS[z] for z in ZONE_NAMES]
    occ = [L["occ"][z] for z in ZONE_NAMES]
    y = np.arange(len(ZONE_NAMES))
    ax.barh(y, seats, color=T["border"], height=0.55, label="Capacity")
    bars = ax.barh(y, occ, color=PALETTE[1], height=0.55, label="Occupied")
    for yi, o, s in zip(y, occ, seats):
        ax.text(s + 2, yi, f"{o / s * 100:.0f}%", va="center", fontsize=8, color=T["text"])
    ax.set_yticks(y)
    ax.set_yticklabels([f"{z}" for z in ZONE_NAMES], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, max(seats) * 1.18)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Seats")
    legend(ax, T, loc="lower right")
    return fig


def chart_live_ticker(L, T):
    fig, ax = new_fig(T, 6.2, 3.0)
    h = pd.DataFrame(L["history"])
    ax.plot(h["t"], h["pct"], color=PALETTE[0], lw=2, marker="o", ms=3)
    ax.fill_between(h["t"], h["pct"], alpha=0.15, color=PALETTE[0])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Occupancy (%)")
    step = max(len(h) // 6, 1)
    ax.set_xticks(h["t"].iloc[::step])
    ax.tick_params(axis="x", rotation=0)
    return fig


# =============================================================================
# 6. PREDICTOR (scikit-learn Random Forest)
# =============================================================================
@st.cache_resource(show_spinner="Training the busy-hour model...")
def train_model():
    d = OCC.copy()
    d["zone_code"] = d["zone"].map({z: i for i, z in enumerate(ZONE_NAMES)})
    X, y = d[["hour", "dow", "zone_code"]], d["occupancy_pct"]
    cutoff = d["date"].sort_values().iloc[int(len(d) * 0.8)]
    tr, te = d["date"] < cutoff, d["date"] >= cutoff
    model = RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1).fit(X[tr], y[tr])
    pred = model.predict(X[te])
    return model, {"mae": mean_absolute_error(y[te], pred), "r2": r2_score(y[te], pred),
                   "importance": dict(zip(["Hour", "Day of week", "Zone"], model.feature_importances_)),
                   "y_test": y[te].to_numpy(), "y_pred": pred, "n_train": int(tr.sum()), "n_test": int(te.sum())}


def predict_day(model, dow, zones):
    hours = SUNDAY_HOURS if dow == 6 else OPEN_HOURS
    rows = [(h, dow, ZONE_NAMES.index(z)) for h in hours for z in zones]
    p = model.predict(pd.DataFrame(rows, columns=["hour", "dow", "zone_code"]))
    df = pd.DataFrame(rows, columns=["hour", "dow", "zc"])
    df["pct"] = p
    df["seats"] = df["zc"].map(lambda i: ZONE_SEATS[ZONE_NAMES[i]])
    out = df.groupby("hour").apply(lambda g: np.average(g["pct"], weights=g["seats"]), include_groups=False).reset_index()
    out.columns = ["hour", "pct"]
    return out


def chart_prediction(pr, T, day):
    fig, ax = new_fig(T, 6.4, 3.3)
    ax.plot(pr["hour"], pr["pct"], color=PALETTE[0], lw=2.2, marker="o")
    ax.fill_between(pr["hour"], pr["pct"], alpha=0.15, color=PALETTE[0])
    best = pr.nsmallest(3, "pct")
    ax.scatter(best["hour"], best["pct"], s=110, color=T["good"], zorder=5, label="Best 3 hours")
    ax.axhspan(0, 45, color=T["good"], alpha=0.06)
    ax.axhspan(75, 100, color=T["bad"], alpha=0.06)
    ax.set_ylim(0, 100)
    ax.set_xticks(pr["hour"])
    ax.set_xticklabels([hour_label(h) for h in pr["hour"]], fontsize=7.5)
    ax.set_ylabel("Predicted occupancy (%)")
    legend(ax, T, loc="upper left")
    return fig


def chart_importance(info, T):
    fig, ax = new_fig(T, 4, 2.8)
    items = sorted(info["importance"].items(), key=lambda kv: kv[1])
    bars = ax.barh([k for k, _ in items], [v * 100 for _, v in items], color=PALETTE[2])
    ax.bar_label(bars, fmt="%.0f%%", padding=3, fontsize=8, color=T["muted"])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Importance (%)")
    ax.set_xlim(0, 105)
    return fig


def chart_actual_vs_pred(info, T):
    fig, ax = new_fig(T, 4, 2.8)
    ax.scatter(info["y_test"], info["y_pred"], s=10, color=PALETTE[0], alpha=0.5)
    ax.plot([0, 100], [0, 100], color=T["bad"], ls="--", lw=1.2)
    ax.set_xlabel("Actual (%)")
    ax.set_ylabel("Predicted (%)")
    ax.grid(axis="x", color=T["border"], alpha=0.5)
    return fig


# =============================================================================
# 7. SIDEBAR + THEME
# =============================================================================
with st.sidebar:
    st.markdown('<div class="brand">📚 LibraSmart<br><span>CHRIST (Deemed to be University)</span></div>', unsafe_allow_html=True)
    dark = st.toggle("Dark mode", key="dark")
    st.divider()
    st.markdown("**Filters**")
    sel_depts = st.multiselect("Department", list(DEPARTMENTS), placeholder="All departments")
    sel_zones = st.multiselect("Floor / zone", ZONE_NAMES, placeholder="All zones",
                               format_func=lambda z: f"{z} ({ZONE_FLOOR[z]})")
    dmin, dmax = ENT["date"].min().date(), ENT["date"].max().date()
    dr = st.date_input("Date range", value=(dmin, dmax), min_value=dmin, max_value=dmax)
    sel_cats = st.multiselect("Book category", sorted(BOR["category"].unique()), placeholder="All categories")
    st.divider()
    st.markdown("**Live mode**")
    live_on = st.toggle("Live updates", value=True)
    refresh = st.select_slider("Refresh every (seconds)", options=[3, 5, 10, 15, 30, 60], value=5)
    clock_mode = st.radio("Live clock", ["Demo clock", "Real clock"], horizontal=True,
                          help="Demo clock replays a library day so the live view is always active. Real clock follows IST.")
    demo = clock_mode == "Demo clock"

T = THEMES["dark" if dark else "light"]
inject_css(T)

# ---- apply filters
d0, d1 = (pd.Timestamp(dr[0]), pd.Timestamp(dr[1])) if isinstance(dr, (tuple, list)) and len(dr) == 2 else (pd.Timestamp(dmin), pd.Timestamp(dmax))
depts = sel_depts or list(DEPARTMENTS)
zones = sel_zones or ZONE_NAMES
cats = sel_cats or sorted(BOR["category"].unique())

in_range = lambda df, a, b: (df["date"] >= a) & (df["date"] <= b)
ent_f = ENT[in_range(ENT, d0, d1) & ENT["department"].isin(depts) & ENT["zone"].isin(zones)]
occ_f = OCC[in_range(OCC, d0, d1) & OCC["zone"].isin(zones)]
bor_f = BOR[in_range(BOR, d0, d1) & BOR["department"].isin(depts) & BOR["category"].isin(cats)]
ov = overall(occ_f)

span = (d1 - d0).days + 1
p0, p1 = d0 - pd.Timedelta(days=span), d0 - pd.Timedelta(days=1)
ent_prev = ENT[in_range(ENT, p0, p1) & ENT["department"].isin(depts) & ENT["zone"].isin(zones)]
bor_prev = BOR[in_range(BOR, p0, p1) & BOR["department"].isin(depts) & BOR["category"].isin(cats)]

with st.sidebar:
    st.divider()
    st.markdown("**Export**")
    stretch(st.download_button, "Download visits (CSV)", ent_f.drop(columns=["date", "hour", "dow"]).to_csv(index=False).encode(),
            "librasmart_visits.csv", "text/csv")
    stretch(st.download_button, "Download borrowing (CSV)", bor_f.drop(columns=["date"]).to_csv(index=False).encode(),
            "librasmart_borrowing.csv", "text/csv")
    st.caption("Department and category filters apply to visits and borrowing. Occupancy charts follow the zone and date filters.")

# =============================================================================
# 8. HEADER
# =============================================================================
L0 = get_live(live_on, refresh, demo)
st.markdown(
    f'<div class="hero"><div><div class="hero-title">CHRIST LibraSmart</div>'
    f'<div class="hero-sub">Library seat occupancy and book demand analytics Dashboard</div></div>'
    f'<div class="live-pill"><span class="dot {"" if live_on else "off"}"></span>'
    f'{"Live" if live_on else "Paused"} &middot; {"demo clock" if demo else "IST"}</div></div>',
    unsafe_allow_html=True)

# =============================================================================
# 9. KPI METRIC CARDS
# =============================================================================
usual = OCC.groupby(["dow", "hour", "date"])[["occupied", "capacity"]].sum().reset_index()
usual["pct"] = usual["occupied"] / usual["capacity"] * 100
usual = usual.groupby(["dow", "hour"])["pct"].mean()


def kpi_panel():
    L = get_live(live_on, refresh, demo)
    seats_used = sum(L["occ"].values())
    live_pct = seats_used / TOTAL_SEATS * 100
    usual_now = usual.get((L["clock"].weekday(), L["clock"].hour), np.nan)
    by_hour = ov.groupby("hour")["pct"].mean() if not ov.empty else pd.Series(dtype=float)
    peak_h = int(by_hour.idxmax()) if len(by_hour) else None
    overdue_now = bor_f[bor_f["status"] == "Overdue"]
    cols = st.columns(6)
    cards = [
        kpi("🪑", "Live occupancy", f"{live_pct:.0f}%", " vs usual for this hour", None if np.isnan(usual_now) else live_pct - usual_now, good_up=False),
        kpi("✅", "Seats free", f"{int(TOTAL_SEATS - seats_used)}", f"of {TOTAL_SEATS} seats"),
        kpi("⏰", "Peak hour", hour_label(peak_h) if peak_h is not None else "-",
            f"{by_hour.max():.0f}% avg occupancy" if peak_h is not None else ""),
        kpi("👥", "Total visitors", f"{len(ent_f):,}", " vs previous period", pct_change(len(ent_f), len(ent_prev))),
        kpi("📚", "Books borrowed", f"{len(bor_f):,}", " vs previous period", pct_change(len(bor_f), len(bor_prev))),
        kpi("⚠️", "Overdue books", f"{len(overdue_now):,}", f"Rs {int(overdue_now['fine_inr'].sum()):,} fines pending"),
    ]
    for c, h in zip(cols, cards):
        c.markdown(h, unsafe_allow_html=True)


stretch_frag = st.fragment(run_every=(refresh if live_on else None))(kpi_panel)
stretch_frag()
st.write("")

# =============================================================================
# 10. TABS
# =============================================================================
tab_live, tab_trends, tab_books, tab_predict = st.tabs(["Live", "Trends", "Books", "Predict"])

# ------------------------------------------------------------------ LIVE
with tab_live:
    def live_panel():
        L = get_live(live_on, refresh, demo)
        pct = sum(L["occ"].values()) / TOTAL_SEATS * 100
        mood = ("Quiet: plenty of seats" if pct < 50 else "Moderate: seats are filling up" if pct < 80 else "Busy: very few seats left")
        if not is_open(L["clock"]):
            mood = "Library is closed at this time"
        c1, c2 = st.columns([1, 1.5])
        with c1:
            with card("Live seat occupancy", f"{L['clock']:%a %I:%M %p} ({'demo clock' if demo else 'IST'}) &middot; Plotly gauge"):
                stretch(st.plotly_chart, gauge(pct, T), key="live_gauge", config={"displayModeBar": False})
                insight(mood)
        with c2:
            with card("Occupancy by zone", "Seats in use right now vs capacity &middot; Matplotlib"):
                show(chart_live_zones(L, T))
        c3, c4 = st.columns([1.5, 1])
        with c3:
            with card("Live occupancy ticker", "Library-wide occupancy over the last readings &middot; Matplotlib line chart"):
                show(chart_live_ticker(L, T))
        with c4:
            with card("Entry and exit feed", "Latest simulated swipes"):
                feed = pd.DataFrame(L["feed"][:7])
                st.markdown(html_table(feed, badge_col="Action", empty="Waiting for the first swipes..."), unsafe_allow_html=True)

    st.fragment(run_every=(refresh if live_on else None))(live_panel)()

# ------------------------------------------------------------------ TRENDS
with tab_trends:
    a, b = st.columns(2)
    with a:
        with card("Hourly occupancy trend", "Average seats occupied through the day &middot; Line chart"):
            fig, txt = chart_hourly_line(ov, T)
            show(fig)
            insight(txt)
    with b:
        with card("Visitor trend by floor", "Daily visitors stacked by floor &middot; Area chart"):
            fig, txt = chart_area_visits(ent_f, T)
            show(fig)
            insight(txt)
    a, b = st.columns(2)
    with a:
        with card("Crowd heatmap", "Occupancy by day and hour &middot; Seaborn heatmap"):
            fig, txt = chart_heatmap(ov, T)
            show(fig)
            insight(txt)
    with b:
        with card("How long students stay", "Time spent per visit &middot; Histogram"):
            fig, txt = chart_histogram(ent_f, T)
            show(fig)
            insight(txt)
    a, b = st.columns(2)
    with a:
        with card("Visits by department", "Who uses the library most &middot; Horizontal bar chart"):
            fig, txt = chart_hbar_dept(ent_f, T)
            show(fig)
            insight(txt)
    with b:
        with card("Zone usage share", "Where students sit &middot; Pie chart"):
            fig, txt = chart_pie_zone(ent_f, T)
            show(fig)
            insight(txt)

# ------------------------------------------------------------------ BOOKS
with tab_books:
    a, b = st.columns(2)
    with a:
        with card("Most borrowed categories", "Book demand by subject &middot; Bar chart"):
            fig, txt = chart_bar_categories(bor_f, T)
            show(fig)
            insight(txt)
    with b:
        with card("Rating vs popularity", f"Real book catalogue ({META['catalogue_source']}) &middot; Scatter plot"):
            fig, txt = chart_scatter_books(CAT, bor_f, T)
            show(fig)
            insight(txt)
    a, b = st.columns(2)
    with a:
        with card("Fine analysis by department", "Spread of late fines (Rs) &middot; Seaborn box plot"):
            fig, txt = chart_box_fines(bor_f, T)
            show(fig)
            insight(txt)
    with b:
        with card("Return status", "On time, late and overdue books &middot; Donut chart"):
            fig, txt = chart_donut_status(bor_f, T)
            show(fig)
            insight(txt)
    a, b = st.columns(2)
    with a:
        with card("Top 8 borrowed books", "Most issued titles in the selected period"):
            if bor_f.empty:
                st.markdown(html_table(pd.DataFrame()), unsafe_allow_html=True)
            else:
                top = (bor_f.groupby(["title", "author", "category"]).size().reset_index(name="Times borrowed")
                       .sort_values("Times borrowed", ascending=False).head(8))
                top = top.merge(CAT[["title", "average_rating"]].drop_duplicates("title"), on="title", how="left")
                top = top.rename(columns={"title": "Title", "author": "Author", "category": "Category", "average_rating": "Rating"})
                top["Title"] = top["Title"].str.slice(0, 38)
                st.markdown(html_table(top[["Title", "Author", "Category", "Times borrowed", "Rating"]]), unsafe_allow_html=True)
    with b:
        with card("Overdue watchlist", "Highest pending fines (Rs 2 per late day)"):
            od = bor_f[bor_f["status"] == "Overdue"].sort_values("fine_inr", ascending=False).head(8)
            od = od.assign(due=od["due_date"].dt.strftime("%d %b"))[["student_id", "department", "title", "due", "late_days", "fine_inr"]]
            od["title"] = od["title"].str.slice(0, 30)
            od.columns = ["Student", "Dept", "Book", "Due", "Days late", "Fine (Rs)"]
            st.markdown(html_table(od, empty="No overdue books for these filters."), unsafe_allow_html=True)

# ------------------------------------------------------------------ PREDICT
with tab_predict:
    model, info = train_model()
    sc1, sc2, sc3 = st.columns([1, 1.4, 2])
    tomorrow = (datetime.now(IST).weekday() + 1) % 7
    day = sc1.selectbox("Day of the week", range(7), index=tomorrow, format_func=lambda i: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][i])
    pz = sc2.multiselect("Zone", ZONE_NAMES, default=[], placeholder="All zones", key="pred_zone")
    pr = predict_day(model, day, pz or ZONE_NAMES)
    best = pr.nsmallest(3, "pct").sort_values("hour")
    busiest = pr.loc[pr["pct"].idxmax()]
    quiet = pr.loc[pr["pct"].idxmin()]
    label = lambda v: "Quiet" if v < 45 else "Moderate" if v < 75 else "Busy"
    k1, k2, k3 = st.columns(3)
    k1.markdown(kpi("🟢", "Best time to visit", hour_label(int(quiet["hour"])), f"{quiet['pct']:.0f}% full ({label(quiet['pct'])})"), unsafe_allow_html=True)
    k2.markdown(kpi("🔴", "Busiest hour", hour_label(int(busiest["hour"])), f"{busiest['pct']:.0f}% full ({label(busiest['pct'])})"), unsafe_allow_html=True)
    k3.markdown(kpi("🎯", "Model accuracy", f"{info['r2'] * 100:.0f}%", f"R² score &middot; MAE {info['mae']:.1f} points"), unsafe_allow_html=True)
    st.write("")
    a, b = st.columns([1.6, 1])
    with a:
        with card("Busy-hour predictor", "Random Forest forecast of seat occupancy by hour &middot; Matplotlib"):
            show(chart_prediction(pr, T, day))
            slots = ", ".join(f"<b>{hour_label(int(h))}</b> ({p:.0f}%)" for h, p in zip(best["hour"], best["pct"]))
            insight(f"Plan your visit around {slots}. Slots under 45% usually have plenty of free seats.")
    with b:
        with card("What drives the prediction", "Feature importance &middot; Bar chart"):
            show(chart_importance(info, T))
        with card("Predicted vs actual", f"Test data ({info['n_test']:,} rows) &middot; Scatter plot"):
            show(chart_actual_vs_pred(info, T))
    st.caption(f"Model: RandomForestRegressor trained on {info['n_train']:,} hourly records (hour, day of week, zone) and tested on the latest 20% of days.")

# =============================================================================
# 11. DATA TABLE
# =============================================================================
st.write("")
with card("Data explorer", "Search the records behind the charts"):
    t1, t2, t3 = st.columns([1.2, 2, 1])
    which = t1.selectbox("Dataset", ["Borrowing records", "Library visits"])
    q = t2.text_input("Search", placeholder="Student ID, title, department, zone...")
    nrows = t3.select_slider("Rows", options=[10, 25, 50, 100], value=10)
    if which == "Borrowing records":
        tb = bor_f.assign(Borrowed=bor_f["borrow_date"].dt.strftime("%d %b %Y"), Due=bor_f["due_date"].dt.strftime("%d %b %Y"))
        tb = tb.rename(columns={"student_id": "Student", "department": "Dept", "title": "Title", "category": "Category",
                                "status": "Status", "fine_inr": "Fine (Rs)"})[["Student", "Dept", "Title", "Category", "Borrowed", "Due", "Status", "Fine (Rs)"]]
        badge = "Status"
    else:
        tb = ent_f.assign(Entry=ent_f["entry_time"].dt.strftime("%d %b %H:%M"), Exit=ent_f["exit_time"].dt.strftime("%H:%M"))
        tb = tb.rename(columns={"student_id": "Student", "department": "Dept", "floor": "Floor", "zone": "Zone",
                                "duration_min": "Minutes"})[["Student", "Dept", "Floor", "Zone", "Entry", "Exit", "Minutes"]]
        badge = None
    if q:
        mask = tb.astype(str).apply(lambda col: col.str.contains(q, case=False, regex=False)).any(axis=1)
        tb = tb[mask]
    tb = tb.copy()
    if "Title" in tb.columns:
        tb["Title"] = tb["Title"].str.slice(0, 40)
    st.markdown(html_table(tb.head(nrows), badge_col=badge), unsafe_allow_html=True)
    st.caption(f"Showing {min(nrows, len(tb))} of {len(tb):,} records.")

st.markdown(
    f'<div class="foot">Book catalogue: {html.escape(META["catalogue_source"])} &middot; Library entries, occupancy, borrowing and fines are simulated '
    f'(the library does not publish live data) &middot; Built with Streamlit, Pandas, NumPy, Matplotlib, Seaborn, Plotly and scikit-learn</div>',
    unsafe_allow_html=True)
