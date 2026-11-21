# Data

Exported simulation results (Cadence ADE L / ADE XL "Send To → Table" or waveform CSV exports). Large CSVs are gzip-compressed; `scripts/reproduce_figures.sh` decompresses what it needs into `build/`.

All post-layout runs: DVM parasitic-extracted, gpdk045, 800 MHz, VDD = 1.0 V.

| File | Source | Contents | Used by |
|---|---|---|---|
| `ade_l_states/state_static.csv` | ADE L `state_static` (tt 27 °C) | code at 17.5 ns, flags 14–18 ns and static VDD for droop depth 0 → 0.15 V in 2.5-mV steps | `make_dnl.py` (Fig. 3b) |
| `ade_l_states/state_short.csv` | ADE L `state_short` (tt 27 °C) | DVM / TAP_CAL flags for V-shaped droops, FWHM 1–3 ns × depth 5/10/15 % × 2 sampling phases | report Table IV |
| `ade_xl/W1_droop.csv.gz` | ADE XL corner run | `VDD_DVM` waveforms, single droops 5/10/15 % | `make_wave.py` (Fig. 4) |
| `ade_xl/W1_all.csv.gz` | ADE XL corner run | `DVM_O<0:2>`, `clkdiv_b` and other nets for the same runs | `make_wave.py` (Fig. 4) |
| `ade_xl/tt27_all.npz` | ADE XL, tt 27 °C, droops 0/5/10/15 % | all 32 TDC taps, `VDD_DVM` and `clkdiv_b` on a common time grid | `make_tdc_droop.py` (Fig. 5) |
| `ade_xl/matrix2_res.json` | processed from `droop_trains/MATRIX2_tt27.csv.gz` | per droop: depth, FWHM, centre, DVM / TAP_CAL level and latency | `make_matrix.py` (Fig. 7) |
| `droop_trains/Train2.csv.gz` | ADE XL, tt 27 °C, `VDD_droop_train_v3_tt27.va` | supply and flags for the six-event droop train | `make_train4.py` (Fig. 6a) |
| `droop_trains/TRAIN4_ff125_clean.csv.gz` | ADE XL, ff 125 °C, S = 01, `VDD_droop_train.va` | same, exact-depth train | `make_train4.py` (Fig. 6b) |
| `droop_trains/MATRIX2_tt27.csv.gz` | ADE XL, tt 27 °C, `VDD_droop_matrix.va` | raw waveforms of the 40-droop detection map | source of `matrix2_res.json` |
| `montecarlo/M1_100_samples.csv` | ADE XL Monte Carlo, schematic, 1 GHz, T = 11 | 100 samples, process + mismatch | `make_mc.py` (Fig. 8) |
| `montecarlo/M2_100_samples.csv` | same | 100 samples, mismatch only | `make_mc.py` (Fig. 8) |
