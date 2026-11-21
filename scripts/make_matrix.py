"""Detection map: flag level reached vs droop depth and width (Gaussian droops, post-layout, TT 27 C)."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.labelsize": 8,
                     "xtick.labelsize": 7, "ytick.labelsize": 7,
                     "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02})
R = json.load(open("matrix2_res.json"))
dep = [0.025, 0.05, 0.0625, 0.075, 0.10, 0.1125, 0.125, 0.15]; fw = [1, 2, 4, 8, 12]
exp_lvl = {0.025: 0, 0.05: 1, 0.0625: 1, 0.075: 1, 0.10: 2, 0.1125: 2, 0.125: 2, 0.15: 3}
# 0 correct, 1 under-graded, 2 missed, 3 over-graded
cmap = ListedColormap(["#4caf50", "#ffb74d", "#e57373", "#64b5f6"])
fig, axs = plt.subplots(1, 2, figsize=(3.45, 2.25), sharey=True)
for ax, pre, title in [(axs[0], "DVM", "DVM"), (axs[1], "CAL", "TAP_CAL")]:
    M = np.zeros((8, 5)); L = np.zeros((8, 5), int)
    for r in R:
        i, j = dep.index(r["depth"]), fw.index(r["fwhm"])
        got, e = r[pre], exp_lvl[r["depth"]]
        L[i, j] = got
        M[i, j] = 0 if got == e else (2 if got == 0 else (1 if got < e else 3))
    ax.imshow(M, cmap=cmap, vmin=-0.5, vmax=3.5, origin="lower", aspect="auto")
    for i in range(8):
        for j in range(5):
            ax.text(j, i, str(L[i, j]), ha="center", va="center", fontsize=7)
    ax.set_xticks(range(5)); ax.set_xticklabels([str(f) for f in fw])
    ax.set_xlabel("Droop FWHM (ns)"); ax.set_title(title, fontsize=8)
    ax.set_xticks(np.arange(-0.5, 5), minor=True); ax.set_yticks(np.arange(-0.5, 8), minor=True)
    ax.grid(which="minor", color="white", lw=1); ax.tick_params(which="minor", length=0)
axs[0].set_yticks(range(8)); axs[0].set_yticklabels([f"{d*100:g}% ({exp_lvl[d]})" for d in dep])
axs[0].set_ylabel("Depth (expected level)")
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=c, label=l) for c, l in zip(cmap.colors[:3], ["correct", "under-graded", "missed"])],
           loc="lower center", ncol=3, fontsize=6.5, frameon=False, bbox_to_anchor=(0.55, 0.0))
fig.tight_layout(w_pad=0.4, rect=(0, 0.07, 1, 1))
fig.savefig("fig_matrix.pdf"); fig.savefig("fig_matrix.png", dpi=220)
