import os
import datetime
import pandas as pd
from src.utils import scrapeDataFromSpreadsheet, generate_colors
import src.plots as plots
import config
import traceback

plots_folder = config.plots_folder
os.makedirs(plots_folder, exist_ok=True)

sheetId = os.environ.get("sheetId")
if not sheetId:
    raise ValueError("Environment variable sheetId not set!")

gids = config.gids

dg = config.hossa_col['dark_green']
lg = config.hossa_col['light_green']
dr = config.hossa_col['dark_red']

log_file = config.log_file

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    with open(log_file, "a") as f:
        f.write(line + "\n")
    print(line)


def run_update():
    log("=== Starting daily update ===")

    try:
        # Scrape data
        df_tab = scrapeDataFromSpreadsheet(sheetId, gids['tab'])
        df_stopa = scrapeDataFromSpreadsheet(sheetId, gids['stopa'])
        df_sums = scrapeDataFromSpreadsheet(sheetId, gids['sums']).iloc[:,1:-1]
        df_wyceny = scrapeDataFromSpreadsheet(sheetId, gids['wyceny'])
        df_wig = scrapeDataFromSpreadsheet(sheetId, gids['wig'])

        # --- Horizontal bar plot ---
        title = "stopa-zwrotu"
        val_col = "Stopa zwrotu"
        label_col = "Nazwa"
        fontsize = 13
        colors_list = [dr, lg, dg]

        colors, cmap, norm = generate_colors(df_stopa, val_col, colors_list)
        plots.horizontal_bars(df_stopa, val_col, label_col, colors, 
                              title=title, xlabel=val_col, fontsize=fontsize, path=plots_folder)

        # --- Donut plot ---
        title = "udzial"
        val_col = "Udział w portfelu"
        label_col = "Nazwa"
        fontsize = 11
        colors_list = ['#ddeedd', '#224422']
        colors, cmap, norm = generate_colors(df_stopa, val_col, colors_list, to_hex=True)
        
        path_donut = os.path.join(plots_folder, f"{title}.html")
        
        if os.path.exists(path_donut):
            os.remove(path_donut)
            log(f"Removed existing file: {path_donut}")
            
        plots.donut(df_stopa, val_col, label_col, colors, title=title, fontsize=fontsize, path=plots_folder)
        log(f"Saved new plot: {path_donut}")

        # --- Portfolio vs WIG plot ---
        title = "portfolio_vs_wig"
        path_wig = os.path.join(plots_folder, f"{title}.html")
        fontsize = 17
        if os.path.exists(path_wig):
            os.remove(path_wig)
            log(f"Removed existing file: {path_wig}")
        plots.portfolio_vs_wig(df_wig, title=title, fontsize=fontsize, height=450, path=plots_folder)
        log(f"Saved new plot: {path_wig}")

        # --- Tables ---
        table_files = [
            ("portfolio_tab.html", plots.table2html, df_tab, {"fontsize":14}),
            ("wyceny_tab.html", plots.table2html, df_wyceny, {"fontsize":14, "link":"link (hidden)"}),
            ("sums_tab.html", plots.vals2html, df_sums, {"fontsize":18})
        ]

        for filename, func, df, kwargs in table_files:
            file_path = os.path.join(plots_folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                log(f"Removed existing file: {file_path}")
            func(df, title=filename.replace(".html",""), path=plots_folder, **kwargs)
            log(f"Saved new plot: {file_path}")

        log("All plots and tables saved successfully.")

    except Exception as e:
        log("ERROR occurred during update!")
        log(traceback.format_exc())

    log("=== Daily update completed ===")

if __name__ == "__main__":
    run_update()
