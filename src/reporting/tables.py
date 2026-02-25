import os
import pandas as pd

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def export_summary_table(summary_dict, outdir):
    ensure_dir(outdir)
    path = os.path.join(outdir, "table_summary.csv")
    df = pd.DataFrame(summary_dict, index=["Value"]).T
    df.to_csv(path)
    print("Saved:", os.path.abspath(path))

def export_monthly_table(monthly_rets, outdir):
    ensure_dir(outdir)
    path = os.path.join(outdir, "table_monthly_returns.csv")
    monthly_rets.to_csv(path)
    print("Saved:", os.path.abspath(path))