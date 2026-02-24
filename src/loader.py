import pandas as pd
import numpy as np

def load_prices_csv(path: str, date_col: str = "Date") -> pd.DataFrame:
    """
    Charger un CSV de prix (une colonne de date + une colonne par actif).
    
    Paramètres :
    path : str
        chemin veers le fichier CSV.
    date_col : str
        nom de la colonne contenant les dates ( par defaut "Date ).
        
    Retour
    -------
    pd.DataFrame
        DataFrame indzxé par dates ( DatetimeIndex ), trié, avec colonnes = actifs.
        Les lignes entièrement vides sont supprimées.
    """

    # lecture du CSV ; parse_dates convertis la colonne Date en datetime
    px = pd.read_csv(path, parse_dates=[date_col])

    # On met la colonne Date en index pour manipuler des séries temporelles
    px = px.set_index(date_col)

    # Trie chronologique (indispensable pour pct_change / backtest)
    px = px.sort_index()

    # Supprime les lignes ou toutes les colonnes d'actifs sont Nan
    px = px.dropna(how="all")

    return px

def clean_prices(px):
    px = px.replace(0, np.nan)
    px = px.ffill()
    return px
