import pandas as pd
import numpy as np

import time
import re
import os

from lxml.etree import tostring
from bs4 import BeautifulSoup
import requests

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# General utils
def str2float(series: pd.Series) -> pd.Series: # df[col] = str2float(df[col])
    return (
        series.astype(str)
        .str.strip()
        .replace({"": None, "-": None})
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )

def scrapeDataFromSpreadsheet(sheetId, gid, headers = True) -> pd.DataFrame:
    url = f'https://docs.google.com/spreadsheets/u/0/d/{sheetId}/gviz/tq?tqx=out:html&tq=&gid={gid}'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    
    # finding first table in html
    table = soup.find_all('table')[0]
    
    # dwonload all rows
    rows = [[td.text.strip() for td in row.find_all("td")] for row in table.find_all('tr')]
    
    # to DataFrame
    if len(rows) < 2:
        return pd.DataFrame()  # if no data -> return empty table

    if headers:
        df = pd.DataFrame(rows[1:], columns=rows[0])  # first row as headers
    else:
        df = pd.DataFrame(rows)
    return df

def generate_colors(df: pd.DataFrame, col_name: str, colors_list=['#a6a6a6', '#304536'], to_hex = True):
    """
    Generuje kolory dla wartości w kolumnie df[col_name] w gradiencie.
    
    Args:
        df (pd.DataFrame): DataFrame wejściowy
        col_name (str): nazwa kolumny numerycznej
        colors_list (list): lista kolorów w hex lub nazwach, np. ["#a6a6a6", "#ffff00", "#2d4236"]
                            jeśli None -> używa ["#a6a6a6", "#2d4236"]
    
    Returns:
        colors (list): lista kolorów dla wartości
        cmap (Colormap): obiekt colormap (można wykorzystać do legendy)
        norm (Normalize): normalizator wartości (np. do colorbar)
    """
    df[col_name] = str2float(df[col_name])
  
    # Tworzymy colormap z listy kolorów
    cmap = mcolors.LinearSegmentedColormap.from_list("custom", colors_list)
    
    # Normalizacja wartości
    norm = plt.Normalize(df[col_name].min(), df[col_name].max())
    
    # Generujemy kolory dla każdej wartości
    colors = cmap(norm(df[col_name]))

    if to_hex:
        colors = [mcolors.to_hex(c) for c in colors]
    
    return colors, cmap, norm

def test_colors(df, val, colors_list):
    colors, cmap, norm = generate_colors(df, val, colors_list=colors_list)

    gradient = np.linspace(df[val].min(), df[val].max(), 256).reshape(1, -1)
    plt.figure(figsize=(15,1))
    plt.imshow(gradient, aspect='auto', cmap=cmap)
    plt.axis('off')
    plt.show()