import os
import datetime
import pandas as pd

from src.utils import scrapeDataFromSpreadsheet
import src.plots as plots
import src.colors as c
import config

import traceback

wp_folder = config.WP_FOLDER
plots_folder = config.PLOTS_FOLDER
log_file = config.LOG_FILE

gids = config.GIDS

dg = config.HOSSA_COL['dark_green']
lg = config.HOSSA_COL['light_green']
dr = config.HOSSA_COL['dark_red']

sheetId = os.environ.get("sheetId")
if not sheetId:
    raise ValueError("Environment variable sheetId not set!")

output_path = os.path.join(wp_folder, plots_folder)
os.makedirs(output_path, exist_ok=True)

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

        colors, cmap, norm = c.generate_colors(df_stopa, val_col, colors_list)
        plots.horizontal_bars(df_stopa, val_col, label_col, colors=[dr, dg], 
                              title=title, xlabel=val_col, fontsize=fontsize, path=output_path)

        # --- Donut plot ---
        title = "udzial"
        val_col = "Udział w portfelu"
        label_col = "Nazwa"
        fontsize = 11
        colors_list = ['#ddeedd', '#224422']
        colors, cmap, norm = c.generate_colors(df_stopa, val_col, colors_list, to_hex=True)
        
        path_donut = os.path.join(output_path, f"{title}.html")
        
        if os.path.exists(path_donut):
            os.remove(path_donut)
            log(f"Removed existing file: {path_donut}")
            
        plots.donut(df_stopa, val_col, label_col, colors, title=title, fontsize=fontsize, path=output_path)
        log(f"Saved new plot: {path_donut}")

        # --- Portfolio vs WIG plot ---
        title = "portfolio_vs_wig"
        path_wig = os.path.join(output_path, f"{title}.html")
        fontsize = 17
        if os.path.exists(path_wig):
            os.remove(path_wig)
            log(f"Removed existing file: {path_wig}")
        plots.portfolio_vs_wig(df_wig, title=title, fontsize=fontsize, height=450, path=output_path)
        log(f"Saved new plot: {path_wig}")

        # --- Tables ---
        df_wyceny = df_wyceny[df_wyceny['DCF'].astype(str).str.strip().ne("")]

        table_files = [
            ("portfolio_tab.html", plots.table2html, df_tab, {"fontsize":14}),
            ("wyceny_tab.html", plots.table2html, df_wyceny, {"fontsize":14, "link":"link (hidden)"}),
            ("sums_tab.html", plots.vals2html, df_sums, {"fontsize":18})
        ]

        for filename, func, df, kwargs in table_files:
            file_path = os.path.join(output_path, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                log(f"Removed existing file: {file_path}")
            func(df, title=filename.replace(".html",""), path=output_path, **kwargs)
            log(f"Saved new plot: {file_path}")

        log("All plots and tables saved successfully.")

    except Exception as e:
        log("ERROR occurred during update!")
        log(traceback.format_exc())

    log("=== Daily update completed ===")

if __name__ == "__main__":
    run_update()