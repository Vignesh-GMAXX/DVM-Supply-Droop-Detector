# Data

Exported simulation results (Cadence ADE L / ADE XL: *Send To → Table* for scalar outputs, *Export → CSV* for waveforms). Large CSVs are gzip-compressed; [`scripts/reproduce_figures.sh`](../scripts/reproduce_figures.sh) decompresses what it needs into `build/`.

Unless stated: post-layout (DVM parasitic-extracted), gpdk045, 800 MHz, V<sub>DD</sub> = 1.0 V, `T = S = 00`. Units are SI (s, V, W, J). How each output is computed: [docs §5.4](../docs/05-simulation-setup.md#54-measurement-expressions).

## Overview

```text
data/
├── ade_l_states/        final test bench (DVM_TOP), saved ADE L states, scalar results
├── ade_xl/              ADE XL runs: waveforms at TT, the 15-corner sweep, detection-map summary
│   └── corners/
├── droop_trains/        waveforms of the droop trains and the detection map
├── montecarlo/          per-sample Monte Carlo results
└── schematic/           schematic-level reference runs
```

## Files

| File | Source | Contents | Used by |
|---|---|---|---|
| `ade_l_states/state_tt.csv` | state `state_tt`: tt 27 °C, vdroop 0 / 0.05 / 0.10 / 0.15 | codes, DVM and TAP_CAL flag levels, latencies, `P_dvm`, `E_cyc`, `E_det` | docs §6 (droop response, power) |
| `ade_l_states/state_static.csv` | state `state_static`: tt 27 °C, long flat droops | code at 17.5 ns (on the flat bottom), the three flag levels and the static supply, for vdroop 0 → 0.15 V in 2.5-mV steps (61 points; X/Y column pairs, X = vdroop) | `make_dnl.py` (report Fig. 3b) |
| `ade_l_states/state_short.csv` | state `state_short`: tt 27 °C, V-shaped droops | DVM and TAP_CAL flag levels for FWHM `w` = 1 / 1.5 / 2 / 3 ns × depth 5 / 10 / 15 % × start `tdelay` 9.9 / 11.15 ns | report Table IV, docs §6 (shortest droop) |
| `ade_l_states/state_worst.csv` | state `state_worst`: ff −40 °C, `T = 11` | as `state_tt` | worst-corner power and energy |
| `ade_l_states/state_ff125.csv` | state `state_ff125`: ff 125 °C, `S = 01` | as `state_tt` | DVM false alarm vs. TAP_CAL at ff 125 °C |
| `ade_l_states/state_ss27.csv` | state `state_ss27`: ss 27 °C, `S = 10` | as `state_tt` | worst-corner TAP_CAL latency (4.94 ns) |
| `ade_xl/W1_droop.csv.gz` | ADE XL, single droops | `VDD_DVM` waveforms, 5 / 10 / 15 % (and other corners) | `make_wave.py` (report Fig. 4) |
| `ade_xl/W1_all.csv.gz` | same runs | `DVM_O<0:2>`, `clkdiv_b` and other nets | `make_wave.py` (report Fig. 4) |
| `ade_xl/tt27_all.npz` | ADE XL, tt 27 °C, vdroop 0 / 0.05 / 0.10 / 0.15 | `taps_<vdroop>` (32 × 8001: `O<0>`…`O<31>`), `VDD_DVM`, `CLK`, `clkdiv_b`, `DVM_O<0:2>`, `CAL_O<0:2>` on a common 5-ps grid `grid` (0–40 ns) | `make_tdc_droop.py`, `make_timing_diagram.py`, `make_tap_timing.py` |
| `ade_xl/tt27_clocks.npz` | same run | `CLK`, `clkdiv`, `clkdiv_b`, `TRC_Out`, `VDD_DVM` on the same grid (float32) | `make_timing_diagram.py`, `make_tap_timing.py` |
| `ade_xl/corners/corners_droop_0_5pct.csv` | ADE XL corner sweep, 15 corners, vdroop 0 and 0.05 | codes, flags, latencies, timing (`t_clk2div`, `t_buf`, `t_TRC`, `t_stage_post`, `tr_clkdiv_b`), power | `make_corner_timing.py`, `make_corner_codes.py` |
| `ade_xl/corners/corners_droop_10_15pct.csv` | ADE XL corner sweep, 15 corners, vdroop 0.10 and 0.15 (final, retimed TAP_CAL) | same outputs | `make_corner_codes.py` |
| `ade_xl/matrix2_res.json` | processed from `droop_trains/MATRIX2_tt27.csv.gz` | per droop: `depth`, `fwhm` (ns), centre `c` (ns), level reached and latency for the DVM and TAP_CAL | `make_matrix.py` (report Fig. 7) |
| `droop_trains/Train2.csv.gz` | ADE XL, tt 27 °C, `VDD_droop_train_v3_tt27.va` | supply and flags for the six-event droop train | `make_train4.py` (report Fig. 6a) |
| `droop_trains/TRAIN4_ff125_clean.csv.gz` | ADE XL, ff 125 °C, `S = 01`, `VDD_droop_train.va` | same, exact-depth train | `make_train4.py` (report Fig. 6b) |
| `droop_trains/MATRIX2_tt27.csv.gz` | ADE XL, tt 27 °C, `VDD_droop_matrix.va` | raw waveforms of the 40-droop detection map | source of `matrix2_res.json` |
| `montecarlo/M1_100_samples.csv` | ADE XL Monte Carlo, **schematic**, 1 GHz, `T = 11`, no droop | 100 samples, process + mismatch: code, flag levels, `t_TRC`, `t_stage_post`, `t_clk2div`, `t_buf`, `tr_clkdiv_b`, `P_mc` | `make_mc.py` (report Fig. 8, Table VI) |
| `montecarlo/M2_100_samples.csv` | same | 100 samples, mismatch only | `make_mc.py` |
| `schematic/trc_trim_sweep.csv` | ADE XL, **schematic**, 800 MHz, tt 27 °C | `t_TRC` and code for `T` = 00 / 01 / 10 / 11 | docs §2.3, §7.6 |

## Column names

| Column | Meaning |
|---|---|
| `vdroop` | droop depth in volts (0.05 = 5 % of 1.0 V) |
| `code_nom`, `code_droop` | code (report eq. 3) before the droop (10 ns) and at the droop bottom (20 ns) |
| `code17.5` | code at 17.5 ns, on the flat bottom (`state_static`) |
| `dflag0..2`, `cflag0..2` | highest level of `DVM_O<k>` / `CAL_O<k>` in the run (V); > 0.5 V = fired |
| `sflag0..2` | flag levels on the flat bottom (`state_static`) |
| `vdd_static` | supply on the flat bottom (`state_static`) |
| `mflag0..2`, `mcal0` | flag levels in the Monte Carlo runs |
| `latency0..2`, `clat0` | droop start (supply at `vnom − 10 mV`) → flag at 0.5 V (s). Read only where that flag fired: ADE fills the other points with misleading values |
| `droop_true` | measured droop depth, `vnom − min(VDD_DVM)` (V) |
| `P_dvm` | DVM power at its own supply terminal, 12.5–22.5 ns (W) |
| `P_pre`, `P_active` | earlier power measurements through the 0-V supply probe (DVM + test-bench clock path, with TAP_CAL where present) |
| `P_mc` | active power in the Monte Carlo runs (schematic) |
| `E_cyc` | `P_dvm × tclk` (J) |
| `E_det` | DVM energy from droop start to `DVM_O<0>` rising (J) |
| `E_sample` | probe power × one measurement (2 cycles) |
| `t_clk2div`, `t_buf` | `CLK` → `clkdiv`, `clkdiv` → `clkdiv_b` (s) |
| `t_TRC` | `clkdiv_b` → `TRC_Out` (s) |
| `t_stage_post` | average TDC stage delay (s) |
| `tr_clkdiv_b` | 10–90 % rise time of `clkdiv_b` (s) |
| `t_clear0` | time at which `DVM_O<0>` falls again after the droop (s) |

## ADE XL corner-table format

The corner files have one column per corner and one block per sweep point:

```text
,,Parameter,,,,,,K1_0,K1_1,...        ← corner names
,,S0,,,,,,0,0,...                     ← per-corner settings: S0, S1, T0, T1, model section, temperature
...
Point,Test,Output,Spec,Weight,Pass/Fail,Min,Max,K1_0,K1_1,...
Parameters: vdroop=0,,,...            ← start of a block
1,Project:DVM_test:1,t_clk2div,,,,...,192.6e-12,...
```

[`scripts/adexl_table.py`](../scripts/adexl_table.py) parses it: `meta, data = read_corner_table(path)`, then `data[0.05]["code_droop"]["C7"]`. Corner names: `K1_0/1/2` tt/fs/sf 27 °C, `C3` ss −40, `C4_0/1/2` tt/fs/sf −40, `C5` ff 27, `C6` ff −40, `C7` ff 125, `C8_0/1/2` tt/fs/sf 125, `C9` ss 27, `C10` ss 125.

**Provenance notes**

- In `corners_droop_0_5pct.csv` the three tt/fs/sf 125 °C corners (`C8_*`) ran with `S = 01` and TAP_CAL was not yet retimed. Their **codes and timing** are valid (they do not depend on `S`); their TAP_CAL flags are not the final ones. The final flags at all corners are in report Table V and [docs §7.4](../docs/07-pvt-and-calibration.md#74-fixed-thresholds-vs-tap_cal).
- These ADE XL corner runs used the TAP_CAL **schematic** next to the extracted DVM; the saved ADE L states use the extracted TAP_CAL.
- Power columns named `P_pre` and `P_active` come from the 0-V probe and include more than the DVM; the reported DVM power is `P_dvm` (138.4 µW at TT).

## Not included

The Cadence library, netlists, extracted views and the PDK are not included (course and PDK licence terms). The raw waveform export behind `tt27_clocks.npz` (54 MB) is not stored; [`scripts/prep/extract_tt27_clocks.py`](../scripts/prep/extract_tt27_clocks.py) shows how it was reduced.
