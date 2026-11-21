"""Droop-train figure: (a) v3 train at tt 27 C, (b) exact-depth v4 train at ff 125 C.
Each block: supply + flag level (0-3) of DVM and TAP_CAL."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
exec(open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "make_train.py")).read().split("files = sys.argv")[0])

TARGET = [1, 2, 2, 3, 3, 1]
V3 = dict(EV=[(18.8, 5, "sym."), (41.9, 10, "fast fall"), (73.2, 10, "wide"), (98.3, 15, "fast fall"), (128.5, 15, "sym."), (160.1, 5, "wide")],
          WIN=[(10, 32), (32, 57), (57, 89), (89, 115), (115, 142), (142, 178)],
          HOLD=[(16.5, 21.1), (40.4, 44.9), (70.2, 76.2), (97.0, 101.5), (126.0, 131.0), (156.6, 163.6)],
          Q=(28, 34), pk=1.08, stop=178)
_c = [(20.5, 6.0, 6.0), (47.3, 4.2, 7.8), (83.8, 8.0, 8.0), (113.0, 3.6, 8.4), (148.1, 6.6, 6.6), (184.8, 9.3, 9.3)]
V4 = dict(EV=[(c, a, s) for (c, _, _), (_, a, s) in zip(_c, V3["EV"])],
          WIN=[(10, 38), (38, 70), (70, 105), (105, 135), (135, 170), (170, 206)],
          HOLD=[(c - 0.3765 * wf, c + 0.3765 * wr) for c, wf, wr in _c],
          Q=(32, 40), pk=1.0, stop=206)


def lvl_trace(S, pre):
    t = S[f"{pre}_O<0>"][0]
    return t, sum((np.interp(t, *S[f"{pre}_O<{k}>"]) > 0.5).astype(int) for k in range(3))


def block(axv, axl, S, P, lab, tag):
    axv.plot(*S["VDD_DVM"], color="C4")
    for k, (tc, a, w) in enumerate(P["EV"]):
        axv.text(tc, 1.0 - P["pk"] * a / 100 - 0.008, f"E{k+1}: {a}%, {w}", ha="center", va="top", fontsize=6)
    axv.set_ylim(0.79, 1.015); axv.set_ylabel(r"$V_{DD}$ (V)")
    axv.set_xlim(5, P["stop"])
    axv.text(0.003, 0.08, tag, transform=axv.transAxes, fontsize=7, fontweight="bold")
    for (h0, h1), tg in zip(P["HOLD"], TARGET):
        axl.plot([h0, h1], [tg, tg], color="0.6", lw=4, alpha=0.5, solid_capstyle="butt")
    t, y = lvl_trace(S, "DVM"); axl.step(t, y + 0.06, where="post", color="C0", lw=1.0, label="DVM")
    t, y = lvl_trace(S, "CAL"); axl.step(t, y - 0.06, where="post", color="C3", lw=1.0, label="TAP_CAL")
    tq, yq = lvl_trace(S, "DVM"); base = int(yq[(tq >= P["Q"][0]) & (tq <= P["Q"][1])].max())
    if base:
        axl.text(np.mean(P["Q"]) + 6, base + 0.12, f"DVM false alarm: level {base} with no droop",
                 fontsize=5.8, ha="center", va="bottom", color="C0")
    for k, (lo, hi) in enumerate(P["WIN"]):
        d, c = level(S, "DVM", lo, hi), level(S, "CAL", lo, hi)
        okd, okc = (d == TARGET[k] and base == 0), c == TARGET[k]
        x = P["EV"][k][0]
        axl.text(x - 0.6, 3.25, f"{d}", ha="right", va="bottom", fontsize=6, color="C0" if okd else "k",
                 fontweight="normal" if okd else "bold")
        axl.text(x, 3.25, "/", ha="center", va="bottom", fontsize=6)
        axl.text(x + 0.6, 3.25, f"{c}", ha="left", va="bottom", fontsize=6, color="C3" if okc else "k",
                 fontweight="normal" if okc else "bold")
    axl.set_ylim(-0.3, 3.9); axl.set_yticks([0, 1, 2, 3]); axl.grid(axis="y", alpha=0.25)
    axl.set_ylabel(lab + "\nlevel", fontsize=6.5); axl.set_xlim(5, P["stop"])
    axl.set_xlabel("Time (ns)")


fig, axs = plt.subplots(4, 1, figsize=(7.1, 3.5), gridspec_kw=dict(height_ratios=[1.05, 1, 1.05, 1]))
block(axs[0], axs[1], load(sys.argv[1]), V3, "tt, 27 °C\nS=00", "(a)")
block(axs[2], axs[3], load(sys.argv[2]), V4, "ff, 125 °C\nS=01", "(b)")
axs[0].set_xticklabels([]); axs[2].set_xticklabels([]); axs[1].set_xlabel("")
axs[1].legend(loc="upper right", bbox_to_anchor=(1.0, 0.82), fontsize=6, frameon=True, framealpha=0.9, ncol=2)
fig.tight_layout(h_pad=0.2)
fig.savefig("fig_train.pdf"); fig.savefig("fig_train.png", dpi=200)
for nm, f, P in [("tt27", sys.argv[1], V3), ("ff125", sys.argv[2], V4)]:
    S = load(f); print(nm, [(level(S, "DVM", lo, hi), level(S, "CAL", lo, hi)) for lo, hi in P["WIN"]])
