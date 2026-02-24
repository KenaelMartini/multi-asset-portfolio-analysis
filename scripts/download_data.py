import yfinance as yf
import pandas as pd
from pathlib import Path

tickers = {
    "WORLD": "IWDA.AS",
    "EM": "IEMA.AS",
    "BONDS": "AGGH.AS",
    "MM": "XEON.DE",
}

start = "2010-01-01"
end = "2026-02-18"

raw = yf.download(
    list(tickers.values()),
    start=start,
    end=end,
    auto_adjust=False,   # important pour contrôler les colonnes
    progress=True
)

print("Colonnes disponibles :", raw.columns)

# 🔎 Sélection propre
if "Adj Close" in raw.columns:
    data = raw["Adj Close"]

elif "Close" in raw.columns:
    print("⚠ Adj Close absent → fallback sur Close")
    data = raw["Close"]

else:
    raise ValueError("Ni 'Adj Close' ni 'Close' trouvés dans les données.")

# Renommage colonnes
data.columns = tickers.keys()

data = data.dropna(how="all")

out_path = Path("data/prices.csv")
out_path.parent.mkdir(parents=True, exist_ok=True)

data.to_csv(out_path)

print("CSV généré :", out_path)
