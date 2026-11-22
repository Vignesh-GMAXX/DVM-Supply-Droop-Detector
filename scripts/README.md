# Scripts

Python scripts that turn the exported simulation data in [`data/`](../data) into every data figure of the report and of the documentation. No simulator is needed.

## Quick start

```bash
pip install -r scripts/requirements.txt     # numpy, pandas, matplotlib
bash scripts/reproduce_figures.sh           # → build/figures/fig_*.png and .pdf (about 30 s)
bash scripts/reproduce_figures.sh /tmp/out  # or any output folder
```

[`reproduce_figures.sh`](reproduce_figures.sh) stages the inputs in the output folder (decompressing the `.csv.gz` files once), puts `scripts/` on `PYTHONPATH` and runs every script there. The regenerated report figures render identically to the PDFs in [`report/latex/`](../report/latex).

The same run, plus [`check_links.py`](check_links.py), executes on every push in GitHub Actions ([workflow](../.github/workflows/reproduce-figures.yml)); the figures are attached to each run as an artifact.

## Figure scripts

| Script | Figure | Inputs (from `data/`) | What it shows |
|---|---|---|---|
| [`make_prepost.py`](make_prepost.py) | report Fig. 3a | values logged in the script | active power and no-droop flags through the design fixes |
| [`make_dnl.py`](make_dnl.py) | report Fig. 3b | `ade_l_states/state_static.csv` | code vs. static supply, DNL / INL; also writes `dnl_res.json` and prints the per-code widths |
| [`make_wave.py`](make_wave.py) | report Fig. 4 | `ade_xl/W1_droop.csv.gz`, `ade_xl/W1_all.csv.gz` | 5 / 10 / 15 % droops and `DVM_O<0:2>` |
| [`make_tdc_droop.py`](make_tdc_droop.py) | report Fig. 5 | `ade_xl/tt27_all.npz` | all 32 taps in one window at the droop bottom |
| [`make_train4.py`](make_train4.py) | report Fig. 6 | `droop_trains/Train2.csv.gz`, `droop_trains/TRAIN4_ff125_clean.csv.gz` | droop trains at TT and ff 125 °C, DVM vs. TAP_CAL level |
| [`make_matrix.py`](make_matrix.py) | report Fig. 7 | `ade_xl/matrix2_res.json` | detection map, 40 Gaussian droops |
| [`make_mc.py`](make_mc.py) | report Fig. 8 | `montecarlo/M1_100_samples.csv`, `montecarlo/M2_100_samples.csv` | Monte Carlo histograms; prints the statistics of report Table VI |
| [`make_timing_diagram.py`](make_timing_diagram.py) | docs §2.4 | `ade_xl/tt27_all.npz`, `ade_xl/tt27_clocks.npz` | one measurement in waveforms, 0 % and 15 % droop, with every delay annotated |
| [`make_tap_timing.py`](make_tap_timing.py) | docs §2.4, §6 | same | when each tap is reached; alternating stage delays |
| [`make_prepost_delays.py`](make_prepost_delays.py) | docs §4.4 | values in the script (report Table II, Section VI-A) | schematic vs. extracted delays |
| [`make_corner_timing.py`](make_corner_timing.py) | docs §7.2 | `ade_xl/corners/corners_droop_0_5pct.csv` | stage, replica and clock-path delay per corner; eq. 1 check |
| [`make_corner_codes.py`](make_corner_codes.py) | docs §7.3 | `ade_xl/corners/*.csv` | code vs. droop at all 15 corners with both sets of thresholds |

Every script writes a `.png` and a `.pdf` into the current directory. Several also print the numbers they plot, so a value in the documentation can be traced to its source.

## Helpers

| File | Purpose |
|---|---|
| [`adexl_table.py`](adexl_table.py) | parses ADE XL corner-table exports (one column per corner, one block per sweep point) into `meta[corner]` (`S`, `T`, model section, temperature) and `data[vdroop][output][corner]` |
| [`wload.py`](wload.py) | loads ADE waveform exports (X/Y column pairs) into numpy arrays, keyed by signal, corner, droop and temperature |
| [`make_train.py`](make_train.py) | plotting helpers for the droop trains, used by `make_train4.py` (on its own it draws the first, Gaussian version of the train figure, whose data is not included) |
| [`check_links.py`](check_links.py) | checks every relative link, image and `#anchor` in the repository's markdown files (GitHub heading rules); exits with status 1 if anything is broken |
| [`prep/extract_tt27_clocks.py`](prep/extract_tt27_clocks.py) | one-off: cuts the clock-path waveforms out of the raw 54-MB waveform export into `data/ade_xl/tt27_clocks.npz` |

## Conventions

- Times in the data are in seconds, voltages in volts, powers in watts; the scripts convert for the axes.
- A code is computed from the latch voltages exactly as in the simulator (`32 − Σ O<k> / V_DD`, report eq. 3).
- The `.npz` files were made from the waveform CSVs by interpolating onto a common 5-ps grid.
