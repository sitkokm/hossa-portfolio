import pandas as pd
import numpy as np

import time
import re
import os

from lxml.etree import tostring
from bs4 import BeautifulSoup
import requests

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