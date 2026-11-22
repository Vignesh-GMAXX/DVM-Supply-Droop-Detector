"""TDC code vs. droop depth at all 15 process-temperature corners, with the flag thresholds.

Each panel is one corner: the post-layout code at 0/5/10/15 % droop (ADE XL corner runs), the three
fixed DVM thresholds (taps O<15>/O<19>/O<22>: flag fires when code <= 16 / 12 / 9) and the TAP_CAL
thresholds selected for that corner by S. The flags printed in each panel are report Table V.

Inputs : corners/corners_droop_0_5pct.csv, corners/corners_droop_10_15pct.csv
Output : fig_corner_codes.png / .pdf
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from adexl_table import read_corner_table

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "savefig.bbox": "tight",
                     "savefig.pad_inches": 0.08})

m05, d05 = read_corner_table("corners_droop_0_5pct.csv")
m10, d10 = read_corner_table("corners_droop_10_15pct.csv")
code = {}
for cid, m in m05.items():
    key = (m["gpdk045.scs"], int(m["temperature"]))
    code[key] = [d05[0.0]["code_droop"][cid], d05[0.05]["code_droop"][cid],
                 d10[0.1]["code_droop"][cid], d10[0.15]["code_droop"][cid]]
    code[key + ("T",)] = f"{m['T1']}{m['T0']}"

# S per corner and the flags of report Table V (0/5/10/15 % droop; expected 000/100/110/111)
S = {("tt", 27): "00", ("fs", 27): "00", ("sf", 27): "00", ("ff", 27): "00", ("ss", 27): "10",
     ("tt", -40): "00", ("fs", -40): "00", ("sf", -40): "00", ("ff", -40): "00", ("ss", -40): "00",
     ("tt", 125): "10", ("fs", 125): "10", ("sf", 125): "10", ("ff", 125): "01", ("ss", 125): "11"}
OK = "000/100/110/111"
DVM = {k: OK for k in S}
CAL = {k: OK for k in S}
DVM.update({("ss", 27): "100/110/111/111", ("ff", -40): "000/000/000/110", ("tt", 125): "110/111/111/111",
            ("fs", 125): "110/111/111/111", ("sf", 125): "110/111/111/111", ("ff", 125): "100/100/110/111",
            ("ss", 125): "111/111/111/111"})
CAL.update({("ss", 27): "000/100/111/111", ("ff", -40): "000/000/000/110", ("tt", 125): "000/100/111/111",
            ("fs", 125): "000/100/111/111", ("sf", 125): "000/100/111/111", ("ss", 125): "000/000/000/000"})
TH = {"00": (16, 12, 9), "01": (14, 11, 10), "10": (10, 8, 7), "11": ()}   # code <= 31 - tap


def score(s):
    return sum(a == b for a, b in zip(s.split("/"), OK.split("/")))


procs = ["tt", "fs", "sf", "ff", "ss"]
temps = [-40, 27, 125]
fig, axes = plt.subplots(3, 5, figsize=(14, 9), sharex=True, sharey=True,
                         gridspec_kw={"hspace": 0.42, "wspace": 0.08})
x = [0, 5, 10, 15]
for i, T in enumerate(temps):
    for j, p in enumerate(procs):
        ax = axes[i, j]
        k = (p, T)
        for t in TH["00"]:
            ax.axhline(t, color="#9e9e9e", ls="--", lw=0.9)
        s = S[k]
        if s not in ("00",):
            for t in TH[s]:
                ax.axhline(t, color="#7b1fa2", ls="-", lw=0.9, alpha=0.8)
        ax.plot(x, code[k], "o-", color="#1f4e79", lw=1.6, ms=5, zorder=5)
        for xi, c in zip(x, code[k]):
            ax.text(xi, c + 0.9, f"{c:.0f}", ha="center", fontsize=7.5, color="#1f4e79")
        dv, ca = DVM[k], CAL[k]
        ax.text(0.03, 0.05, f"DVM {dv}  ({score(dv)}/4)", transform=ax.transAxes, fontsize=7.3, bbox=dict(facecolor="white", alpha=0.85, lw=0, pad=0.6),
                color="#2e7d32" if score(dv) == 4 else "#c62828")
        if s == "11":
            ax.text(0.03, 0.15, "CAL 000/000/000/000  (disabled)", transform=ax.transAxes, fontsize=7.3, bbox=dict(facecolor="white", alpha=0.85, lw=0, pad=0.6),
                    color="#616161")
        else:
            ax.text(0.03, 0.15, f"CAL {ca}  ({score(ca)}/4)", transform=ax.transAxes, fontsize=7.3, bbox=dict(facecolor="white", alpha=0.85, lw=0, pad=0.6),
                    color="#2e7d32" if score(ca) == 4 else "#c62828")
        ax.set_title(f"{p} {T} °C   S={s}  T={code[k + ('T',)]}", fontsize=9.5,
                     fontweight="bold" if score(dv) < 4 else "normal")
        ax.set_ylim(2, 31)
        ax.set_xlim(-1.5, 16.5)
        ax.set_xticks(x)
        ax.grid(alpha=0.2)
        if j == 0:
            ax.set_ylabel("TDC code")
        if i == 2:
            ax.set_xlabel("droop (%)")
fig.suptitle("TDC code vs. droop at the 15 PVT corners (post-layout, 800 MHz)", x=0.06, ha="left", y=0.985,
             fontsize=12, fontweight="bold")
fig.text(0.06, 0.962, "Gray dashed: fixed DVM thresholds (flag fires at code <= 16 / 12 / 9).  "
         "Purple: TAP_CAL thresholds chosen by S for that corner.  Flags DVM_O / CAL_O at 0/5/10/15 % from "
         "report Table V (expected 000/100/110/111).\nThe code is read at the droop bottom (20 ns); a flag is the "
         "highest level reached in the run, so at hot corners the flags fire on the way down even where the bottom "
         "code has aliased back up.", fontsize=8.8, color="#333333", va="top")
fig.savefig("fig_corner_codes.png", dpi=150)
fig.savefig("fig_corner_codes.pdf")
print({f"{p} {t}": code[(p, t)] for p in procs for t in temps})
