"""Monte Carlo distribution figure (schematic, 1 GHz, T=11, TT 27 C, no droop).
M1 = global + mismatch (100 samples), M2 = mismatch only (overlaid if present)."""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "axes.labelsize": 8,
    "legend.fontsize": 6.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "axes.grid": True, "grid.alpha": 0.3, "lines.linewidth": 1.1,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})

D = sys.argv[1] if len(sys.argv) > 1 else "../mcdata"


def load(name):
    p = os.path.join(D, name)
    if not os.path.exists(p):
        return None
    d = pd.read_csv(p).dropna(subset=["code_nom"])
    d["clk"] = d.t_clk2div + d.t_buf
    return d


m1, m2 = load("M1_100_samples.csv"), load("M2_100_samples.csv")
runs = [(m1, "M1 global+mismatch", "C0")] + ([(m2, "M2 mismatch only", "C3")] if m2 is not None else [])


def gauss(ax, x, scale, col):
    mu, sd = x.mean(), x.std(ddof=1)
    xs = np.linspace(mu - 4 * sd, mu + 4 * sd, 200)
    ax.plot(xs, scale * np.exp(-0.5 * ((xs - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi)),
            "--", color=col, lw=0.9)


fig, axs = plt.subplots(2, 3, figsize=(7.1, 3.0))
ax = axs[0, 0]
# (a) code histogram with flag thresholds
w = 0.38 if m2 is not None else 0.7
for k, (d, lab, col) in enumerate(runs):
    vals, cnt = np.unique(d.code_nom, return_counts=True)
    off = (k - (len(runs) - 1) / 2) * w
    ax.bar(vals + off, cnt, width=w, color=col, alpha=0.8, label=lab.split()[0])
    gauss(ax, d.code_nom.astype(float), len(d), col)
ax.axvspan(10, 16.5, color="C1", alpha=0.12)
ax.axvline(16.5, color="C1", ls="--", lw=0.9)
ax.text(15.0, ax.get_ylim()[1] * 0.45, "flag0\nfires\n($\\leq$16)", color="C1",
        fontsize=6, ha="center", va="center")
txt = []
for d, lab, _ in runs:
    mu, sd = d.code_nom.mean(), d.code_nom.std(ddof=1)
    txt.append(f"{lab.split()[0]}: {mu:.2f}$\\pm${sd:.2f} ({(mu-16.5)/sd:.1f}$\\sigma$)")
ax.text(0.98, 0.95, "\n".join(txt), transform=ax.transAxes, ha="right", va="top", fontsize=6)
ax.set_ylim(0, ax.get_ylim()[1] * 1.3); ax.set_xlim(13.5, 27.5); ax.set_xticks(range(14, 28, 2)); ax.set_xlabel("TDC code (no droop)"); ax.set_ylabel("Samples")
ax.set_title("(a) Code", fontsize=8)

panels = [(axs[0, 1], "t_TRC", 1e12, r"$t_{TRC}$ (ps)", "(b) Replica delay"),
          (axs[0, 2], "t_stage_post", 1e12, r"$t_s$ (ps)", "(c) TDC stage delay"),
          (axs[1, 0], "clk", 1e12, r"$t_{clk2div}+t_{buf}$ (ps)", "(d) Clock path"),
          (axs[1, 1], "P_mc", 1e6, r"$P_{act}$ ($\mu$W)", "(e) Active power")]
for ax, col_name, sc, xl, title in panels:
    allx = np.concatenate([d[col_name].values * sc for d, _, _ in runs])
    bins = np.linspace(allx.min(), allx.max(), 16)
    bw = bins[1] - bins[0]
    txt = []
    for d, lab, col in runs:
        x = d[col_name] * sc
        ax.hist(x, bins=bins, color=col, alpha=0.55 if len(runs) > 1 else 0.8,
                edgecolor="white", lw=0.3, label=lab.split()[0])
        gauss(ax, x, len(x) * bw, col)
        txt.append(f"{lab.split()[0]}: {x.mean():.1f}$\\pm${x.std(ddof=1):.2f}")
    ax.text(0.98, 0.95, "\n".join(txt), transform=ax.transAxes, ha="right", va="top", fontsize=6)
    ax.set_xlabel(xl); ax.set_title(title, fontsize=8)
axs[1, 0].set_ylabel("Samples"); axs[0, 1].set_ylabel("")

# (f) code vs total delay: code follows the delay equation sample by sample
ax = axs[1, 2]
for d, lab, col in runs:
    x = (d.t_TRC + d.clk) * 1e12
    jit = np.random.default_rng(1).uniform(-0.15, 0.15, len(d))
    ax.plot(x, d.code_nom + jit, "o", ms=2.2, color=col, alpha=0.7, mec="none", label=lab.split()[0])
xx = (m1.t_TRC + m1.clk).values
r = np.corrcoef(xx, m1.code_nom)[0, 1]
p = np.polyfit(xx * 1e12, m1.code_nom, 1)
xs = np.linspace(xx.min() * 1e12, xx.max() * 1e12, 50)
ax.plot(xs, np.polyval(p, xs), "k-", lw=0.8)
ax.text(0.98, 0.95, f"M1: r = {r:.2f}",
        transform=ax.transAxes, ha="right", va="top", fontsize=6)
ax.set_xlabel(r"$t_{TRC}+t_{clk2div}+t_{buf}$ (ps)"); ax.set_ylabel("Code")
ax.set_title("(f) Code vs. edge delay", fontsize=8)

if m2 is not None:
    axs[0, 0].legend(loc="center right", frameon=False)
fig.tight_layout(w_pad=0.6, h_pad=0.6)
fig.savefig("fig_mc.pdf"); fig.savefig("fig_mc.png", dpi=200)
plt.close(fig)

# summary numbers for the table
for d, lab, _ in runs:
    print(lab, len(d), "samples")
    for c, s in [("code_nom", 1), ("t_TRC", 1e12), ("t_stage_post", 1e12), ("clk", 1e12),
                 ("tr_clkdiv_b", 1e12), ("P_mc", 1e6)]:
        x = d[c] * s
        print(f"  {c:13s} mu={x.mean():8.3f} sd={x.std(ddof=1):7.3f} min={x.min():8.2f} max={x.max():8.2f}")
    print("  max flag level (V):", d[["mflag0", "mflag1", "mflag2", "mcal0"]].max().max())
    print("  yield:", ((d[["mflag0", "mflag1", "mflag2"]] < 0.5).all(axis=1)).mean() * 100, "%")
if m2 is not None:
    for c in ["code_nom", "t_TRC", "t_stage_post", "clk", "P_mc"]:
        print(f"  global share {c}: {100*(1-m2[c].var()/m1[c].var()):.1f}%")
