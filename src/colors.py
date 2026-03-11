import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import pandas as pd
import numpy as np

import colorsys

import src.utils as u

def lighten_color(hex_color, amount=0.4):
    """
    Rozjaśnia kolor hex o podany współczynnik (0–1),
    ale nie do czystej bieli.
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    l = min(1, l + amount * (1 - l))  # rozjaśnianie bez wybielania
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))


def interpolate_color(c1, c2, t):
    """
    Interpolacja liniowa między dwoma kolorami hex.
    t = 0 → c1
    t = 1 → c2
    """
    c1 = c1.lstrip('#')
    c2 = c2.lstrip('#')
    r1, g1, b1 = tuple(int(c1[i:i+2], 16) for i in (0, 2, 4))
    r2, g2, b2 = tuple(int(c2[i:i+2], 16) for i in (0, 2, 4))

    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)

    return f'#{r:02x}{g:02x}{b:02x}'

def positive_negative_colors(colors, values):
    neg_color, pos_color = colors
    min_val = min(values)
    max_val = max(values)

    neg_light = lighten_color(neg_color, 0.5)
    pos_light = lighten_color(pos_color, 0.5)

    new_colors = []
    for v in values:
        if v < 0:
            # teraz: min → neg_color (ciemny), 0 → neg_light (jasny)
            t = (v - min_val) / (0 - min_val) if min_val != 0 else 1
            t = 1 - t  # ODWRÓCENIE GRADIENTU
            new_colors.append(interpolate_color(neg_color, neg_light, t))
        else:
            # teraz: 0 → pos_light (jasny), max → pos_color (ciemny)
            t = v / max_val if max_val != 0 else 1
            t = 1 - t  # ODWRÓCENIE GRADIENTU
            new_colors.append(interpolate_color(pos_color, pos_light, t))
    return new_colors

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
    df[col_name] = u.str2float(df[col_name])
  
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