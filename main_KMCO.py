# main.py

from src.loader import load_prices_csv
from src.returns import calc_simple_returns
from src.engine import backtest_portfolio
from pathlib import Path

from src.reporting.charts import plot_nav, plot_drawdown, plot_monthly_returns
from src.reporting.tables import export_summary_table, export_monthly_table

# Metrics (tout est déjà dans src/metrics.py chez toi)
from src.metrics import (
    total_return, cagr, annualized_return,
    annualized_vol, downside_vol,
    sharpe_ratio, sortino_ratio, calmar_ratio,
    max_drawdown, average_drawdown, ulcer_index,
    max_drawdown_duration, max_recovery_duration,
    hit_ratio, best_worst, skewness, kurtosis,
    var_95, cvar_95, win_loss_ratio, expectancy,
    max_dd_info,
)

# -----------------------
# FORMATTERS (AFFICHAGE)
# -----------------------

def fmt_pct(x: float) -> str:
    return f"{x*100:>7.2f}%"

def fmt_num(x: float) -> str:
    return f"{x:>7.3f}"

def fmt_int(x: int) -> str:
    return f"{x:>7d}"

def fmt_date(x) -> str:
    return str(x.date()) if hasattr(x, "date") else str(x)

def print_block(title: str, rows: list[tuple[str, str]]):
    print(f"\n{title}")
    print("-" * len(title))
    for k, v in rows:
        print(f"{k:<32} {v}")


# -----------------------
# PARAMÈTRES BACKTEST
# -----------------------

periods = 252     # daily
rf = 0.0          # taux sans risque annualisé
tc_bps = 5.0      # coûts (bps) sur turnover
rebalance_freq = "Q"

weights = {
    "WORLD": 0.1778,
    "WQDV": 0.0889,
    "IMEU": 0.1111,
    "ASIA": 0.0667,
    "IBGS": 0.1111,
    "IBTS": 0.1111,
    "TIP5": 0.1111,
    "GOLD": 0.1111,
    "REIT": 0.1111,
}

# -----------------------
# PIPELINE
# -----------------------

prices = load_prices_csv("data/prices_kmco.csv")
returns = calc_simple_returns(prices)

res = backtest_portfolio(
    returns=returns,
    target_weights=weights,
    rebalance_freq=rebalance_freq,
    tc_bps=tc_bps,
    start_value=100.0,
)

# Returns portefeuille (nettoyés)
rets = res["ret"].dropna()
val = res["value"].dropna()


best, worst = best_worst(rets)
dd_info = max_dd_info(val)

start_date = val.index[0]
end_date = val.index[-1]
years_obs = len(val) / periods
final_nav = float(val.iloc[-1])

# -----------------------
# METRICS (CALCUL)
# -----------------------

stats = {
    # Contexte
    "Start Date": start_date,
    "End Date": end_date,
    "Years (obs/252)": years_obs,
    "Final NAV": final_nav,

    # Performance
    "Total Return": total_return(val),
    "CAGR": cagr(val, periods),
    "Annualized Return (mean)": annualized_return(rets, periods),

    # Risque / DD
    "Volatility": annualized_vol(rets, periods),
    "Downside Vol": downside_vol(rets, periods),
    "Max Drawdown": max_drawdown(val),
    "Average Drawdown": average_drawdown(val),
    "Ulcer Index": ulcer_index(val),

    # Ratios ajustés risque
    "Sharpe": sharpe_ratio(rets, rf, periods),
    "Sortino": sortino_ratio(rets, rf, periods),
    "Calmar": calmar_ratio(val, rets, periods),

    # Timing DD (en observations; daily ≈ jours de bourse)
    "Max DD Duration (obs)": max_drawdown_duration(val),
    "Max Recovery Duration (obs)": max_recovery_duration(val),

    # Path / régularité
    "Hit Ratio": hit_ratio(rets),
    "Win/Loss Ratio": win_loss_ratio(rets),
    "Expectancy (per period)": expectancy(rets),

    # Stress / queues
    "VaR 95% (per period)": var_95(rets),
    "CVaR 95% (per period)": cvar_95(rets),
    "Best Period": best,
    "Worst Period": worst,
    "Skewness": skewness(rets),
    "Kurtosis": kurtosis(rets),

    # Infos max DD (dates)
    "MaxDD Peak Date": dd_info["Peak"],
    "MaxDD Trough Date": dd_info["Trough"],
}

# -----------------------
# PRINT (REPORT TERMINAL)
# -----------------------

print("\n" + "=" * 62)
print("KM&CO — Portfolio Backtest Summary")
print("=" * 62)

print_block("Context", [
    ("Start Date", fmt_date(stats["Start Date"])),
    ("End Date", fmt_date(stats["End Date"])),
    ("Years (obs/252)", fmt_num(stats["Years (obs/252)"])),
    ("Final NAV (start=100)", fmt_num(stats["Final NAV"])),
])

print_block("Performance", [
    ("Total Return", fmt_pct(stats["Total Return"])),
    ("CAGR", fmt_pct(stats["CAGR"])),
    ("Annualized Return (mean)", fmt_pct(stats["Annualized Return (mean)"])),
])

print_block("Risk / Drawdown", [
    ("Volatility", fmt_pct(stats["Volatility"])),
    ("Downside Volatility", fmt_pct(stats["Downside Vol"])),
    ("Max Drawdown", fmt_pct(stats["Max Drawdown"])),
    ("Average Drawdown", fmt_pct(stats["Average Drawdown"])),
    ("Ulcer Index (RMS DD)", fmt_num(stats["Ulcer Index"])),
])

print_block("Risk-adjusted ratios", [
    ("Sharpe (mean/vol)", fmt_num(stats["Sharpe"])),
    ("Sortino (mean/downside)", fmt_num(stats["Sortino"])),
    ("Calmar (CAGR/|MaxDD|)", fmt_num(stats["Calmar"])),
])

print_block("Behaviour / path feel", [
    ("Hit Ratio (% positive periods)", fmt_pct(stats["Hit Ratio"])),
    ("Win/Loss Ratio (avg win / avg loss)", fmt_num(stats["Win/Loss Ratio"])),
    ("Expectancy (per period)", fmt_pct(stats["Expectancy (per period)"])),
    ("Best Period", fmt_pct(stats["Best Period"])),
    ("Worst Period", fmt_pct(stats["Worst Period"])),
])

print_block("Drawdown timing", [
    ("Max DD Duration (obs)", fmt_int(int(stats["Max DD Duration (obs)"]))),
    ("Max Recovery Duration (obs)", fmt_int(int(stats["Max Recovery Duration (obs)"]))),
    ("MaxDD Peak Date", fmt_date(stats["MaxDD Peak Date"])),
    ("MaxDD Trough Date", fmt_date(stats["MaxDD Trough Date"])),
])

print_block("Tail / distribution", [
    ("VaR 95% (5% quantile)", fmt_pct(stats["VaR 95% (per period)"])),
    ("CVaR 95% (mean tail)", fmt_pct(stats["CVaR 95% (per period)"])),
    ("Skewness (asymmetry)", fmt_num(stats["Skewness"])),
    ("Kurtosis (fat tails)", fmt_num(stats["Kurtosis"])),
])

print("\nAllocation cible")
print("--------------")
for k, w in weights.items():
    print(f"{k:<10} {w*100:>6.2f}%")

# -----------------------
# REPORTING (FIGURES/TABLES)
# -----------------------

reports_fig = "reports/figures"
reports_tab = "reports/tables"

# NAV = val, Returns = rets (déjà calculés plus haut)
drawdown = (val / val.cummax()) - 1

# Rendements mensuels (correct : produit, pas somme)
monthly_rets = (1 + rets).resample("M").prod() - 1

# Summary table (valeurs numériques finales, pas fonctions)
summary = {
    "Total Return": float(stats["Total Return"]),
    "CAGR": float(stats["CAGR"]),
    "Volatility": float(stats["Volatility"]),
    "Sharpe": float(stats["Sharpe"]),
    "Max Drawdown": float(stats["Max Drawdown"]),
}

# Plots
plot_nav(val, reports_fig)
plot_drawdown(drawdown, reports_fig)
plot_monthly_returns(monthly_rets, reports_fig)

# Tables
export_summary_table(summary, reports_tab)
export_monthly_table(monthly_rets, reports_tab)
BASE_DIR = Path(__file__).resolve().parent
reports_fig = str(BASE_DIR / "reports" / "figures")
reports_tab = str(BASE_DIR / "reports" / "tables")

# -----------------------
# NOTES (INTERPRÉTATION COURTE)
# -----------------------
# Total Return : performance cumulée sur toute la période.
# CAGR : performance annualisée géométrique (croissance composée).
# Annualized Return (mean) : moyenne arithmétique annualisée (espérance).
# Volatility : dispersion des returns (risque global).
# Downside Vol : volatilité calculée uniquement sur returns négatifs (risque de baisse).
# Sharpe : rendement excédentaire / vol (efficacité rendement/risque symétrique).
# Sortino : rendement excédentaire / downside vol (pénalise seulement les baisses).
# Calmar : CAGR / |MaxDD| (rendement relatif au pire stress historique).
# Max Drawdown : pire baisse peak-to-trough observée.
# Average Drawdown : drawdown moyen (douleur moyenne).
# Ulcer Index : RMS des drawdowns (profondeur + durée), très pertinent pour profils prudents.
# DD Duration : durée max passée sous un peak (temps “sous l’eau”).
# Recovery Duration : durée max pour refaire un nouveau peak (patience nécessaire).
# Hit Ratio : % de périodes positives (régularité).
# Win/Loss Ratio : moyenne gains / moyenne pertes (qualité asymétrie).
# Expectancy : gain moyen par période (P(win)*AvgWin + P(loss)*AvgLoss).
# VaR 95% : perte seuil à 5% (perte typique de queue).
# CVaR 95% : perte moyenne conditionnelle dans la queue (gravité des queues).
# Skewness : asymétrie (négatif = crashes plus probables).
# Kurtosis : épaisseur des queues (>3 = fat tails).