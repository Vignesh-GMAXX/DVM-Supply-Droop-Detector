#!/usr/bin/env bash
# Regenerate every data figure of the report from the exported simulation data.
# Usage: scripts/reproduce_figures.sh [output_dir]   (default: build/figures)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/build/figures}"
mkdir -p "$OUT"
cd "$OUT"

# Stage the inputs next to the scripts' working directory (decompress *.csv.gz once).
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
stage ade_xl/matrix2_res.json
stage droop_trains/Train2.csv.gz
stage droop_trains/TRAIN4_ff125_clean.csv.gz
stage montecarlo/M1_100_samples.csv
stage montecarlo/M2_100_samples.csv

S="$ROOT/scripts"
python3 "$S/make_prepost.py"                                   # Fig. 3a
python3 "$S/make_dnl.py"                                       # Fig. 3b
python3 "$S/make_wave.py"                                      # Fig. 4
python3 "$S/make_tdc_droop.py"                                 # Fig. 5
python3 "$S/make_train4.py" Train2.csv TRAIN4_ff125_clean.csv  # Fig. 6
python3 "$S/make_matrix.py"                                    # Fig. 7
python3 "$S/make_mc.py" .                                      # Fig. 8

echo "Figures written to $OUT"
