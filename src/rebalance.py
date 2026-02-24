import pandas as pd 

def rebalance_mask( dates : pd.DatetimeIndex, freq: str = "Q") -> pd.Series:
    """
    Construit un masque booléen indiquant les dates de rebalancing.
    
    Problème réel :
    - "fin de trimestre" ( 31/03, 30/06, 30/09, 31/12 ) peut tomber un week-end/jour férié
    - tes données ( dates ) n'auront pas forcément ces jours exacts
    
    Solution :
    - on rebalance sur le Dernier jour dispononible de chaque periode ( mois/trimestre)
    
    Paramètres
    -----------
    dates : pd.DatetimeIndex
        Index des dates de tes returns ( ou prix ).
    freq : str
        "M" pour rebal fin de mois, "Q" pour rebal fin de trimestre
        
    Retour
    -------
    pd.series ( bool ), index = dates
        True aux dates ou on rebalance.
    """

    # Garentis un DatetimeIndex ( au cas ou on donne une liste )
    idx = pd.DatetimeIndex(dates)

    # Vérifie la fréquence
    if freq not in ("M", "Q"):
        raise ValueError("freq doit etre 'M' (mois) ou 'Q' (trimestre).")
    
    # On transforme chaque date en period ( mois ou trimestre)
    # Exemple : 2026-02-19 -> 2026Q1 si freq="Q"
    per = idx.to_period(freq)

    # On veut "le dernier jour présent dans tes données" pour chaque période.
    # Méthode :
    # - On convertit idx en Série
    # - groupby par la période ( mois ou trimestre)
    # - transform("max") renvoie, chaque ligne, la date max du groupe
    last_in_period = pd.Series(idx).groupby(per).transform("max").values

    # rebalance = True quand la date = dernier jour de sa periiode
    mask = (idx == last_in_period)

    # On renvoie une Series bool avec index=dates pour faire reb.loc[dt]
    return pd.Series(mask, index=idx)

