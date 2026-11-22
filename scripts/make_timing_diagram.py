"""One measurement cycle of the post-layout DVM, read from the transistor-level waveforms.

Left: no droop.  Right: at the bottom of a 15 % droop.  TT, 27 C, 800 MHz, T = S = 00.
Shows the clock path (CLK -> clkdiv -> clkdiv_b), the replica edge (TRC_Out), a selection of
TDC taps and the flag DVM_O<0>, and annotates every delay that sets the code.

Inputs : tt27_all.npz (taps, CLK, VDD, flags), tt27_clocks.npz (clkdiv, clkdiv_b, TRC_Out)
Output : fig_timing_diagram.png / .pdf
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.linewidth": 0.6,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.08})

A = np.load("tt27_all.npz")
C = np.load("tt27_clocks.npz")
g = A["grid"] * 1e9                                         # ns


def crossings(y, th=0.5):
    s = np.sign(y - th)
    i = np.where(np.diff(s) != 0)[0]
    t = g[i] + (th - y[i]) * (g[i + 1] - g[i]) / (y[i + 1] - y[i])
    return t, np.sign(y[i + 1] - y[i])


def first(y, lo, hi, direction):
    t, d = crossings(y)
    m = (t > lo) & (t < hi) & (d == direction)
    return t[m][0] if m.any() else None


def value(y, t):
    return float(np.interp(t, g, y))


TAPS = [31, 30, 28, 22, 19, 15, 12, 11, 9, 0]
cases = [("0", 10.0, 12.85, "No droop, VDD = 1.00 V"),
         ("0.15", 17.5, 20.35, "Bottom of a 15 % droop, VDD = 0.85 V")]

fig, axes = plt.subplots(1, 2, figsize=(13, 7.6), sharey=True, gridspec_kw={"wspace": 0.12})
LE = "clkdiv_b (latch enable)"
rows = ["CLK", "clkdiv", LE, "TRC_Out"] + [f"O<{k}>" for k in TAPS] + ["DVM_O<0>"]
ypos = {r: len(rows) - 1 - i for i, r in enumerate(rows)}
H = 0.6
summary = []

for ax, (d, t0, t1, title) in zip(axes, cases):
    m = (g >= t0) & (g <= t1)
    vdd = A[f"VDD_DVM_{d}"]
    traces = {"CLK": A[f"CLK_{d}"], "clkdiv": C[f"clkdiv_{d}"], LE: C[f"clkdiv_b_{d}"],
              "TRC_Out": C[f"TRC_Out_{d}"], "DVM_O<0>": A[f"DVM_O<0>_{d}"]}
    for k in TAPS:
        traces[f"O<{k}>"] = A[f"taps_{d}"][k]

    clk_up = first(A[f"CLK_{d}"], t0, t1, +1)
    div_up = first(C[f"clkdiv_{d}"], clk_up, t1, +1)
    open_ = first(C[f"clkdiv_b_{d}"], div_up, t1, +1)
    trc = first(C[f"TRC_Out_{d}"], open_, t1, +1)
    close = first(C[f"clkdiv_b_{d}"], open_, t1, -1)
    clk_dn = first(A[f"CLK_{d}"], close, t1, -1)
    clk_up2 = first(A[f"CLK_{d}"], close, t1, +1)

    # code exactly as eq. (3): read in the hold phase
    th = close + 0.45
    v = value(vdd, th)
    code = 32 - sum(value(A[f"taps_{d}"][k], th) for k in range(32)) / v
    reached = [k for k in range(31, -1, -1) if value(A[f"taps_{d}"][k], th) < 0.5 * v]
    run = 0
    for k in range(31, -1, -1):
        if value(A[f"taps_{d}"][k], th) < 0.5 * v:
            run += 1
        else:
            break
    summary.append((d, code, run, len(reached) - run, 1e3 * (clk_dn - close)))

    ax.axvspan(open_, close, color="#e8f5e9", zorder=-2)
    ax.axvspan(close, t1, color="#fff8e1", zorder=-2)
    for r in rows:
        y = traces[r][m] / np.maximum(vdd[m], 0.5)           # normalised to the local supply
        col = "#1f4e79" if r.startswith("O<") else "#333333"
        if r == LE:
            col = "#2e7d32"
        if r == "DVM_O<0>":
            col = "#b22222"
        ax.plot(g[m], ypos[r] + H * np.clip(y, -0.05, 1.1), color=col, lw=1.15)
        ax.axhline(ypos[r], color="#e3e3e3", lw=0.4, zorder=-1)

    top = len(rows) - 0.25
    ax.text((open_ + close) / 2, top, "sampling window\n(latches transparent)", ha="center", va="bottom",
            fontsize=8, color="#2e7d32")
    ax.text((close + t1) / 2, top, "hold\n(code frozen)", ha="center", va="bottom", fontsize=8,
            color="#a66d00")

    def span(ta, tb, row, label, color="k"):
        y = ypos[row] + 0.8
        ax.annotate("", xy=(tb, y), xytext=(ta, y),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=0.9, shrinkA=0, shrinkB=0))
        ax.text(tb + 0.03, y, label, ha="left", va="center", fontsize=8, color=color)

    span(clk_up, div_up, "clkdiv", f"t_clk2div = {1e3*(div_up-clk_up):.0f} ps")
    span(div_up, open_, LE, f"t_buf = {1e3*(open_-div_up):.0f} ps")
    span(open_, trc, "TRC_Out", f"t_TRC = {1e3*(trc-open_):.0f} ps", color="#2e7d32")

    for k in TAPS:
        tf = first(A[f"taps_{d}"][k], trc, close + 0.1, -1)
        if tf is not None:
            ax.plot(tf, ypos[f"O<{k}>"] + H / 2, "o", ms=3.6, color="#1f4e79", zorder=5)

    ax.axvline(close, color="#2e7d32", ls="--", lw=0.9)
    ax.axvline(clk_dn, color="#b22222", ls=":", lw=1.1)
    ax.text(close - 0.02, -0.75, "latches\nclose", fontsize=7.5, color="#2e7d32", ha="right", va="top")
    ax.text(clk_dn + 0.02, -0.75, "DVM\ndecides", fontsize=7.5, color="#b22222", ha="left", va="top")
    if clk_up2 is not None:
        ax.axvline(clk_up2, color="#6a1b9a", ls=":", lw=1.1)
        ax.text(clk_up2 + 0.02, -0.75, "TAP_CAL\ndecides", fontsize=7.5, color="#6a1b9a",
                ha="left", va="top")
    ym = -0.45
    ax.annotate("", xy=(clk_dn, ym), xytext=(close, ym),
                arrowprops=dict(arrowstyle="<->", color="#b22222", lw=0.8, shrinkA=0, shrinkB=0))
    ax.text(close - 0.02, ym, f"margin {1e3*(clk_dn-close):.0f} ps", fontsize=7.5, color="#b22222",
            va="center", ha="right")
    flag = value(A[f"DVM_O<0>_{d}"], th) > 0.5 * v
    ax.text(t1, ypos["DVM_O<0>"] + H / 2, f" = {int(flag)}", fontsize=8.5, color="#b22222", va="center",
            ha="left", fontweight="bold")
    if d != "0":
        ax.text(t1, ypos["O<0>"] + H / 2, " held 0:\n bubble", fontsize=7.5, color="#1f4e79", va="center",
                ha="left")

    bub = len(reached) - run
    extra = f" + {bub} bubble" if bub else ""
    ax.set_title(f"{title}\ncode = {code:.0f}  ({run} taps reached{extra})", fontsize=10.5, loc="left")
    ax.set_xlim(t0, t1)
    ax.set_xlabel("time (ns)")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)

axes[0].set_yticks([ypos[r] + H / 2 for r in rows])
axes[0].set_yticklabels(rows, fontsize=8.5)
for a in axes:
    a.tick_params(axis="y", length=0)
axes[0].set_ylim(-1.45, len(rows) + 0.55)
fig.suptitle("One DVM measurement in post-layout transistor-level waveforms (TT, 27 °C, 800 MHz, T = S = 00)",
             x=0.07, ha="left", y=1.0, fontsize=11.5, fontweight="bold")
fig.text(0.07, -0.045,
         "Taps reset to 1 when the latches open and fall one by one as the replica edge runs down the inverter chain; "
         "a reached tap reads 0.\nDots: tap fell before the latches closed. Flag DVM_O<0> watches O<15>: it rises "
         "when O<15> is not reached (code <= 16).\nDVM decides on the falling CLK edge (baseline); TAP_CAL on the next rising edge (end of hold). "
         "Margin: time from latch close to the DVM decision edge. Traces are normalised to the local supply.",
         fontsize=8.5, color="#444444")
fig.savefig("fig_timing_diagram.png", dpi=160)
fig.savefig("fig_timing_diagram.pdf")
for s in summary:
    print("vdroop %s: code %.2f, contiguous taps %d, bubbles %d, close->CLK-fall margin %.0f ps" % s)
