import pandas as pd
import numpy as np

def fix_scale_breaks(prices: pd.DataFrame, threshold: float = 20.0) -> pd.DataFrame:
    """
    Corrige les ruptures d'échelle (ex: x100) typiques des glitches Yahoo.
    Méthode :
    - calcule le ratio jour/jour
    - si ratio > threshold ou < 1/threshold, on considère une rupture
    - on rescale la partie 'après' la rupture pour recoller au niveau 'avant'
    """
    px = prices.copy()

    for col in px.columns:
        s = px[col].astype(float).copy()

        s = s.replace(0, np.nan).ffill()
        r = s / s.shift(1)

        # Ruptures candidates
        breaks = r[(r > threshold) | (r < 1.0 / threshold)].dropna()
        if breaks.empty:
            px[col] = s
            continue

        # On corrige séquentiellement (cas rare de multiples breaks)
        for dt, ratio in breaks.items():
            if ratio > threshold:
                # saut UP énorme -> on divise la suite par ratio
                scale = ratio
                s.loc[dt:] = s.loc[dt:] / scale
            else:
                # saut DOWN énorme -> on multiplie la suite par 1/ratio
                scale = 1.0 / ratio
                s.loc[dt:] = s.loc[dt:] * scale

        px[col] = s

    return px


def calc_simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Returns simples : r_t = P_t / P_{t-1} - 1
    Nettoyage robuste Yahoo :
    - remplace 0 par NaN, ffill
    - corrige ruptures d'échelle (x100, etc.)
    - pct_change(fill_method=None)
    """
    prices = prices.replace(0, np.nan).ffill()
    prices = fix_scale_breaks(prices, threshold=20.0)

    rets = prices.pct_change(fill_method=None)
    return rets.dropna(how="all")
