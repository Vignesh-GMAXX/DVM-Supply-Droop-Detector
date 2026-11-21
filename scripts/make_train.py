"""Droop-train figure: 6 smooth droops of different depth/width in one post-layout run.
Usage: python3 make_train.py TRAIN_tt27.csv [TRAIN_ff125.csv]"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "axes.labelsize": 8,
    "legend.fontsize": 6.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "axes.grid": True, "grid.alpha": 0.3, "lines.linewidth": 1.0,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})

EV = [(18.8, 5, "sym."), (41.9, 10, "fast fall"), (73.2, 10, "wide"), (98.3, 15, "fast fall"), (128.5, 15, "sym."), (160.1, 5, "wide")]
WIN = [(10, 32), (32, 57), (57, 89), (89, 115), (115, 142), (142, 178)]
TARGET = [1, 2, 2, 3, 3, 1]


def load(p):
    d = pd.read_csv(p)
    S = {}
    for i in range(0, len(d.columns), 2):
        n = d.columns[i].split(" ")[0].lstrip("/")
        S[n] = (d.iloc[:, i].dropna().values * 1e9, d.iloc[:, i + 1].dropna().values)
    return S


def level(S, pre, lo, hi):
    return sum(int(S[f"{pre}_O<{k}>"][1][(S[f"{pre}_O<{k}>"][0] >= lo) & (S[f"{pre}_O<{k}>"][0] <= hi)].max() > 0.5)
               for k in range(3))


files = sys.argv[1:]
labels = [("ff, 125 °C, S=01" if "ff" in f.lower() else "tt, 125 °C, S=10" if "tt125" in f.lower() else "tt, 27 °C, S=00") for f in files]
fig, axs = plt.subplots(3, len(files), figsize=(7.1 if len(files) == 1 else 7.1, 3.3),
                        sharex=True, squeeze=False, gridspec_kw=dict(height_ratios=[1.3, 1, 1]))
for c, (f, lab) in enumerate(zip(files, labels)):
    S = load(f)
    t, v = S["VDD_DVM"]
    ax = axs[0, c]
    ax.plot(t, v, color="C4")
    for k, (tc, a, w) in enumerate(EV):
        ax.text(tc, 1.0 - 1.08 * a / 100 - 0.008, f"E{k+1}\n{a}%, {w}", ha="center", va="top", fontsize=5.6)
    ax.set_ylim(0.765, 1.015); ax.set_ylabel(r"$V_{DD,DVM}$ (V)")
    ax.set_title(lab, fontsize=8)
    for r, pre, name in [(1, "DVM", "DVM"), (2, "CAL", "TAP_CAL")]:
        ax = axs[r, c]
        for k, col in zip(range(3), ["C0", "C1", "C3"]):
            tt, y = S[f"{pre}_O<{k}>"]
            ax.plot(tt, (y > 0.5) * 0.8 + k, color=col, lw=0.9, label=f"flag{k} ({5*(k+1)}%)")
        for k, (lo, hi) in enumerate(WIN):
            got = level(S, pre, lo, hi)
            ok = got == TARGET[k]
            ax.text(EV[k][0], 3.05, f"{got}/{TARGET[k]}", ha="center", va="bottom", fontsize=6,
                    color="k" if ok else "C3", fontweight="normal" if ok else "bold")
        ax.set_yticks([0.4, 1.4, 2.4]); ax.set_yticklabels(["5%", "10%", "15%"]); ax.set_ylim(-0.15, 3.6)
        ax.set_ylabel(f"{name} flag")
        ax.grid(axis="y", alpha=0)
    axs[2, c].set_xlabel("Time (ns)")
    axs[2, c].set_xlim(5, 178)
fig.tight_layout(h_pad=0.3)
fig.savefig("fig_train.pdf"); fig.savefig("fig_train.png", dpi=200)
