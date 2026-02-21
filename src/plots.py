import pandas as pd
import numpy as np

from matplotlib.patches import Patch
import plotly.graph_objects as go

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import src.utils as u
import os

def table2html(df: pd.DataFrame, title="table", fontsize=14, link=None, path=""):
    """
    Generuje responsywną tabelę HTML:
    - Arial
    - nagłówek ciemnozielony #304536, biała czcionka
    - wiersze naprzemiennie #cedbce / biały
    - hover #f0a1a1
    - czarne ramki
    - linkowanie kolumny poprzedzającej kolumnę `link`
    - kolumna `link` jest usuwana po zastosowaniu linków
    - automatycznie dopasowuje wysokość do ekranu (bez scrollbars)
    """
    html = f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}
        #table-container {{
            width: 100%;
            height: 100%;
            overflow: auto; /* allows vertical scrolling if necessary */
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
            font-size: {fontsize}px;
        }}
        th {{
            background-color: #304536;
            color: white;
            font-weight: bold;
            padding: 0.7em 1em;
            border-bottom: 3px solid black;
            text-align: center;
        }}
        td {{
            padding: 0.7em 1em;
            text-align: center;
            color: black;
        }}
        tr:nth-child(even) td {{ background-color: #cedbce; }}
        tr:nth-child(odd) td {{ background-color: #ffffff; }}
        tr:hover td {{ background-color: #f0a1a1; }}
        a {{
            color: #852029;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
    </head>
    <body>
    <div id="table-container">
        <table>
            <thead>
                <tr>
    """

    # jeśli mamy linkową kolumnę
    link_idx = None
    if link and link in df.columns:
        link_idx = df.columns.get_loc(link)

    # nagłówki (bez kolumny linkowej)
    for i, col in enumerate(df.columns):
        if i == link_idx:
            continue
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"

    # wiersze
    for _, row in df.iterrows():
        html += "<tr>"
        for i, (col, val) in enumerate(row.items()):
            if i == link_idx:
                continue
            if link_idx and i == link_idx - 1:  
                # dodajemy link do wartości w kolumnie poprzedzającej
                url = row.iloc[link_idx]
                html += f'<td><a href="{url}" target="_blank">{val}</a></td>'
            else:
                html += f"<td>{val}</td>"
        html += "</tr>"

    html += "</tbody></table></div>"

    # JS na dopasowanie wysokości do okna
    html += """
    <script>
        const container = document.getElementById('table-container');
        function resizeTable() {
            container.style.height = window.innerHeight + 'px';
        }
        window.addEventListener('resize', resizeTable);
        resizeTable();
    </script>
    """

    html += "</body></html>"

    with open(f"{path}/{title}.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Plik {title}.html zapisany!")


def vals2html(df: pd.DataFrame, title="table", fontsize=17, link=None, path=""):
    """
    Generuje responsywną tabelę HTML:
    - Arial
    - nagłówek biały, czarna czcionka
    - wiersze naprzemiennie #cedbce / biały
    - hover #f0a1a1
    - jeżeli `link` != None: kolumna `link` zawiera URL-e,
      a kolumna poprzedzająca dostaje <a href="..."> z tym linkiem.
      Po zastosowaniu linków kolumna `link` jest usuwana.
    """
    html = f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}
        #table-container {{
            width: 100%;
            height: 100%;
            overflow: auto;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
            font-size: {fontsize}px;
        }}
        th {{
            background-color: white;
            color: black;
            font-weight: bold;
            padding: 0.7em 1em;
            border-bottom: 2px solid black;
            text-align: center;
        }}
        td {{
            background-color: white;
            padding: 0.7em 1em;
            text-align: center;
            color: black;
        }}
        tr:nth-child(even) td {{ background-color: #cedbce; }}
        tr:nth-child(odd) td {{ background-color: #ffffff; }}
        tr:hover td {{ background-color: #f0a1a1; }}
        a {{
            color: #852029;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
    </head>
    <body>
    <div id="table-container">
        <table>
            <thead>
                <tr>
    """

    # links handling
    link_idx = None
    if link and link in df.columns:
        link_idx = df.columns.get_loc(link)

    # headers but withut links
    for i, col in enumerate(df.columns):
        if i == link_idx:
            continue
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"
        for i, (col, val) in enumerate(row.items()):
            if i == link_idx:
                continue
            if link_idx and i == link_idx - 1:  
                url = row.iloc[link_idx]
                html += f'<td><a href="{url}" target="_blank">{val}</a></td>'
            else:
                html += f"<td>{val}</td>"
        html += "</tr>"

    html += "</tbody></table></div></body></html>"

    with open(f"{path}/{title}.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Plik {title}.html zapisany!")

def portfolio_vs_wig(df: pd.DataFrame, title="portfolio_vs_wig", fontsize=17, height=450, path = ""):
    """
    Interaktywny wykres HTML pokazujący wyniki portfela vs benchmark.
    Format:
    - czcionka Arial
    - kolory (#304536 portfel, #852029 benchmark)
    - hover w %
    - szeroki, responsywny wykres
    - x-axis wizualnie przy y=0 z tylko pierwszą i ostatnią etykietą (wyrównanie do lewej/prawej)
    """

    # remove nans and formatting 
    for col in df.columns:
        if col != "Data":
            df[col] = u.str2float(df[col])
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna()
    print(df)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Data"], y=df.iloc[:, 1],
        mode="lines",
        name=df.columns[1],
        line=dict(color="#304536", width=2),
        hovertemplate="%{y:.2f}%<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=df["Data"], y=df.iloc[:, 2],
        mode="lines",
        name=df.columns[2],
        line=dict(color="#852029", width=2),
        hovertemplate="%{y:.2f}%<extra></extra>"
    ))

    # fake x-axis on y=0 with only first and last label
    x_ticks = [df["Data"].iloc[0], df["Data"].iloc[-1]]
    x_labels = [df["Data"].iloc[0].strftime("%Y-%m-%d"),
                df["Data"].iloc[-1].strftime("%Y-%m-%d")]
    annotations = [
        dict(
            x=x_ticks[0], y=0,
            text=x_labels[0],
            showarrow=False,
            xanchor="left", 
            yanchor="top",
            font=dict(family="Arial", size=fontsize, color="black")
        ),
        dict(
            x=x_ticks[1], y=0,
            text=x_labels[1],
            showarrow=False,
            xanchor="right",  
            yanchor="top",
            font=dict(family="Arial", size=fontsize, color="black")
        )
    ]

    fig.update_layout(
        font=dict(family="Arial", size=fontsize, color="black"),
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            showline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="lightgray",
            zeroline=False
        ),
        shapes=[dict(
            type="line",
            x0=df["Data"].min(),
            x1=df["Data"].max(),
            y0=0,
            y1=0,
            line=dict(color="black", width=2)
        )],
        annotations=annotations,
        plot_bgcolor="white",
        hovermode="x unified",
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.05,
            xanchor="center", x=0.5,
            font=dict(size=fontsize)
        ),
        margin=dict(l=50, r=50, t=30, b=50)
    )

    full_path = os.path.join(path, f"{title}.html")
    if os.path.exists(full_path):
        os.remove(full_path)
        print(f"Removed existing file: {full_path}")

    fig.write_html(
        full_path,
        include_plotlyjs="cdn",
        full_html=True,
        config={
            "responsive": True
            }
    )
    print(f"Saved new plot: {full_path}")

def donut(df, val_col, label_col, colors=None, title=None, fontsize=12, path = ""):
    """
    Tworzy donut chart w HTML z wartościami procentowymi na pierścieniu,
    etykietami na zewnątrz i legendą po prawej stronie.
    """
    df[val_col] = u.str2float(df[val_col])
    
    if colors is None:
        colors = [f"rgba(31,{i*10%255},200,0.8)" for i in range(len(df))]
    else:
        colors = [mcolors.to_hex(c) for c in colors]

    fig = go.Figure(data=[go.Pie(
        labels=df[label_col],
        values=df[val_col],
        hole=0.5, 
        marker=dict(colors=colors, line=dict(color="white", width=1)), 
        textinfo="percent", 
        textposition="inside",
        insidetextfont=dict(size=fontsize, color="black"),
        hovertemplate="%{label}: %{value}<extra></extra>", 
        showlegend=True
    )])

    fig.update_layout(
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=fontsize) 
        ),
        margin=dict(t=40, b=40, l=40, r=120),
        paper_bgcolor="white"
    )
    
    full_path = os.path.join(path, f"{title}.html")
    if os.path.exists(full_path):
        os.remove(full_path)
        print(f"Removed existing file: {full_path}")

    fig.write_html(
        full_path,
        include_plotlyjs="cdn",
        full_html=True,
        config={"responsive": True}
    )
    print(f"Saved new plot: {full_path}")

def horizontal_bars(df, val_col, label_col, colors=None, 
                              title=None, xlabel=None, fontsize=10, path = ""):
    df[val_col] = u.str2float(df[val_col])
    values = df[val_col].astype(float).to_numpy()
    labels = df[label_col].to_numpy()
    n = len(df)

    if colors is None:
        colors = ["gray"] * n

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker=dict(color=colors),
        hovertemplate='%{y}: %{x:.2f}%<extra></extra>',
        showlegend=False
    ))
    
    # --- etykiety na końcach (positive outside on right, negative inside also right) ---
    dx_abs = 0.015 * (max(values) - min(values))
    annotations = []
    for i, (val, label) in enumerate(zip(values, labels)):
        if val >= 0:
            x_text = val + dx_abs
            xanchor = 'left'
            font = dict(family='Arial', size=fontsize, color='black')
        else:
            inner_dx = min(dx_abs, 0.4 * abs(val))
            x_text = val + inner_dx
            xanchor = 'left'
            font = dict(family='Arial', size=fontsize, color='white')
        annotations.append(dict(
            x=x_text,
            y=label,
            text=f"{val:.2f}%",
            xanchor=xanchor,
            yanchor='middle',
            font=font,
            showarrow=False
        ))

    fig.update_layout(
        annotations=annotations,
        font=dict(family='Arial', size=fontsize, color='black'),
        xaxis=dict(
            # title=xlabel,
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1
        ),
        yaxis=dict(
            autorange='reversed',  # top-to-bottom like barh
            showgrid=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        shapes=[dict(
            type='line',
            x0=0, x1=0,
            y0=-0.5, y1=n-0.5,
            line=dict(color='black', width=1.3)
        )],
        margin=dict(l=150, r=50, t=30, b=50),
        bargap = 0.5,
    )

    full_path = os.path.join(path, f"{title}.html")
    if os.path.exists(full_path):
        os.remove(full_path)
        print(f"Removed existing file: {full_path}")

    fig.write_html(
        full_path,
        include_plotlyjs="cdn",
        full_html=True,
        config={"responsive": True}
    )
    print(f"Saved new plot: {full_path}")
