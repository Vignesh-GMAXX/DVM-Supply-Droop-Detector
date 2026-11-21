# Verilog-A stimuli

Verilog-A is used only in the test bench, to generate the supply droop. The DVM and TAP_CAL themselves are transistor-level.

| File | Waveform | Used for |
|---|---|---|
| `VDD_droop3.va` | one droop: raised-cosine fall (`tdown`), flat bottom (`twidth`), raised-cosine recovery (`tup`); `mode = 1` gives an RC-like droop | all ADE L states; with `twidth = 0`, `tdown = tup = w` a V-shaped droop of FWHM `w` (`state_short`) |
| `VDD_droop_train_v3_tt27.va` | six rounded droops of different depth and shape in one run | droop train, tt 27 °C (report Fig. 6a) |
| `VDD_droop_train.va` | v4: six droops whose deepest point is exactly 5/10/15 % | droop train, ff 125 °C (report Fig. 6b) |
| `VDD_droop_matrix.va` | 40 Gaussian droops, 8 depths × 5 widths, 8-ns gaps | detection map (report Fig. 7) |

Parameters of `VDD_droop3`: `vnom` (1.0 V), `vdroop` (depth, V), `mode`, `tdelay` (start), `tdown`, `twidth`, `tup`, `tauf`, `taur`.
