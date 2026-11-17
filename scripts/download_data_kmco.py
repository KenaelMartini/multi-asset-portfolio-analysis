import yfinance as yf
import pandas as pd
from pathlib import Path

# Allocation exacte (tickers Yahoo Finance) — proxies UCITS Europe quand possible
# IMPORTANT : certains tickers peuvent varier selon la place (AS/DE/L). Si un ticker échoue,
# on remplacera par un équivalent coté sur une autre place.
tickers = {
    "WORLD": "IWDA.AS",     # iShares Core MSCI World UCITS
    "WQDV": "WQDV.L",       # iShares MSCI World Quality Dividend UCITS (souvent coté LSE)
    "IMEU": "IMEU.L",       # iShares Core MSCI Europe UCITS (souvent coté LSE)
    "ASIA": "CPJ1.L",       # Proxy Asia Pac ex-Japan (à défaut, on ajustera si indisponible)
    "IBGS": "IBGS.L",       # iShares Euro Govt Bond 1-5yr UCITS
    "IBTS": "IBTS.L",       # iShares $ Treasury Bond 1-5yr UCITS
    "TIP5": "TIP5.L",       # iShares $ TIPS 0-5 UCITS (si indisponible, fallback)
    "GOLD": "SGLN.L",       # iShares Physical Gold ETC (ticker souvent SGLN.L)
    "REIT": "VNQ",          # Vanguard US Real Estate ETF (US)
}

start = "2010-01-01"
end = "2026-02-24"

raw = yf.download(
    list(tickers.values()),
    start=start,
    end=end,
    auto_adjust=False,
    progress=True,
)

# Debug : affiche la structure
print("Colonnes disponibles :", raw.columns)

# Sélection prix
if "Adj Close" in raw.columns:
    data = raw["Adj Close"]
elif "Close" in raw.columns:
    print("⚠ Adj Close absent → fallback sur Close")
    data = raw["Close"]
else:
    raise ValueError("Ni 'Adj Close' ni 'Close' trouvés dans les données.")

# Association explicite des colonnes Yahoo aux actifs du portefeuille.
# Ne pas renommer par position : Yahoo peut trier les tickers différemment.
ticker_to_asset = {ticker: asset for asset, ticker in tickers.items()}
if data.columns.has_duplicates:
    raise ValueError("Colonnes de prix Yahoo dupliquées.")

missing = [ticker for ticker in tickers.values() if ticker not in data.columns]
if missing:
    raise ValueError(f"Tickers absents du téléchargement : {missing}")

data = data.loc[:, list(tickers.values())].rename(columns=ticker_to_asset)
data = data.reindex(columns=list(tickers.keys()))

# Audit de couverture AVANT la sélection de l'historique commun.
print("Couverture des données par actif (avant alignement) :")
for asset in data.columns:
    valid = data[asset].dropna()
    if valid.empty:
        raise ValueError(f"Aucune donnée disponible pour {asset}")
    print(f"  {asset}: {valid.index[0].date()} -> {valid.index[-1].date()} ({len(valid)} observations)")

# Dates communes aux neuf actifs : aucune date ni prix futur n'est injecté.
aligned = data.dropna(how="any")
if aligned.empty:
    raise ValueError("Aucune date commune aux neuf actifs.")

common_window = data.loc[aligned.index.min():aligned.index.max()]
excluded_dates = len(common_window) - len(aligned)
print(f"Dates exclues dans la fenêtre commune (calendriers/données manquantes) : {excluded_dates}")
if excluded_dates:
    print("Attention : les rendements successifs peuvent couvrir plusieurs jours calendaires.")

data = aligned

# Écriture
out_path = Path("data/prices_kmco.csv")
out_path.parent.mkdir(parents=True, exist_ok=True)
data.to_csv(out_path)

print("CSV généré :", out_path)
print("Start/End effectifs :", data.index.min().date(), "→", data.index.max().date())
print("Nb lignes :", len(data))
