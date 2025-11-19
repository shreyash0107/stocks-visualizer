# Stock Portfolio Visualizer

This is a Streamlit-based Stock Portfolio Visualizer & Risk Estimator.

Contents:
- `Home.py` – main Streamlit app
- `analytics.py`, `data.py`, `monte_carlo.py`, `plots.py` – analysis modules
- `data/` – data files (contains `data.csv`)
- `pages/` – extra Streamlit pages

How to run locally (basic):

1. Create and activate a virtual environment

   PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Run the app

   ```powershell
   streamlit run Home.py
   ```

Notes:
- This repository contains example analytics and a simulated in-memory "database" for demo purposes.
- The `data/data.csv` file may contain sample data; remove or replace as needed.

License: add your preferred license.
