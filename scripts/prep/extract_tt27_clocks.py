"""Extract the clock-path waveforms of the tt 27 C droop run into a small .npz.

Input : the raw ADE XL waveform export TT_27_ALLDROOPS_ALLOTHER.csv (X/Y column
        pairs per signal and droop depth, ~54 MB, not stored in this repository).
Output: data/ade_xl/tt27_clocks.npz on the same 5-ps grid as tt27_all.npz, with
        CLK, clkdiv, clkdiv_b, TRC_Out and VDD_DVM for vdroop = 0/0.05/0.1/0.15.

Usage : python3 scripts/prep/extract_tt27_clocks.py TT_27_ALLDROOPS_ALLOTHER.csv data/ade_xl/tt27_clocks.npz
"""
import sys
import numpy as np
import pandas as pd

src, dst = sys.argv[1], sys.argv[2]
df = pd.read_csv(src, low_memory=False)
grid = np.arange(0, 40e-9 + 1e-15, 5e-12)
out = {"grid": grid}
for sig in ["CLK", "clkdiv", "clkdiv_b", "TRC_Out", "VDD_DVM"]:
    for d in ["0", "0.05", "0.1", "0.15"]:
        x = pd.to_numeric(df[f"/{sig} (vdroop={d}) X"], errors="coerce").to_numpy()
        y = pd.to_numeric(df[f"/{sig} (vdroop={d}) Y"], errors="coerce").to_numpy()
        ok = np.isfinite(x) & np.isfinite(y)
        out[f"{sig}_{d}"] = np.interp(grid, x[ok], y[ok]).astype(np.float32)
np.savez_compressed(dst, **out)
print("wrote", dst, len(out) - 1, "traces")
