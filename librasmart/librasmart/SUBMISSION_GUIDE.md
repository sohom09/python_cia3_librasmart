# LibraSmart: Submission Guide (MCA411-2, Component 3)

## Rubric checklist (25 marks)
| Rubric | Marks | Where it is covered |
|---|---|---|
| Topic selection | 5 | CHRIST-specific, unique topic, entered in the sheet before 15 Nov |
| Implementation | 10 | Multi-tab Streamlit app, 10 chart types, KPI cards, filters, predictor, light/dark mode, CSV export |
| Innovative idea / real-time | 5 | Live mode (auto-refresh gauge, zone bars, ticker, entry feed), busy-hour predictor, real Kaggle catalogue |
| Concept clarity (viva) | 5 | Practise the viva notes below; know every library and chart |

## Sheet entry (already submitted)
**Title:** CHRIST LibraSmart: Library Seat Occupancy & Book Demand Analytics Dashboard
**Description:** LibraSmart is an interactive Streamlit dashboard for the CHRIST University library that shows live seat occupancy by floor and zone, peak-hour crowding, most borrowed book categories, overdue returns and fine analysis, and a simple busy-hour predictor to help students choose the best time to visit. Python libraries used: Streamlit, Pandas, NumPy, Matplotlib, Seaborn, Plotly, scikit-learn. Dataset: simulated real-time library entry and borrowing data (CSV), auto-refreshed live in the app.

## Step 1: Test locally
```
pip install -r requirements.txt
streamlit run app.py
```
Check every tab in light and dark mode, try each sidebar filter, and switch Live mode on and off.

## Step 2: Upload the folder to GitHub (no git needed)
1. Sign in at github.com and click New repository. Name it `librasmart`, set it to Public, and create it.
2. Click "uploading an existing file".
3. Drag in everything inside the `librasmart` folder: `app.py`, `common.py`, `generate_data.py`, `requirements.txt`, `README.md`, and the `data` and `.streamlit` folders.
4. Click Commit changes.
5. Copy the repository link (for example `https://github.com/<username>/librasmart`).

If the `.streamlit` folder does not upload, open the repo, click Add file, Create new file, type `.streamlit/config.toml` as the name, and paste the contents of that file.

## Step 3: Deploy on Streamlit Community Cloud
1. Go to share.streamlit.io and sign in with GitHub.
2. Click Create app, then choose "Deploy a public app from GitHub".
3. Pick your repository, branch `main`, and main file path `app.py`.
4. Click Deploy and wait a few minutes for the build.
5. Open the app link (`https://<name>.streamlit.app`) and check that it loads.

## Step 4: Submit in Google Classroom
- GitHub repository link
- Streamlit app link
- Source link (the Kaggle dataset): https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata

## Step 5: Viva day
Arrive 5 minutes early, open the deployed app before your slot, and keep the GitHub repo open too.

### Two-minute talk
1. Problem: students cannot tell when the library is crowded or which books are in demand.
2. Solution: LibraSmart shows live seat occupancy, crowd patterns, book demand, fines, and predicts the best time to visit.
3. Demo order: KPI cards, Live tab, Trends tab (heatmap), Books tab, Predict tab, dark mode, a sidebar filter, CSV download.
4. Data: real Kaggle book catalogue plus simulated library entries and borrowing, because the library does not publish live data.
5. Future scope: connect to real library swipe-card data, seat booking, mobile alerts.

### Likely viva questions
- **Why Streamlit?** It turns Python scripts into interactive web apps without HTML, CSS or JavaScript.
- **Why is the data simulated?** The library does not publish live data. The app reads CSV files, so real data with the same columns can replace it.
- **How does live mode work?** `st.fragment(run_every=...)` reruns only the live panels every few seconds. Each tick updates seat counts with a random walk towards the expected occupancy for that time.
- **What does the predictor do?** A Random Forest regressor learns occupancy from hour, day of week and zone. It is trained on the first 80% of days and tested on the last 20%, and the app shows R² and MAE.
- **What is R² / MAE?** R² is how much of the variation the model explains. MAE is the average prediction error in percentage points.
- **Matplotlib vs Seaborn vs Plotly?** Matplotlib is the base plotting library, Seaborn adds statistical charts and nicer styling on top of it (heatmap, box plot), and Plotly makes interactive charts (the gauge).
- **Why Pandas?** For loading, filtering, grouping and merging the CSV data.
- **What does `st.cache_data` do?** It stores loaded data so it is not read again on every interaction.
- **How is dark mode done?** A sidebar toggle injects CSS variables and the matplotlib charts use the same colours.
- **How are fines calculated?** Rs 2 per day after the 14-day loan period.
- **How would you make it real-time with real data?** Replace the simulated feed with an API or database that records card swipes at the library gate.
