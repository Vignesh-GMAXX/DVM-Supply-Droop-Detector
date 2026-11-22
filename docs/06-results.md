# Results

All post-layout numbers: DVM and TAP_CAL parasitic-extracted (av_extracted), gpdk045, 800 MHz, VDD = 1.0 V, TT, 27 °C unless stated. Full discussion in the [report](../report/P1G11_FinalReport.pdf).

## Figure-of-merit summary (report Table VII)

| FoM | Condition | Spec | Pre-layout (1 GHz) | Post-layout (800 MHz) | Worst corner | Monte Carlo |
|---|---|---|---|---|---|---|
| Resolution | mV/LSB, static sweep | – | 10 mV | **13.3 mV** | 25 mV (125 °C) | n/m |
| DNL / INL (LSB) | codes 10–19 | – | n/m | −0.81..0.89 / −0.89..0.08 | n/m | n/m |
| Detection levels | flags | 5/10/15 % | 5/10/15 % | **5/10/15 %** | 5 % only (hot) | – |
| Flag switching | static VDD | 0.95/0.90/0.85 V | n/m | 0.958/0.905/0.868 V | n/m | n/m |
| Shortest flagged droop | FWHM, 5 % / 10 % | – | n/m | 2 / 1 ns | n/m | n/a |
| Detection latency | droop → flag | ≤ 5 ns | 3.31 ns | **1.9–4.5 ns** | 4.94 ns (TAP_CAL, ss 27 °C, 10 %) | n/a |
| False warnings, no droop | 15 corners | 0 | n/m | DVM 6/15; **TAP_CAL 0/15** | ss 27: DVM 100 / CAL 000 | 0/100 |
| Active power | at f<sub>max</sub> | ≤ 300 µW | 143.9 µW | **138.4 µW** | 202.3 µW (ff −40 °C) | 144.1 ± 2.2 µW |
| TAP_CAL power overhead | TT, no droop | – | n/a | ≈ 11 µW (6 %) | n/m | n/a |
| Energy / cycle | P/f | – | 144 fJ | **173 fJ** | 253 fJ | 144 ± 2 fJ |
| Energy / detection E<sub>tot</sub> | ∫P dt to flag | – | n/m | 0.28–0.71 pJ | 0.65 pJ | n/a |
| RWP | (mV/LSB) × T<sub>w</sub> | – | 10 mV·ns | 16.6 mV·ns | n/m | n/a |
| ERP | (P/f) × (mV/LSB) | – | 1.44 pJ·mV | 2.29 pJ·mV | n/m | n/a |
| FoM1 = RWP × ERP | lower is better | – | 1.44 × 10⁴ | 3.80 × 10⁴ | n/m | n/a |
| FoM2 = FoM1 × Area | lower is better | – | n/a | 2.50 × 10⁷ | n/a | n/a |
| Leakage | clock stopped | – | n/m | 5.67 (6.67) nW | 90.2 (112) nW (ff 125 °C) | n/a |
| Area | layout (DVM) | ≤ 0.005 mm² | n/a | **658.7 µm²** | n/a | n/a |
| Calibration points | per die | – | – | 1 (sets S, T) | – | – |
| Reference; Verilog-A | – | – | – | clock only; none | – | – |

Values in brackets include TAP_CAL. RWP, ERP, FoM1, FoM2 are in the course units (mV, ns, fJ, µm²), T<sub>w</sub> = t<sub>clk</sub>. n/m: not measured; n/a: not applicable.

## PVT corners: fixed thresholds vs. TAP_CAL (report Table V)

Flags at 0/5/10/15 % droop; expected `000/100/110/111`. S = TAP_CAL tap table, T = TRC trim.

| Corner | S/T | Code | DVM_O (fixed taps) | CAL_O (TAP_CAL) |
|---|---|---|---|---|
| tt 27 | 00/00 | 20 | 000/100/110/111 | 000/100/110/111 |
| fs 27 | 00/00 | 20 | 000/100/110/111 | 000/100/110/111 |
| sf 27 | 00/00 | 20 | 000/100/110/111 | 000/100/110/111 |
| ff 27 | 00/10 | 20 | 000/100/110/111 | 000/100/110/111 |
| ss 27 | 10/00 | 14 | **100**/**110**/**111**/111 | 000/100/**111**/111 |
| tt −40 | 00/11 | 18 | 000/100/110/111 | 000/100/110/111 |
| fs −40 | 00/11 | 18 | 000/100/110/111 | 000/100/110/111 |
| sf −40 | 00/11 | 18 | 000/100/110/111 | 000/100/110/111 |
| ff −40 | 00/11 | 28 | 000/**000**/**000**/**110** | 000/**000**/**000**/**110** |
| ss −40 | 00/00 | 20 | 000/100/110/111 | 000/100/110/111 |
| tt 125 | 10/00 | 12 | **110**/**111**/**111**/111 | 000/100/**111**/111 |
| fs 125 | 10/00 | 12 | **110**/**111**/**111**/111 | 000/100/**111**/111 |
| sf 125 | 10/00 | 12 | **110**/**111**/**111**/111 | 000/100/**111**/111 |
| ff 125 | 01/00 | 16 | **100**/100/110/111 | 000/100/110/111 |
| ss 125 | 11/00 | 9 | **111**/**111**/**111**/111 | 000/**000**/**000**/**000** (disabled) |
| **Detected correctly** | | | **41/60** | **50/60** |
| **False warnings** | | | **16/60** | **4/60** |

Bold: wrong. False warning: flag level above the applied droop. TAP_CAL removes every no-droop false alarm.

## Monte Carlo (schematic, 100 samples, LHS, TT 27 °C, 1 GHz, T = 11, no droop; report Table VI)

| µ ± σ | Process + mismatch | Mismatch only |
|---|---|---|
| Code (range) | 20.9 ± 1.0 (19–23) | 21.4 ± 0.6 (20–22) |
| t<sub>TRC</sub> (ps) | 428.6 ± 13.7 | 425.9 ± 3.2 |
| t<sub>s</sub> (ps) | 28.45 ± 1.00 | 28.29 ± 0.51 |
| t<sub>clk2div</sub> + t<sub>buf</sub> (ps) | 171.7 ± 5.6 | 170.4 ± 2.6 |
| P<sub>act</sub> (µW) | 144.1 ± 2.2 | 144.8 ± 0.9 |
| Samples with no false flag | 100/100 | 100/100 |
| Margin to flag0 | 4.3σ | 8.1σ |

Global process causes 94 % of the replica-delay variance, 74 % of the stage-delay variance and 66 % of the code variance, so per-die calibration (T trim, S tap table) addresses the dominant source.

## Comparison with published supply-droop monitors (report Table VIII, abridged)

| | [1] JSSC'04 | [3,5] Bowman | [2] JSSC'17 | [8] Access'21 | [7] JSSC'22 | [9] TCAS-I'23 | [10] ISCAS'25 | **This work** |
|---|---|---|---|---|---|---|---|---|
| Technology | 90 nm | 45 nm | 28 nm | 65 nm | 65 nm | 28 nm | 22 nm | **45 nm** |
| All-digital | no | yes | yes | no | no | yes | yes | **yes** |
| Sampling rate | core clock | 1 per 2 clk | 0.4–2.24 GS/s | 1.6-µs count | 500 MHz | 0.5–2 GS/s | 2 GS/s | **400 MS/s** |
| Resolution | 20 mV step | 6.5-ps step | 3.3 mV | 10 mV | 0.9 % V<sub>DD</sub> | 1.92–7.32 mV | 7.01 mV | **13.3 mV** |
| Detection latency | n/r | 2-cycle readout | 2 cycles | ≈ 5 ns | 2–3.5 ns | 0 (prediction) | n/r | **1.9–4.5 ns** |
| Area (µm²) | n/r | 1990 | 108500 (macro) | 8800 | 8500 | 1427 | 819 | **659** |
| Power | n/r | n/r | 416 µW (macro) | 297 µW | 62 µW | 4.93 mW | 2.19 mW | **138 µW** |
| Energy / cycle | n/r | n/r | 520 fJ | n/r | 124 fJ | 2.46 pJ | 1.10 pJ | **173 fJ** |
| False warnings over corners | n/r | n/r | n/r | n/r | n/r | n/r | n/r | **0/15** |
| Result type | measured | measured | measured | measured | measured | measured | simulated | post-layout sim. |

Energy per cycle of [2], [7], [9], [10] derived as power / clock (sampling) frequency. The DVM has the smallest area of the compared monitors and the second-lowest power and energy per cycle after [7]; its resolution is 2–7× coarser than the 22–28-nm GS/s sensors.

## Limitations

- At hot corners the TDC floor (code 9–10) limits TAP_CAL to one level (droop ≥ 5 %); at ss 125 °C TAP_CAL is disabled.
- At ff −40 °C the code sits at 27–28 even with maximum trim, so 5 % and 10 % droops are missed.
- Thresholds sit on the nominal codes: droops shorter than ≈ 8 ns are under-graded by one level (Fig. 7).
- Rising and falling stage delays differ (taps 28/60 ps apart), giving DNL up to −0.81 LSB.
- The 1.75× post-layout stage delay forced 800 MHz, raising energy per cycle from 144 to 173 fJ.
