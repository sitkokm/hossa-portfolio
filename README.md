# hossa-portfolio

This repository generates simple interactive HTML plots and tables for a portfolio stored in a Google Sheet. It is written in Python and uses a small Flask app to trigger updates.

---
## What this project does
- Reads several tabs from a Google Spreadsheet.
- Converts the data into interactive HTML plots and responsive tables.
- Saves HTML files into a local `plots` folder. A log file (log/log.txt) records actions.
- A minimal Flask endpoint "/" triggers a full update of all plots.

## Repository structure 
```
├── load_env.py          # only for setting up environment variables from .env locally
├── testing.ipynb        # optional for development and testing
├── app.py               # Flask app with to trigger updates
├── config.py            # configuration: output folders, sheet GIDs, log file path
├── passenger_wsgi.py    # only needed in our hosting environment
├── src/
│   ├── update_script.py # main script that scrapes the sheet and generates plots
│   ├── utils.py         # helper functions: scraping, color generation, string → float conversion
│   └── plots.py         # functions that generate HTML plots/tables
├── plots/               # created at runtime - stores generated HTML files
└── log/
    └── log.txt          # created at runtime - stores logs 
```

## Requirements and installation

### 1. Recommended Python: 3.11 (but 12, 13 should be fine).
    git clone https://github.com/sitkokm/hossa-portfolio
### 2. Setting up environment and installing dependencies:

#### Option A — Conda (especially for JupyterLab)
1. Create environment:
   ```
   conda create -n hossa_env python=3.11 -y
   ```
2. Activate it:
    ```
   conda activate hossa_env
    ```
3. Install pip and required packages:
   ```
   pip install -r requirements.txt
   ```

#### Option B — virtualenv / pip
1. ```
   python -m venv .venv
   ```
2. ``` 
   .venv\Scripts\activate
   ```
3. ```
   pip install -r requirements.txt
   ```

### 3. Keys to accessing the Google Sheet

The code expects an environment variable named `sheetId`. The simplest way is to create a `.env` file in the project root containing:
sheetId=YOUR_GOOGLE_SHEET_ID_HERE

How to find the Google Sheet ID:
- Open the spreadsheet in your browser.
- Look at the URL: https://docs.google.com/spreadsheets/d/<THIS_PART_IS_SHEET_ID>/edit...
- Copy the part between `/d/` and `/edit`.

Save the `.env` file in the project root (same folder as app.py).

To load environment variables into your current shell/session run:
```
pip install python-dotenv
python load_env.py
```
---

## How to run the update locally

1. Ensure dependencies installed and `.env` is set up (sheetId present).
2. From the project root run the update directly:
   python src/update_script.py
This will:
- Fetch data from Google Sheets,
- Generate: stopa-zwrotu.html, udzial.html, portfolio_vs_wig.html and several table HTML files,
- Save them into the `plots` folder and append messages to the log.

If you get an error: "Environment variable sheetId not set!" — set your sheetId via .env or environment variable.

## How the Flask endpoint works
- app.py exposes a single route at "/". Visiting that route triggers the same update routine:
  - It imports src.update_script and calls run_update().
- To run the Flask app locally:
  ```
    set FLASK_APP=app.py
    set FLASK_ENV=development
    flask run
  ```

Then open http://127.0.0.1:5000/ in your browser; you should see "Plots updated successfully!" or an error message.

## Running under a WSGI host
- passenger_wsgi.py and the `application` variable are already prepared for some hosting setups (the file loads app.py and exposes application).
- It only applies on our hosting server - it only runs the Flask app when the server receives a request, so it will trigger updates on demand without needing to run anything manually.
- No need to change as it only runs app.py

---

## Jupyter notebook (test.ipynb)

- The notebook demonstrates how plots are generated step-by-step, so you can dig more into the code
- To run it you will need a JupyterLab environment. 
- Set up kernel:
    ```
    pip install jupyterlab ipykernel
    ```
- If you want to run inside the same environment and show the same environment in Jupyter:
  ```
  python -m ipykernel install --user --name hossa_env --display-name "hossa_env"
  ```
- The notebook reads the same `.env` variable and uses the functions in src/ to build plots.

## Where outputs go

- Plots (interactive HTML) are saved to: the folder defined in config.py -> plots_folder (default "plots").

- Logs: config.py -> log_file (default "log/log.txt").

