"""The edge race inside the TDC: when each tap is reached, for 0/5/10/15 % droop.

(a) Time after the latches open at which each tap falls (is reached), measured on the
    post-layout waveforms in the sampling window at the droop bottom. Every tap under the
    latch-close line is counted, so the number of points below the line is the code.
(b) Delay between consecutive taps: stages alternate between a slow and a fast transition,
    which is why even and odd codes have different widths (the DNL in Fig. 3b).

Inputs : tt27_all.npz, tt27_clocks.npz        Output : fig_tap_timing.png / .pdf
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.grid": True, "grid.alpha": 0.25,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.08})

A = np.load("tt27_all.npz")
C = np.load("tt27_clocks.npz")
g = A["grid"] * 1e9


def first(y, lo, hi, direction, th=0.5):
    s = np.sign(y - th)
    i = np.where(np.diff(s) != 0)[0]
    t = g[i] + (th - y[i]) * (g[i + 1] - g[i]) / (y[i + 1] - y[i])
    d = np.sign(y[i + 1] - y[i])
    m = (t > lo) & (t < hi) & (d == direction)
    return t[m][0] if m.any() else None


cases = [("0", 10.0, "0 %  (1.00 V)", "#1f77b4"), ("0.05", 17.5, "5 %  (0.95 V)", "#2ca02c"),
         ("0.1", 17.5, "10 %  (0.90 V)", "#ff7f0e"), ("0.15", 17.5, "15 %  (0.85 V)", "#d62728")]
res = {}
for d, lo, lab, col in cases:
    vdd = A[f"VDD_DVM_{d}"]
    op = first(C[f"clkdiv_b_{d}"], lo, lo + 1.0, +1)
    trc = first(C[f"TRC_Out_{d}"], op, op + 1.5, +1)
    cl = first(C[f"clkdiv_b_{d}"], op, op + 2.0, -1)
    falls = []
    for k in range(31, -1, -1):                       # O<31> is stage 1
        y = A[f"taps_{d}"][k] / np.maximum(vdd, 0.5)
        falls.append(first(y, trc, cl + 0.3, -1))
    th = cl + 0.45
    v = float(np.interp(th, g, vdd))
    code = 32 - sum(float(np.interp(th, g, A[f"taps_{d}"][k])) for k in range(32)) / v
    res[d] = dict(op=op, trc=trc, cl=cl, falls=falls, code=code, lab=lab, col=col)

fig, (a0, a1) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.35, 1], "wspace": 0.22})

for d, r in res.items():
    n = [i + 1 for i, t in enumerate(r["falls"]) if t is not None]
    t = [1e3 * (r["falls"][i - 1] - r["op"]) for i in n]
    a0.plot([0] + n, [1e3 * (r["trc"] - r["op"])] + t, "o-", ms=3.5, lw=1.1, color=r["col"],
            label=f"{r['lab']}: code {r['code']:.0f}")
win = np.mean([1e3 * (r["cl"] - r["op"]) for r in res.values()])
a0.axhline(win, color="k", ls="--", lw=1)
a0.text(31.8, win - 25, f"latches close\n{win:.0f} ps after they open\n(about one 1.25-ns clock period)",
        ha="right", va="top", fontsize=8.5)
a0.annotate("TRC_Out edge\n(stage 0)", xy=(0, 1e3 * (res["0"]["trc"] - res["0"]["op"])), xytext=(2.2, 120),
            fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.7))
a0.set_xlim(-0.8, 32.5)
a0.set_ylim(0, 1500)
a0.set_xticks(range(0, 33, 4))
a0.set_xlabel("TDC stage n reached  (stage n drives tap O<32 - n>)")
a0.set_ylabel("time after the latches open (ps)")
a0.set_title("(a) The edge race: taps reached before the latches close = code", loc="left", fontsize=10.5)
a0.legend(loc="lower right", fontsize=8.5, framealpha=0.95)
a0.text(0.02, 0.97, "15 %: 8 taps + a one-LSB bubble\n(O<0> held at 0) gives code 9", transform=a0.transAxes,
        fontsize=8, va="top", color="#d62728")

for d, off, w in [("0", -0.2, 0.4), ("0.15", 0.2, 0.4)]:
    r = res[d]
    ts = [r["trc"]] + [t for t in r["falls"] if t is not None]
    st = np.diff(ts) * 1e3
    idx = np.arange(1, len(st) + 1)
    cols = [r["col"] if i % 2 == 0 else r["col"] for i in idx]
    a1.bar(idx + off, st, width=w, color=cols, alpha=0.85 if d == "0" else 0.6, label=r["lab"])
a1.set_xlabel("TDC stage n")
a1.set_ylabel("delay from the previous tap (ps)")
a1.set_title("(b) Stage delays alternate slow / fast", loc="left", fontsize=10.5)
a1.set_xticks(range(1, 21))
a1.tick_params(axis="x", labelsize=7.5)
a1.legend(fontsize=8.5, loc="upper right")
st0 = np.diff([res["0"]["trc"]] + [t for t in res["0"]["falls"] if t is not None]) * 1e3
even = st0[1::2][:9]
odd = st0[2::2][:9]
a1.text(0.98, 0.62, f"0 % droop:\nslow stages ≈ {np.mean(even):.0f} ps\nfast stages ≈ {np.mean(odd):.0f} ps\n"
        f"stage 1 includes the first\ninverter and latch", transform=a1.transAxes, ha="right", va="top", fontsize=8.5)
fig.savefig("fig_tap_timing.png", dpi=160)
fig.savefig("fig_tap_timing.pdf")
for d, r in res.items():
    print(d, "code %.2f" % r["code"], "TRC %.0f ps" % (1e3 * (r["trc"] - r["op"])), "window %.0f ps" % (1e3 * (r["cl"] - r["op"])))
print("slow/fast at 0 %%: %.1f / %.1f ps" % (np.mean(even), np.mean(odd)))
