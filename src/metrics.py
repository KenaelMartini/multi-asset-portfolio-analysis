import numpy as np
import pandas as pd

def max_drawdown(value: pd.Series) -> float:
    """
    Max drawdown (MDD) sur une série de valeur.
    
    Définition :
    - peak_t = max(value_0..value_t)
    - drawdown_t = value_t / peak_t - 1
    - max drawdown = min(drawdown_t)
    
    Retout
    -------
    float 
        Valeur négative ( ex: -0.18 = -18% )
    """

    # Pic cumulatif
    peak = value.cummax()

    # Drawdown instantané
    dd = value / peak - 1

    # Maximum drawdown = minimum de la série dd
    return float(dd.min())

def annualized_vol(returns: pd.Series, periods: int = 252) -> float:
    """
    Valatilité annualisée
    
    vol_ann = std(returns) * sqrt(periods)
    
    periods = 252 pour daily, 52 pour weakly, 12 pour monthly.
    """
    return float(returns.std(ddof=1) * np.sqrt(periods))

def cagr(value: pd.Series, periods: int = 252) -> float:
    """
    CAGR ( taux de croissance annuealisé ) a partir d'une courbe de valeur.
    
    CAGR = ( V_end / V_start ) ** ( periods / n_obs ) - 1
    """

    if len(value) < 2:
        return np.nan
    
    v0 = float(value.iloc[0])
    v1 = float(value.iloc[-1])

    if v0 <= 0:
        return np.nan
    
    n = len(value)
    return (v1 / v0) ** (periods / n) - 1.0

def sharpe_ratio(returns: pd.Series, rf: float = 0.0, periods: int = 252) -> float:
    """
    Sharpe ratio annualisé.
    
    Approche simple :
    - mean_ann = mean(returns) * periods
    - vol_ann = std(returns) * sqrt(periods)
    - sharpe = (mean_ann - rf ) / vol_ann
    
    rf = taux sans risque annualisé ( ex : 0.02 pour 2% )
    """

    mean_ann = float(returns.mean() * periods)
    vol_ann = annualized_vol(returns, periods)

    if vol_ann == 0:
        return np.nan
    
    return (mean_ann - rf) / vol_ann

def perf_stats(res: pd.DataFrame, periods: int = 252, rf: float = 0.0) -> dict:
    """
    Agrège les stats principales d'un backtest.

    res doit contenir :
    - "value" : NAV
    - "ret"   : returns période

    Retour
    ------
    dict : métriques clés
    """
    rets = res["ret"].dropna()
    val = res["value"].dropna()

    stats = {
        "TotalReturn": float(total_return(val)),
        "CAGR": float(cagr(val, periods)),
        "Vol": float(annualized_vol(rets, periods)),
        "Sharpe": float(sharpe_ratio(rets, rf, periods)),
        "MaxDD": float(max_drawdown(val)),
        "MaxDD_Duration": int(max_drawdown_duration(val)),
        "MaxRecovery_Duration": int(max_recovery_duration(val)),
    }
    return stats


def total_return(value: pd.Series) -> float:
    """
    Perf rorale : V_end / V_start - 1
    """

    if len(value) < 2:
        return np.nan
    
    v0 = float(value.iloc[0])
    v1 = float(value.iloc[-1])
    if v0 <= 0:
        return np.nan
    return v1 / v0 - 1.0

def drawdown_series(value: pd.Series) -> pd.Series:
    """
    Série de drawdown : dd_t = value_t / peak_t - 1
    """

    peak = value.cummax()
    return value / peak - 1.0

def max_drawdown_duration(value: pd.Series) -> int:
    """
    Durée max ( en nombre d'observations ) passés en drawdown ( sous le dernier peak).
    Exemple : Daily -> nombre de jours de bourse.

    Retour : 
    - int (>=0)
    """

    v = value.dropna()

    if v.empty:
        return 0
    
    dd = drawdown_series(v)
    underwater = dd < 0 # True quand on est sous le peak

    # Longeur maximale de séquence de True
    max_len = 0
    cur_len = 0 
    for flag in underwater.values:
        if flag:
            cur_len += 1
            if cur_len > max_len:
                max_len = cur_len
        else:
            cur_len = 0
    return int(max_len)

def max_recovery_duration(value: pd.Series) -> int:
    """
    Durée max de recovery ( en observations ) :
    temps entre un nouveau peak et le moment ou il est récupéré.
    mesure la "patiencee" nécessaire.
    
    Retour :
    -int (>=0)
    """

    v = value.dropna()
    if v.empty:
        return 0 
    
    peak = v.cummax()

    # Un "peak" est atteint quand value == peak
    is_peak = (v == peak)

    last_peak_idx = None
    max_rec = 0

    for i, flag in enumerate(is_peak.values):
        if flag:
            # On vient de (re)faire un peak => fin d'une phase de recovery
            if last_peak_idx is not None:
                rec_len = i - last_peak_idx
                if rec_len > max_rec:
                    max_rec = rec_len
            last_peak_idx = i
    
    return int(max_rec)

def annualized_return(returns: pd.Series, periods: int = 252) -> float:
    """Rendement moyen annualisé."""
    return float(returns.mean() * periods)

def downside_vol(returns: pd.Series, periods: int = 252) -> float:
    """Volatilité négative uniquement."""
    downside = returns[returns < 0]
    return float(downside.std(ddof=1) * np.sqrt(periods))

def sortino_ratio(returns: pd.Series, rf: float = 0.0, periods: int = 252) -> float:
    """Sharpe asymétrique (downside risk)."""
    mean_ann = returns.mean() * periods
    dvol = downside_vol(returns, periods)
    if dvol == 0:
        return np.nan
    return float((mean_ann - rf) / dvol)

def average_drawdown(value: pd.Series) -> float:
    """Drawdown moyen."""
    dd = drawdown_series(value)
    return float(dd.mean())

def ulcer_index(value: pd.Series) -> float:
    """
    Mesure profondeur + durée des drawdowns.
    Plus pertinent que vol pour investisseurs prudents.
    """
    dd = drawdown_series(value)
    return float(np.sqrt((dd**2).mean()))

def skewness(returns: pd.Series) -> float:
    return float(returns.skew())

def kurtosis(returns: pd.Series) -> float:
    return float(returns.kurtosis())

def hit_ratio(returns: pd.Series) -> float:
    """% périodes positives."""
    return float((returns > 0).mean())

def best_worst(returns: pd.Series) -> tuple:
    return float(returns.max()), float(returns.min())

def calmar_ratio(value: pd.Series, returns: pd.Series, periods: int = 252) -> float:
    """CAGR / |MaxDD|."""
    c = cagr(value, periods)
    mdd = abs(max_drawdown(value))
    if mdd == 0:
        return np.nan
    return float(c / mdd)

def max_dd_info(value: pd.Series) -> dict:
    peak = value.cummax()
    dd = value / peak - 1

    trough = dd.idxmin()
    peak_date = value.loc[:trough].idxmax()

    return {
        "MaxDD": float(dd.min()),
        "Peak": peak_date,
        "Trough": trough,
    }

def win_loss_ratio(returns: pd.Series) -> float:
    wins = returns[returns > 0].mean()
    losses = abs(returns[returns < 0].mean())
    if losses == 0:
        return np.nan
    return float(wins / losses)

def expectancy(returns: pd.Series) -> float:
    win_prob = (returns > 0).mean()
    avg_win = returns[returns > 0].mean()
    avg_loss = returns[returns < 0].mean()
    return float(win_prob * avg_win + (1 - win_prob) * avg_loss)

def var_95(returns: pd.Series) -> float:
    return float(np.percentile(returns, 5))

def cvar_95(returns: pd.Series) -> float:
    var = np.percentile(returns, 5)
    tail_losses = returns[returns <= var]
    return float(tail_losses.mean())
