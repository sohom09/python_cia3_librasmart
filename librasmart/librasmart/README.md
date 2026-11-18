# CHRIST LibraSmart: Library Seat Occupancy & Book Demand Analytics Dashboard

MCA411-2 Python Programming | Component 3 (Assignment) | CHRIST (Deemed to be University)

An interactive Streamlit dashboard that shows live seat occupancy by floor and zone, peak-hour crowding,
most borrowed book categories, overdue returns and fine analysis, and a busy-hour predictor that tells
students the best time to visit the library.

**Live app:** https://your-app-name.streamlit.app
**Course:** MCA411-2 Python Programming, Component 3 (Assignment)
**Student:** Sohom Chakraborty | Reg No: 2647250 | 2 MCA-B

![Dashboard screenshot](screenshot.jpg)

## Features
- **KPI metric cards:** live occupancy, seats free, peak hour, total visitors, books borrowed, overdue books (with change vs previous period)
- **Live mode:** auto-refreshing gauge, zone occupancy, ticker and entry/exit feed (demo clock or real IST clock)
- **10 chart types:** line, area, heatmap, histogram, horizontal bar, pie, bar, scatter, box plot, donut (+ gauge, ticker and predictor charts)
- **Insight caption** under every chart, generated from the filtered data
- **Busy-hour predictor:** Random Forest model (scikit-learn) with accuracy, feature importance and predicted-vs-actual chart
- **Sidebar filters:** department, floor/zone, date range, book category; CSV export of filtered data
- **Light and dark mode** switch
- **Data explorer** with search and status badges

## Tech stack
Streamlit, Pandas, NumPy, Matplotlib, Seaborn, Plotly, scikit-learn

## Data
| File | Type | Description |
|---|---|---|
| `data/catalogue.csv` | Real | Book catalogue from the Kaggle dataset [7k Books with Metadata](https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata) |
| `data/library_entries.csv` | Simulated | Every library entry and exit (student, department, zone, times) |
| `data/occupancy_hourly.csv` | Simulated | Seats occupied per zone per hour (computed from entries) |
| `data/book_borrowing.csv` | Simulated | Issues, returns, late days and fines, linked to real books in the catalogue |
| `data/seat_capacity.csv` | Config | Floors, zones and seat counts |

The library does not publish live data, so entries, occupancy and borrowing are simulated with realistic patterns
(afternoon peaks, quiet weekends, one exam week, department-specific reading habits). The app reads plain CSV files,
so real data with the same columns can be dropped in without changing the code.

## Libraries used

| Library | Used for |
|---|---|
| Streamlit | Web app, layout, widgets, live refresh |
| Pandas | Loading, filtering, grouping and merging data |
| NumPy | Random simulation and numerical calculations |
| Matplotlib | Line, area, histogram, bar, pie, donut and scatter charts |
| Seaborn | Crowd heatmap and fine box plot |
| Plotly | Interactive live occupancy gauge |
| scikit-learn | Random Forest predictor and model scores |

## Data

| File | Type | Description |
|---|---|---|
| `data/catalogue.csv` | Real | 587 books from the Kaggle dataset [7k Books with Metadata](https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata) |
| `data/book_borrowing.csv` | Simulated | 1,289 borrowing records, 23 columns, linked to the real books |
| `data/library_entries.csv` | Simulated | 1,500-row sample of the full visit log |
| `data/occupancy_hourly.csv` | Simulated | Seats occupied per zone per hour, calculated from the full visit log |
| `data/seat_capacity.csv` | Config | Floors, zones and seats (320 seats in total) |
| `data/kaggle_books.csv` | Real (original) | The full Kaggle file, used to rebuild the catalogue |

The library does not publish live entry or borrowing data, so those files are simulated with realistic patterns: quieter mornings, a busy afternoon, low weekends, an exam week and department-specific subject choices. The app reads plain CSV files, so real data with the same columns can replace them without code changes.


## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Rebuild the dataset (optional)
Download `books.csv` from the Kaggle link above, save it as `data/kaggle_books.csv`, then run:
```bash
python generate_data.py
```

## Deploy
Push the folder to GitHub, then create a new app on [Streamlit Community Cloud](https://share.streamlit.io) with `app.py` as the main file.

## Project structure

```
librasmart/
├── app.py              Streamlit dashboard
├── common.py           Shared settings (zones, departments, hourly pattern)
├── generate_data.py    Builds the datasets
├── data/               CSV files and dataset facts (meta.json)
├── .streamlit/
│   └── config.toml     Theme settings
├── requirements.txt
├── README.md
├── SUBMISSION_GUIDE.md
└── VIVA_GUIDE.md
```

## Run locally

```bash
git clone https://github.com/<your-username>/librasmart.git
cd librasmart
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501 in your browser.

## Rebuild the data (optional)

The CSV files are already included. To regenerate them, run:

```bash
python generate_data.py
```

## Deploy

The app is deployed on Streamlit Community Cloud. Repository: this repo, branch `main`, main file `app.py`.

## Source

- Book catalogue: Kaggle, "7k Books with Metadata" by dylanjcastillo (https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata)
- Library activity: simulated for this assignment

## Future scope

- Connect to real card-swipe and library-system data
- Seat booking and mobile alerts when a seat frees up
- Staff login with admin views

## Author

Sohom Chakraborty, MCA, CHRIST (Deemed to be University), Bengaluru