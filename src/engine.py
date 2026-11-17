import pandas as pd

from .rebalance import rebalance_mask

def normalize_weights(w: pd.Series) -> pd.Series:
    """
    Normalise un vecteur de poids pour qu'il somme à 1.
    
    Règles :
    - poids négatifs/NaN => on force Nan à 0
    - somme doit etre > 0 ( sinon allocation invalide )
    
    rettourne
    -------
    pd.Series
        poids normalisés ( somme = 1 ).
    """

    # Remplace les Nan par 0 ( actif absent / poids non fourni)
    w = w.fillna(0)

    # Somme des poids 
    s = float(w.sum())

    # Si somme <=0, le portefeuille n'a pas de sens
    if s <= 0.0:
        raise ValueError("Somme des poids <+ 0. Allocation invalide.")
    
    # Normalisation 
    return w/s

def align_target_weights(assets: pd.Index, target_weights: dict) -> pd.Series:
    """
    Alligne le dict de poids cible sur les colonnes "assets".
    
    Exemple :
    - returns.columns = ["WORLD", "BONDS", "MM"]
    - target_weights dict peut etre incomplet
    => reindex + fillna(0) + normalisation.
    
    Retour
    -------
    pd.Series
        poids cibles alignés sur l'ordre des assets.
    """

    # convertit le dict en Series ; reindex pour suivre l'ordre exact des colonnes
    w = pd.Series(target_weights, dtype=float).reindex(assets)

    # Si un actif n'a pas de poids dans le dict => 0
    w = w.fillna(0.0)

    # Normalise pour que somme = 1
    return normalize_weights(w)

def backtest_portfolio(
    returns: pd.DataFrame,
    target_weights: dict,
    rebalance_freq: str = "Q",
    tc_bps: float = 5.0,
    start_value: float = 100.0,
) -> pd.DataFrame:
    """
    Moteur de backtest de portefeuille multi-actifs avec drift + rebalancing + couts.
    
    Hypothèses ( claires ) :
    1 ) On calcule le rendement portefeuille avec les poids du début de période : 
        R_p,t = sum_i w_{i,t-1} * r_{i,t}
    
    2 ) Après la variation de prix, les poids "driftent" ( se modifient mécanquement ) :
        w'_{i} = w_i * (1 + r_i)
        puis on renormalise pour somme =1
    
    3 ) Aux dates de rebalancing, on remet aux poids cibles

    4 ) Cout transactionnels simples :
        - turnover = sum_i |w_target - w_current
        - cout = turnover * tc ( tc exprimé en fraction, tc_bps/10000 )
        - on reduit la valeur du portefeuille : V *= ( 1 - cout )

    Paramètres
    ----------
    returns : pd.DataFrame
        Returns simples ( dates x assets )
    target_weights : dict
        Poids cible par actif
    rebalance_freq : str
        "Q" ( trimestre ) ou "M" ( mois) selon rebalance_mask
    tc_bps : float
        cout en basis points appliqué au turnover ( approximation ).
    start_value : float
        valeur initiale (NAV) du portefeuille.

    Retour
    -------
    pd.DataFrame
        Colonnes : 
        - value : valeur du portefeuille 
        - ret   : rendement net de la période, après coûts de rééquilibrage
    """

    # Validation minimale
    if returns is None or returns.empty:
        raise ValueError("returns est vide ou None.")
    
    # Liste des actifs = colonnes de returns 
    assets = returns.columns
    
    # Poids cibles allignés sur assets
    w_target = align_target_weights(assets, target_weights)

    # Dates de la simulation 
    dates = returns.index

    # Masque de rebalancing ( True aux dates rebal )
    reb = rebalance_mask(dates, freq=rebalance_freq)

    # Conversion bps -> fraction ( 5bps = 0.0005 )
    tc = tc_bps / 10_000.0

    # Valeur du portefeuille
    value = float(start_value)

    # Poids courant : on démarre a la cible ( choix simple )
    w = w_target.copy()

    # Stockage des résultats 
    out = []

    # Boucle date par date ( simple, explicite; optimisable plus tard )
    for dt in dates:
        # Valeur avant le rendement du jour et les éventuels coûts de rééquilibrage
        value_before_period = value

        # Returns de la date ; NaN remplacés par 0 ( actif manquant ce jour la )
        r = returns.loc[dt].fillna(0.0)

        # 1 ) Rendement du portefeuille avec poids début de période
        port_r = float((w * r).sum())

        # 2 ) Mise a jour de la valeur du portefeuille
        value *= (1.0 + port_r)

        # 3 ) Drift des poids après mouvement de marché
        # w_i <- w_i * (1 + r_i), puis normalisation
        w = w * (1.0 + r)
        w = normalize_weights(w)

        # 4 ) Rebalancing a la fin de la periode si date marquée
        if bool(reb.loc[dt]):
            # Turnover = somme des écarts absoluts des poids
            turnover = float((w_target - w).abs().sum())

            # cout appliqué a la valeur ( approximation )
            cost = turnover * tc
            value *= (1.0 - cost)

            # On remet les poids exactement a la cible
            w = w_target.copy()

        # Rendement net cohérent avec la NAV après frais de rééquilibrage
        net_port_r = value / value_before_period - 1.0

        # Sauvegarde ( date, valeur, rendement net de la période )
        out.append((dt, value, net_port_r))

    # Construction d'un DataFrame résultat
    res = pd.DataFrame(out, columns=["Date", "value", "ret"]).set_index("Date")
    return res
