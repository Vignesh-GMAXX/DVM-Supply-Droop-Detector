#!/usr/bin/env bash
# Regenerate every data figure of the report and of the documentation from the exported simulation data.
# Usage: scripts/reproduce_figures.sh [output_dir]   (default: build/figures)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/build/figures}"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
cd "$OUT"
export MPLBACKEND=Agg

# Stage the inputs in the working directory (decompress *.csv.gz once, link everything else).
stage() {
  local src="$ROOT/data/$1" name
  name="$(basename "${src%.gz}")"
  if [[ "$src" == *.gz ]]; then
    [[ -f "$name" ]] || gunzip -c "$src" > "$name"
  else
    ln -sf "$src" "$name"
  fi
}
stage ade_l_states/state_static.csv
stage ade_xl/W1_all.csv.gz
stage ade_xl/W1_droop.csv.gz
stage ade_xl/tt27_all.npz
stage ade_xl/tt27_clocks.npz
stage ade_xl/matrix2_res.json
stage ade_xl/corners/corners_droop_0_5pct.csv
stage ade_xl/corners/corners_droop_10_15pct.csv
stage droop_trains/Train2.csv.gz
stage droop_trains/TRAIN4_ff125_clean.csv.gz
stage montecarlo/M1_100_samples.csv
stage montecarlo/M2_100_samples.csv

S="$ROOT/scripts"
export PYTHONPATH="$S${PYTHONPATH:+:$PYTHONPATH}"   # adexl_table.py, wload.py

# Report figures
python3 "$S/make_prepost.py"                                   # Fig. 3a  power and flags through the fixes
python3 "$S/make_dnl.py" > /dev/null                           # Fig. 3b  code vs static VDD, DNL/INL
python3 "$S/make_wave.py"                                      # Fig. 4   droop response
python3 "$S/make_tdc_droop.py"                                 # Fig. 5   TDC taps at the droop bottom
python3 "$S/make_train4.py" Train2.csv TRAIN4_ff125_clean.csv  # Fig. 6   droop trains
python3 "$S/make_matrix.py"                                    # Fig. 7   detection map
python3 "$S/make_mc.py" . > /dev/null                          # Fig. 8   Monte Carlo

# Documentation figures (docs/)
python3 "$S/make_timing_diagram.py"                            # one measurement, 0 % and 15 % droop
python3 "$S/make_tap_timing.py"                                # when each tap is reached
python3 "$S/make_prepost_delays.py"                            # schematic vs extracted delays
python3 "$S/make_corner_timing.py" > /dev/null                 # delays and eq. 1 at 15 corners
python3 "$S/make_corner_codes.py"                              # code vs droop at 15 corners

echo "Figures written to $OUT"
ls -1 "$OUT"/fig_*.png
