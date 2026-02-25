import os
import matplotlib.pyplot as plt

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def plot_nav(nav, outdir):
    ensure_dir(outdir)
    figpath = os.path.join(outdir, "fig_nav.png")
    plt.figure()
    nav.plot()
    plt.title("Portfolio NAV (Base 100)")
    plt.ylabel("NAV")
    plt.xlabel("Date")
    plt.savefig(figpath, dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved:", os.path.abspath(figpath))

def plot_drawdown(drawdown, outdir):
    ensure_dir(outdir)
    figpath = os.path.join(outdir, "fig_drawdown.png")
    plt.figure()
    drawdown.plot()
    plt.title("Drawdown (Underwater)")
    plt.ylabel("Drawdown")
    plt.xlabel("Date")
    plt.savefig(figpath, dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved:", os.path.abspath(figpath))

def plot_monthly_returns(monthly_rets, outdir):
    ensure_dir(outdir)
    figpath = os.path.join(outdir, "fig_monthly_returns.png")
    plt.figure()
    monthly_rets.plot(kind="bar")
    plt.title("Monthly Returns")
    plt.ylabel("Return")
    plt.xlabel("Month")
    plt.savefig(figpath, dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved:", os.path.abspath(figpath))