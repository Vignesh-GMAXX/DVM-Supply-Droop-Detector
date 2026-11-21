"""Fig. 3a: active power and no-droop flags through the design fixes (TT, 27 C, no droop).
Values logged from the ADE XL runs (0-V probe: DVM + test-bench clock path)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "axes.labelsize": 8,
    "legend.fontsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "axes.grid": True, "grid.alpha": 0.3, "lines.linewidth": 1.2,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})
W = 3.4  # single column width (in)
# ---------- 6. power/energy pre vs post bar ----------
labels = ["Sch.\nno buf\n1 GHz", "Ext.\nno buf\n1 GHz", "Sch.\nbuffer\n1 GHz", "Ext.\nbuffer\n1 GHz", "Ext.\nfinal\n800 MHz"]
P = [126.2, 203.0, 143.9, 223.5, 181.2]
flags = ["000", "110", "000", "100", "000"]
fig, ax = plt.subplots(figsize=(W, 1.8))
b = ax.bar(range(5), P, color=["C0", "C3", "C0", "C3", "C2"])
for i, (p, c) in enumerate(zip(P, flags)):
    ax.text(i, p + 4, f"{p:.0f} µW\nflags {c}", ha="center", fontsize=6)
ax.set_xticks(range(5)); ax.set_xticklabels(labels, fontsize=6)
ax.set_ylabel(r"$P_{active}$ (µW)"); ax.set_ylim(0, 270)
fig.savefig("fig_prepost.pdf"); fig.savefig("fig_prepost.png", dpi=200); plt.close(fig)
print("ok")
