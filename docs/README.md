# Documentation

[← Repository home](../README.md)

Eleven chapters, from "what is a supply droop" to "how do I rerun every simulation". Each chapter stands on its own and links to the others where it needs them.

| # | Chapter | What you will find |
|---|---|---|
| 1 | [Background](01-background.md) | supply droops, why they matter, families of droop monitors, Bowman's DVM, the project objectives and whether they were met |
| 2 | [Architecture and theory of operation](02-architecture.md) | block diagram, clocking, replica, TDC, how taps become a code, the design equations with our numbers, decision stages, TAP_CAL, timing budget |
| 3 | [Circuits and cells](03-circuits-and-cells.md) | device sizes, every leaf cell and block with its schematic and layout, instance and pin lists, the test-bench hierarchy, cell delays |
| 4 | [Layout and extraction](04-layout-and-extraction.md) | floorplan, block layouts, the DRC/LVS/extraction flow, what extraction changed and why |
| 5 | [Simulation setup and reproduction guide](05-simulation-setup.md) | library structure, test bench, droop stimuli, every measurement expression, the saved states, a step-by-step rebuild, pitfalls |
| 6 | [Results](06-results.md) | transfer curve and DNL/INL, droop response and latency, the TDC edge race, short droops, droop trains, detection map, power, figures of merit, comparison with published monitors |
| 7 | [PVT corners and calibration](07-pvt-and-calibration.md) | what sets the code at each corner, fixed thresholds vs. TAP_CAL at 15 corners, why each failing corner fails, the calibration procedure |
| 8 | [Monte Carlo](08-monte-carlo.md) | 100-sample process + mismatch and mismatch-only runs, false-alarm margin, global vs. local variation |
| 9 | [Design journey and lessons learned](09-design-journey.md) | how the design got here: the post-layout failure, the fixes, TAP_CAL, the timing race, and ten lessons |
| 10 | [FAQ](10-faq.md) | about 35 short questions and answers, viva style |
| – | [Glossary](glossary.md) | signals, symbols, metrics and tool terms |

## Reading paths

| If you want to… | Read |
|---|---|
| understand the design in ten minutes | the [repository README](../README.md), then [2.1–2.6](02-architecture.md) |
| understand why it needed calibration | [7. PVT and calibration](07-pvt-and-calibration.md), then [8. Monte Carlo](08-monte-carlo.md) |
| learn what can go wrong after layout | [4.4 What extraction changed](04-layout-and-extraction.md#what-extraction-changed), then [9. Design journey](09-design-journey.md) |
| rebuild or rerun the simulations | [5. Simulation setup](05-simulation-setup.md) and [`data/README.md`](../data/README.md) |
| regenerate the figures | [`scripts/README.md`](../scripts/README.md) |
| prepare for questions | [10. FAQ](10-faq.md) and the [glossary](glossary.md) |

## Figures in this documentation

| Figure | Shows | Chapter | Script |
|---|---|---|---|
| `fig_timing_diagram.png` | one measurement in post-layout waveforms, 0 % and 15 % droop | [2.4](02-architecture.md#24-time-to-digital-converter-tdc) | [`make_timing_diagram.py`](../scripts/make_timing_diagram.py) |
| `fig_tap_timing.png` | when each tap is reached, stage-delay alternation | [2.4](02-architecture.md#why-the-stage-delay-alternates), [6](06-results.md#inside-the-tdc-the-edge-race) | [`make_tap_timing.py`](../scripts/make_tap_timing.py) |
| `fig_prepost_delays.png` | schematic vs. extracted delays | [4.4](04-layout-and-extraction.md#what-extraction-changed) | [`make_prepost_delays.py`](../scripts/make_prepost_delays.py) |
| `fig_prepost.png` | power and flags through the post-layout fixes | [6](06-results.md#recovering-the-post-layout-design) | [`make_prepost.py`](../scripts/make_prepost.py) |
| `fig_static.png` | code vs. static supply, DNL / INL | [6](06-results.md#static-transfer-curve-resolution-dnl-inl) | [`make_dnl.py`](../scripts/make_dnl.py) |
| `fig_w1.png` | 5 / 10 / 15 % droops and the flags | [6](06-results.md#droop-response-and-detection-latency) | [`make_wave.py`](../scripts/make_wave.py) |
| `fig_tdc_droop.png` | all 32 taps at the droop bottom | [6](06-results.md#inside-the-tdc-the-edge-race) | [`make_tdc_droop.py`](../scripts/make_tdc_droop.py) |
| `fig_train.png` | six-droop trains at TT and ff 125 °C | [6](06-results.md#droop-trains) | [`make_train4.py`](../scripts/make_train4.py) |
| `fig_matrix.png` | detection map, 40 droops | [6](06-results.md#detection-map) | [`make_matrix.py`](../scripts/make_matrix.py) |
| `fig_corner_timing.png` | stage, replica and clock-path delays per corner; eq. 1 check | [7.2](07-pvt-and-calibration.md#what-sets-the-code-at-each-corner) | [`make_corner_timing.py`](../scripts/make_corner_timing.py) |
| `fig_corner_codes.png` | code vs. droop at all 15 corners with both sets of thresholds | [7.3](07-pvt-and-calibration.md#73-code-under-droop-at-every-corner) | [`make_corner_codes.py`](../scripts/make_corner_codes.py) |
| `fig_mc.png` | Monte Carlo distributions | [8](08-monte-carlo.md#82-results) | [`make_mc.py`](../scripts/make_mc.py) |
| `hierarchy.png` | design hierarchy | [3.2](03-circuits-and-cells.md#32-leaf-cells) | [`diagrams/generator/big.py`](../diagrams/generator/big.py) (editable draw.io in [`diagrams/`](../diagrams)) |

Cadence schematic screenshots are in [`images/schematics/`](images/schematics), layout screenshots in [`images/layout/`](images/layout).
