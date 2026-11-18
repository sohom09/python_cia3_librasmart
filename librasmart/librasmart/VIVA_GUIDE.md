# LibraSmart: Viva Guide (MCA411-2, Component 3)

Use this guide to explain the project, the dataset and the code. Read it once the night before, and practise the demo twice with the app open.

---

## 1. Two-minute opening (say this first)

"My project is **CHRIST LibraSmart**, an interactive Streamlit dashboard for the CHRIST University library. It answers three questions for students: how full is the library right now, when is the best time to visit, and which books and subjects are in demand. It uses real book data from a Kaggle dataset and simulated library activity, because the library does not publish live data. The app has KPI cards, ten matplotlib chart types, a Random Forest predictor, live mode, filters, CSV export and a light and dark theme."

---

## 2. Rubric and how the project meets it

| Rubric | Marks | What to show and say |
|---|---|---|
| Topic selection | 5 | The topic is CHRIST-specific and unique. It was entered in the sheet before 15 Nov. Name the real problem: students do not know when the library is crowded. |
| Implementation | 10 | Show the multi-tab app, the 10 chart types, the KPI cards, the filters, the predictor, the dark mode and the CSV download. Explain the code structure. |
| Innovative idea / real-time | 5 | Show Live mode (the gauge and zone bars update every few seconds), the busy-hour predictor, and the real Kaggle catalogue. |
| Concept clarity (viva) | 5 | Explain the dataset, each library, each chart, the predictor and the design choices (use this guide). |

---

## 3. Project files (what each file is)

| File | Purpose |
|---|---|
| `app.py` | The Streamlit dashboard: layout, KPI cards, tabs, charts, predictor, live mode, theme |
| `common.py` | Shared settings: zones and seats, departments, hour profile, loan period, fine rate |
| `generate_data.py` | Builds all datasets: cleans the Kaggle file and simulates library activity |
| `data/kaggle_books.csv` | The original Kaggle file (6,810 rows), kept so the data can be rebuilt |
| `data/*.csv` | The cleaned and simulated datasets used by the app |
| `data/meta.json` | Facts about the dataset: source, date generated, counts, exam week |
| `requirements.txt` | Libraries Streamlit Cloud installs |
| `.streamlit/config.toml` | App settings (theme colour and usage statistics off) |
| `README.md` | Project description and run instructions |
| `SUBMISSION_GUIDE.md` | GitHub and deployment steps |

---

## 4. The dataset (explain this clearly)

### 4.1 Where the data comes from
- **Real:** the book catalogue comes from the Kaggle dataset **"7k Books with Metadata"** by dylanjcastillo (https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata). The original file has **6,810 books and 12 columns**.
- **Simulated:** library visits, seat occupancy, borrowing, returns and fines. The library does not publish this data, so I generated it with realistic patterns.

### 4.2 Why I shrank the dataset
The original file was 4 MB and the first simulated tables had over 26,000 rows. Shorter tables are easier to read, quicker to load and easier to check. The app now uses about 3,400 rows in total, and every table is small enough to open in Excel.

### 4.3 The files the app uses

**`book_borrowing.csv`: main table, 1,289 rows, 23 columns**

| Column | Meaning |
|---|---|
| txn_id | Unique ID for each borrowing |
| student_id | Anonymous student code, such as BTC-123 (department code and number) |
| department | Student's department (MCA, BTech CSE, MBA, MSc, BCom, BCA, BBA, BA English) |
| year_of_study | Year of study, 1 to 3 |
| book_id | ID of the book in the catalogue |
| isbn13 | ISBN-13 of the book (from Kaggle) |
| title | Book title (from Kaggle) |
| author | Main author (from Kaggle) |
| category | Subject category, such as Computers, Science, Business & Economics (from Kaggle) |
| published_year | Year the book was published (from Kaggle) |
| average_rating | Average rating from readers, 0 to 5 (from Kaggle) |
| num_pages | Number of pages (from Kaggle) |
| ratings_count | Number of ratings the book has received (from Kaggle) |
| borrow_date | Date and time the book was issued |
| borrow_month | Month of issue, such as "Nov 2026" |
| borrow_weekday | Day of issue, such as "Mon" |
| exam_week | True if the book was borrowed during the exam week |
| due_date | Borrow date plus 14 days |
| loan_days | Loan period (14 days) |
| return_date | Date returned, empty if still not returned |
| status | Returned, Borrowed (still within the due date) or Overdue |
| late_days | Days past the due date |
| fine_inr | Fine in rupees: Rs 2 per late day |

**`library_entries.csv`: visit log sample, 1,500 rows, 9 columns**
entry_id, student_id, department, floor, zone, entry_time, exit_time, duration_min, exam_week.
This is a random sample of the full simulated visit log of **25,884 visits**. The sample keeps the file small. The occupancy file below was computed from the full log, so the occupancy numbers are based on all visits.

**`occupancy_hourly.csv`: 1,950 rows, 6 columns**
timestamp, floor, zone, occupied (average number of students in that zone in that hour), capacity (seats in that zone), occupancy_pct. This feeds the line chart, heatmap, live baseline and predictor.

**`catalogue.csv`: 587 books, 9 columns**
book_id, title, authors, published_year, average_rating, num_pages, ratings_count, isbn13, category. It is all 372 academic books from the Kaggle file, plus a random 215 others, so the catalogue is about 600 books instead of 6,800.

**`seat_capacity.csv`: 5 rows, 3 columns**
floor, zone, seats. Total library capacity is **320 seats** across five zones: Reading Hall (100), Digital Library (50), Silent Zone (70), Group Study (40) and Computer Lab (60).

### 4.4 How the simulation works (know this)
1. **Visit arrivals:** students arrive per hour with a daily pattern. Quiet mornings, a 3 to 4 PM peak, and fewer visits on Saturdays and almost none on Sundays (open 10 AM to 4 PM).
2. **Zones:** each department prefers certain zones. Computer Lab is used more by MCA, BTech and BCA. Group Study is used more by MBA, BBA and BCom. BA English prefers the Silent Zone and Reading Hall.
3. **Stay length:** a log-normal distribution (median about 91 minutes), capped at the closing time.
4. **Exam week:** one week (5 to 11 Nov) has about 45% more visits and about 25% more borrowing.
5. **Borrowing:** each department picks subjects by taste. Computers for MCA, BTech and BCA. Business for MBA, BBA and BCom. Science for MSc. Fiction and literary books for BA English. Popular books are more likely to be picked.
6. **Returns and fines:** about 60% return on time, some return early, some are late, and some are still overdue. A late book pays Rs 2 per late day.

### 4.5 Key numbers (memorise these)
- Period covered: the last **35 days** (about 15 Oct to 18 Nov 2026)
- Visits simulated: **25,884** (1,500 in the file)
- Books borrowed: **1,289**, of which 824 returned, 280 still within due date and 185 overdue
- Total fines: **Rs 4,312**, largest single fine Rs 40
- Average library occupancy: **34%**; peak about 88% in exam week
- Most borrowed subject: Business & Economics (263 borrowings), then Science (182) and Computers (173)
- Busiest department by borrowing: BTech CSE (291), then MCA (253)

### 4.6 Good answers for dataset questions
- **Is the data real?** The book catalogue is real (Kaggle). The library activity is simulated, because the library does not publish it. The app reads plain CSV files, so real data with the same columns can be dropped in and the code will not change.
- **Why not use a real library dataset?** None is public for CHRIST, and the assignment allows any dataset for convenience.
- **Why is the data small?** The assignment asks for a clear, understandable dataset. Small tables make the charts easy to read and explain, and they load fast on Streamlit Cloud.
- **Why sample the visit log?** The full log has 25,884 visits. I keep a 1,500-row sample for the file and compute the occupancy from the full log, so the numbers are still accurate.
- **How do you handle missing values?** In the Kaggle data, missing ratings, page counts and years are filled with the column median, and books without a title are dropped. Duplicate titles are removed.
- **Why 23 columns in borrowing?** It combines the student, the book details, the dates and the fines in one table, so each chart can be filtered on any of them.

---

## 5. Code walkthrough (say this in your own words)

### 5.1 `generate_data.py` (run once, before the app)
- `load_catalogue()`: reads the Kaggle file, renames columns, fills missing values with medians, splits multi-value categories and keeps the first one.
- `prepare_catalogue()`: keeps all academic books and a random 215 others, adds a `book_id`, and saves `catalogue.csv`.
- `generate_entries()`: simulates visits hour by hour with a Poisson random count (each hour's number of visits is a random draw whose average follows the hourly pattern).
- `hourly_occupancy()`: works out how many students were in each zone in each hour by measuring the overlap of each visit with each hour.
- `book_probs()` and `generate_borrowing()`: pick a subject first using department taste, then a book inside that subject weighted by popularity. Then they create issue, due and return dates, status and fines.
- `main()`: runs everything and saves the files and `meta.json`.

### 5.2 `app.py` (the dashboard, in order)
1. **Themes and CSS:** two colour themes (light and dark) are stored as variables. `inject_css()` writes them into the page, so the whole app switches colour without reloading.
2. **Data loading:** `load_data()` reads the CSV files. It is decorated with `@st.cache_data`, so the files are read once, not on every click.
3. **Helpers:** `card()` draws a white or dark rounded box around a chart, `kpi()` builds a metric card with a change arrow, `html_table()` builds a table with coloured status badges, `new_fig()` styles every matplotlib chart for the current theme, and `show()` displays and closes a figure.
4. **Live simulation:** `target_pct()` gives the expected occupancy for the current time from the hourly pattern. `_step()` moves each zone's occupancy towards that target with a small random change and adds entry and exit events to the feed. `get_live()` runs one step every refresh interval. A demo clock replays a library day, so live mode always shows movement.
5. **Charts:** one function per chart (`chart_hourly_line`, `chart_area_visits`, `chart_heatmap`, `chart_histogram`, `chart_hbar_dept`, `chart_pie_zone`, `chart_bar_categories`, `chart_scatter_books`, `chart_box_fines`, `chart_donut_status`). Each returns a figure and a one-sentence insight that is computed from the data, so the caption changes when the filters change.
6. **Predictor:** `train_model()` trains a Random Forest on hour, day of week and zone. It uses the first 80% of days for training and the last 20% for testing. `predict_day()` forecasts a whole day and `chart_prediction()` plots it with the three best hours highlighted.
7. **Sidebar:** dark mode switch, filters (department, zone, date range, category), live mode, refresh interval, live clock choice, and CSV download buttons.
8. **Layout:** header, six KPI cards (in a fragment that refreshes), then four tabs (Live, Trends, Books, Predict), then the data explorer with search.

### 5.3 Streamlit ideas to explain
- **Script reruns:** Streamlit reruns the whole script when a widget changes. `@st.cache_data` and `@st.cache_resource` stop the data and the model from being reloaded every time.
- **`st.fragment(run_every=...)`:** only the marked part (the KPI cards and live panel) reruns on a timer, so the rest of the page stays still.
- **`st.session_state`:** keeps the live simulation running between reruns.
- **`st.toggle`, `st.multiselect`, `st.date_input`, `st.select_slider`:** the filter widgets.
- **`st.download_button`:** exports the filtered data as CSV.

---

## 6. Chart guide (one line per chart: what it shows and why it is used)

| # | Chart (type) | Library | Where | What it shows | Caption insight |
|---|---|---|---|---|---|
| 1 | Line chart | Matplotlib | Trends | Average occupancy through the day, weekdays vs weekends | Busiest and quietest hours |
| 2 | Area chart | Matplotlib | Trends | Daily visitors stacked by floor | Busiest day and exam-week increase |
| 3 | Heatmap | Seaborn | Trends | Occupancy by day of week and hour | Most and least crowded slots |
| 4 | Histogram | Matplotlib | Trends | How long students stay (minutes) | Mean and median stay |
| 5 | Horizontal bar | Matplotlib | Trends | Visits per department | Department that visits most |
| 6 | Pie chart | Matplotlib | Trends | Share of visits by zone | Most and least used zone |
| 7 | Bar chart | Matplotlib | Books | Books borrowed per category | Highest-demand subject |
| 8 | Scatter plot | Matplotlib | Books | Rating vs number of ratings, with correlation | Popularity and rating are only weakly related |
| 9 | Box plot | Seaborn | Books | Spread of fines per department | Department with highest median fine |
| 10 | Donut chart | Matplotlib | Books | On time, late, overdue, still within due date | Share of late and overdue books |
| 11 | Gauge | Plotly | Live | Live occupancy percentage | Quiet, moderate or busy |
| 12 | Bars and line | Matplotlib | Live | Occupancy by zone, and the live ticker | Current crowding |
| 13 | Line and dots | Matplotlib | Predict | Predicted occupancy for a day, with the best three hours | Best time to visit |
| 14 | Bar chart | Matplotlib | Predict | What drives the prediction (feature importance) | Hour matters most |
| 15 | Scatter plot | Matplotlib | Predict | Predicted vs actual occupancy | Points close to the line means accurate |

Say: "Matplotlib is the main library. Seaborn is used for the heatmap and box plot because it makes statistical charts easier. Plotly is used for the interactive gauge."

---

## 7. The predictor (very likely to be asked)
- **Model:** Random Forest Regressor (scikit-learn). A forest of decision trees, each trained on random parts of the data. The average of the trees is the prediction.
- **Inputs:** hour, day of week, zone.
- **Output:** predicted occupancy percentage.
- **Training:** the first 80% of days. **Testing:** the last 20%, which the model never saw.
- **Scores shown in the app:** R² (how much of the variation is explained) and MAE (average error in percentage points).
- **Why Random Forest?** It handles categories and numbers together, does not need scaling, and is hard to overfit with these settings. It is also explained easily.

---

## 8. Demo script (about 3 minutes)
1. Open the app. Point to the header and the **Live** pill. Say it is a live simulation.
2. Go through the **KPI cards**: live occupancy, seats free, peak hour, visits, books borrowed, overdue books. Explain the change arrows.
3. **Live tab:** point to the gauge and the zone bars. Let it refresh once. Show the entry and exit feed.
4. **Trends tab:** show the line chart (busy afternoons), the heatmap (best and worst slots), the histogram, the pie chart.
5. **Books tab:** show the bar chart, the scatter plot (correlation), the box plot (fines), the donut chart, the top borrowed books table and the overdue watchlist.
6. **Predict tab:** show the best time to visit, the prediction chart, the feature importance and the predicted vs actual check.
7. **Sidebar:** switch to dark mode, pick a department, choose a zone and a date range. Show that the charts and captions change.
8. Click a **CSV download** button. Show the data explorer search with a student ID.
9. Finish by showing the GitHub repo and the Streamlit link.

---

## 9. Likely viva questions and model answers

**Project and topic**
1. **What is the project?** An interactive Streamlit dashboard for the CHRIST library: occupancy, demand, fines and a busy-hour predictor.
2. **Why this topic?** Students waste time going to a crowded library. It is CHRIST-specific and no two students can choose the same one.
3. **What problem does it solve?** It shows when to visit, which seats are free and which subjects are popular.
4. **Who are the users?** Students, the library staff and the admin team.
5. **What is "real-time" here?** Live mode updates occupancy and the entry and exit feed every few seconds. With real data it would read from the library's gate system.
6. **What would you add with more time?** Real card-swipe data, seat booking, mobile alerts and a login for staff.

**Dataset**
7. **Explain the dataset.** Section 4 of this guide: the real Kaggle catalogue and the simulated library activity, with about 3,400 rows across the files.
8. **Where is the data from?** Kaggle, "7k Books with Metadata" by dylanjcastillo (link in the README). The library activity is simulated.
9. **Why simulated?** The library does not publish visit or borrowing data.
10. **How many rows and columns?** The main table has 1,289 rows and 23 columns. The catalogue has 587 books and 9 columns. The visit log sample has 1,500 rows and 9 columns.
11. **Why did you reduce the data?** The original was 4 MB and over 26,000 rows. Smaller tables are easier to read, explain and load.
12. **How did you clean the Kaggle data?** Dropped rows with no title, removed duplicate titles, filled missing numbers with medians, kept the first category for multi-category books.
13. **What is a categorical versus numerical column?** Categorical: department, zone, category, status. Numerical: fine_inr, late_days, average_rating, num_pages.
14. **What is a timestamp?** A date and time together, for example entry_time, used to group visits by hour.
15. **How do you know the simulation is realistic?** The patterns follow what a library looks like: a quiet morning, a busy afternoon, low weekends and a busier exam week. Each department reads different subjects.
16. **Why 14-day loans and Rs 2 fines?** These are simple, realistic assumptions that are easy to change in `common.py`.

**Libraries and code**
17. **Why Streamlit?** It turns Python into a web app with no HTML or JavaScript, and it can be deployed free.
18. **What does Pandas do?** Loads the CSVs, filters, groups, merges and computes totals.
19. **What does NumPy do?** Random numbers, arrays and maths, such as the correlation and the weighted average.
20. **Matplotlib vs Seaborn vs Plotly?** Matplotlib is the base library for most charts. Seaborn adds statistical charts (heatmap, box plot). Plotly makes interactive charts (the gauge).
21. **What is scikit-learn used for?** The Random Forest predictor.
22. **What is `st.cache_data`?** It stores the result of a function so that loading the CSVs happens once, not on every click.
23. **What is `st.fragment`?** A part of the page that can rerun on its own, here the live panels and KPI cards.
24. **What is `st.session_state`?** A dictionary that keeps values (such as the live simulation) between reruns.
25. **How does dark mode work?** The colours are stored as CSS variables. A toggle changes the variables, and the matplotlib charts use the same colours.
26. **Why separate common.py?** So the data generator and the app use the same zones, departments and hour pattern. A change in one place updates both.
27. **How does live mode work?** Each refresh interval, each zone's occupancy moves towards the expected value for that time, with a small random change. Events are added to the feed.
28. **Why a demo clock?** The library is closed at night. The demo clock replays an opening day so the live view always moves during the viva.

**Charts and insights**
29. **Which charts did you use?** Line, bar, horizontal bar, pie, donut, histogram, scatter, box, area, heatmap, plus the gauge and predictor charts. Ten matplotlib chart types in total, as the assignment asked.
30. **Why a line chart for occupancy?** It shows change over time, so the busy hours stand out.
31. **Why a heatmap?** It shows two variables at once (day and hour) with colour, so the best and worst slots are easy to see.
32. **Why a histogram?** To show how stay length is spread out, not just the average.
33. **Why a scatter plot?** To check whether popular books are also highly rated. The correlation is weak.
34. **Why a box plot?** It shows the median, the spread and outliers of fines per department.
35. **What is a donut chart?** A pie chart with the centre cut out. It shows the share of return statuses.
36. **Why not use a 3D chart?** It makes values hard to compare, so 2D charts are clearer.
37. **How are captions made?** They are computed from the filtered data, so the text changes with the filters.

**Predictor**
38. **How does the predictor work?** Section 7 of this guide: a Random Forest trained on hour, day and zone.
39. **What are R² and MAE?** R² is how much of the variation the model explains (closer to 1 is better). MAE is the average error in percentage points.
40. **Why train on 80% and test on 20%?** So the model is checked on days it has not seen. Testing on the training data would give false confidence.
41. **What is overfitting?** When a model memorises the training data and fails on new data. Limiting tree depth helps prevent it.
42. **Is the prediction accurate?** Show the R² shown in the app and the predicted vs actual chart. Explain it is an estimate for planning, not an exact forecast.

**Design and evaluation**
43. **How did you test the app?** I ran every chart in light and dark mode without errors, and checked the numbers against the data files.
44. **What are the limitations?** The library activity is simulated, the live mode is a simulation, the catalogue is a sample, and the predictor only uses three inputs.
45. **How would you deploy it?** Push to GitHub, connect to Streamlit Community Cloud, select app.py, and deploy.
46. **How would you make it real-time with real data?** Replace the simulated feed with a database or API that records card swipes at the gate, and point the app at it. The charts stay the same.
47. **What is the biggest challenge?** Making the simulated data look realistic, so that charts show meaningful patterns. I did this by using department preferences, an exam week and the hourly pattern.

---

## 10. Quick reference for the viva table
- Title: **CHRIST LibraSmart: Library Seat Occupancy & Book Demand Analytics Dashboard**
- Libraries: Streamlit, Pandas, NumPy, Matplotlib, Seaborn, Plotly, scikit-learn
- Main data: Kaggle "7k Books with Metadata" (real), library visits and borrowing (simulated)
- Sizes: borrowing 1,289 rows x 23 columns; catalogue 587 x 9; visits 1,500 x 9; occupancy 1,950 x 6
- Charts: 10 matplotlib types plus Plotly gauge and predictor charts
- Model: Random Forest, 80/20 train-test split
- Themes: light and dark
