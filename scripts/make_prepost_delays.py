"""Schematic vs. extracted (post-layout) delays at TT, 27 C, VDD = 1.0 V, T = 00.

Values are the cell and block measurements of report Table II and Section VI-A (ADE runs on the
schematic and on the av_extracted views). The ratio shows where the post-layout slow-down came from:
the TDC stage (wiring between stages) and the divider flip-flop driving the clock buffer.

Output : fig_prepost_delays.png / .pdf
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.grid": True, "grid.alpha": 0.25,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.08})
rows = [  # name, schematic (ps), extracted (ps)
    ("FO1 inverter  τ_FO1", 8.33, 10.78),
    ("buffer (FO1)", 18.34, 25.2),
    ("TDC stage t_s (inside DVM)", 26.9, 47.1),
    ("÷2 DFF clock-to-Q (loaded)", 49.28, 192.6),
    ("clock path t_clk2div + t_buf", 155.0, 317.0),
    ("replica delay t_TRC (T = 00)", 175.9, 325.6),
]
names = [r[0] for r in rows]
sch = np.array([r[1] for r in rows])
ext = np.array([r[2] for r in rows])
y = np.arange(len(rows))[::-1]
fig, (a0, a1) = plt.subplots(1, 2, figsize=(12, 3.8), gridspec_kw={"width_ratios": [1.6, 1], "wspace": 0.08},
                             sharey=True)
h = 0.38
a0.barh(y + h / 2, sch, height=h, color="#90caf9", label="schematic")
a0.barh(y - h / 2, ext, height=h, color="#1565c0", label="extracted (post-layout)")
for yi, s, e in zip(y, sch, ext):
    a0.text(s + 3, yi + h / 2, f"{s:g} ps", va="center", fontsize=8)
    a0.text(e + 3, yi - h / 2, f"{e:g} ps", va="center", fontsize=8, color="#0d47a1")
a0.set_yticks(y)
a0.set_yticklabels(names)
a0.set_xlabel("delay (ps)")
a0.set_xlim(0, 380)
a0.legend(loc="upper right", fontsize=8.5)
a0.set_title("(a) Delays before and after extraction", loc="left", fontsize=10.5)
r = ext / sch
a1.barh(y, r, color=["#9e9e9e", "#9e9e9e", "#c62828", "#c62828", "#c62828", "#c62828"])
for yi, v in zip(y, r):
    a1.text(v + 0.05, yi, f"{v:.2f}×", va="center", fontsize=9)
a1.axvline(1, color="k", lw=0.7)
a1.set_xlim(0, 4.6)
a1.set_xlabel("extracted / schematic")
a1.set_title("(b) Slow-down factor", loc="left", fontsize=10.5)
fig.text(0.0, -0.12, "A gate driving its own input slows only 1.3×, but the TDC stage slows 1.75× (wiring between "
         "stages, κ = t_s/τ_FO1: 3.0 → 4.4)\nand the divider DFF clock-to-Q ~3.9× (the extracted value is measured "
         "with its real load: the clock buffer and its wiring). TT, 27 °C, 1.0 V.", fontsize=8.5, color="#444444")
fig.savefig("fig_prepost_delays.png", dpi=150)
fig.savefig("fig_prepost_delays.pdf")
print("ok")
