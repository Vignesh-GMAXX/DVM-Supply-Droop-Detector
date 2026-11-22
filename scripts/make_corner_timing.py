"""Where the code comes from at each corner: stage delay, replica delay and clock path.

(a) TDC stage delay t_s, (b) replica delay t_TRC (with the trim T used at that corner) and the
clock path t_clk2div + t_buf, (c) the code predicted by eq. (1), code = (T_w - t_TRC) / t_s with
T_w = 1.278 ns (latch-enable high time measured at TT), against the simulated no-droop code.

Input  : corners/corners_droop_0_5pct.csv (vdroop = 0 block)      Output : fig_corner_timing.png / .pdf
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from adexl_table import read_corner_table

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.grid": True, "grid.alpha": 0.25,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.08})
meta, data = read_corner_table("corners_droop_0_5pct.csv")
D = data[0.0]
order = sorted(meta, key=lambda c: D["t_stage_post"][c])
lab = [f"{meta[c]['gpdk045.scs']} {meta[c]['temperature']}" for c in order]
ts = np.array([D["t_stage_post"][c] for c in order]) * 1e12
trc = np.array([D["t_TRC"][c] for c in order]) * 1e12
clk = np.array([D["t_clk2div"][c] + D["t_buf"][c] for c in order]) * 1e12
code = np.array([D["code_nom"][c] for c in order])
T = [f"{meta[c]['T1']}{meta[c]['T0']}" for c in order]
TW = 1278.0
pred = (TW - trc) / ts

temp_col = {"-40": "#1565c0", "27": "#2e7d32", "125": "#c62828"}
cols = [temp_col[meta[c]["temperature"]] for c in order]
y = np.arange(len(order))
fig, ax = plt.subplots(1, 3, figsize=(14, 5.2), gridspec_kw={"width_ratios": [1, 1.25, 1], "wspace": 0.35})

ax[0].barh(y, ts, color=cols)
for i, v in enumerate(ts):
    ax[0].text(v + 1, i, f"{v:.1f}", va="center", fontsize=8)
ax[0].set_yticks(y)
ax[0].set_yticklabels(lab)
ax[0].set_xlabel("TDC stage delay t_s (ps)")
ax[0].set_title("(a) Stage delay: 30 ps (ff -40) to 82 ps (ss 125)", loc="left", fontsize=10)
ax[0].set_xlim(0, 95)

h = 0.38
ax[1].barh(y - h / 2, trc, height=h, color="#6d4c41", label="t_TRC (replica)")
ax[1].barh(y + h / 2, clk, height=h, color="#90a4ae", label="t_clk2div + t_buf (clock path)")
for i, (a, b, t) in enumerate(zip(trc, clk, T)):
    ax[1].text(a + 6, i - h / 2, f"{a:.0f}  (T={t})", va="center", fontsize=7.5)
    ax[1].text(b + 6, i + h / 2, f"{b:.0f}", va="center", fontsize=7.5, color="#546e7a")
ax[1].set_yticks(y)
ax[1].set_yticklabels([])
ax[1].set_xlabel("delay (ps)")
ax[1].set_xlim(0, 760)
ax[1].set_title("(b) Replica and clock-path delays", loc="left", fontsize=10)
ax[1].legend(loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=2, fontsize=8, frameon=False)

ax[2].plot([6, 30], [6, 30], color="k", lw=0.8)
ax[2].fill_between([6, 30], [5, 29], [7, 31], color="#e0e0e0", alpha=0.6, lw=0, label="within ±1 code")
for p_, c_, col, l in zip(pred, code, cols, lab):
    ax[2].plot(p_, c_, "o", color=col, ms=7)
for t, c in temp_col.items():
    ax[2].plot([], [], "o", color=c, label=f"{t} °C")
ax[2].set_xlabel("predicted  (T_w - t_TRC) / t_s")
ax[2].set_ylabel("simulated no-droop code")
ax[2].set_xlim(6, 30)
ax[2].set_ylim(6, 30)
ax[2].set_title("(c) Eq. (1) predicts the code within ±1", loc="left", fontsize=10)
ax[2].legend(fontsize=8, loc="upper left")
for p_, c_, l in zip(pred, code, lab):
    if l in ("ff -40", "ss 125", "tt 125", "ff 125", "ss 27", "tt 27", "tt -40"):
        ax[2].annotate(l, (p_, c_), xytext=(6, -3), textcoords="offset points", fontsize=7.5)
fig.suptitle("Corner timing of the post-layout DVM (no droop, 800 MHz, T as set per corner)", x=0.05, ha="left",
             fontsize=12, fontweight="bold", y=1.01)
fig.savefig("fig_corner_timing.png", dpi=150)
fig.savefig("fig_corner_timing.pdf")
for l, a, b, c, d, e in zip(lab, ts, trc, clk, code, pred):
    print(f"{l:8s} ts {a:5.1f} trc {b:5.1f} clk {c:5.1f} code {d:5.2f} pred {e:5.2f}")
