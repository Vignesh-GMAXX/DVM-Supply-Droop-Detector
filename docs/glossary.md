# Glossary

[← 10. FAQ](10-faq.md) · [Documentation index](README.md)

Terms, signal names and symbols used in this repository and in the report.

## Signals and pins

| Name | Meaning |
|---|---|
| `CLK` | 800-MHz input clock (period `tclk` = 1.25 ns) |
| `CLKn` | inverted `CLK`; clocks the DVM's decision flip-flops (falling `CLK` edge) |
| `clkdiv`, `clkdivB` | divider output (`CLK` ÷ 2) and its inverse; `clkdivB` is fed back to the divider's D input and selects the decision muxes |
| `clkdiv_b` | buffered `clkdiv` (4× then 16× inverter): enables all 32 latches and drives the TRC input. High = sampling window, low = hold |
| `TRC_Out` | replica output; the edge that runs down the TDC |
| `O<31:0>` | the 32 TDC taps (latch outputs). `O<31>` is the first stage. Reached = 0 |
| `DVM_O<2:0>` | the DVM's flags: `<0>` ≥ 5 %, `<1>` ≥ 10 %, `<2>` ≥ 15 % droop (taps `O<15>`, `O<19>`, `O<22>`) |
| `CAL_O<2:0>` | TAP_CAL's flags, same meaning, thresholds chosen by `S` |
| `T<1:0>` (`T1 T0`) | TRC trim: 4, 8, 12 or 16 buffers |
| `S<1:0>` (`S1 S0`) | TAP_CAL tap select; `S = 11` disables the flags |
| `SN` | active-low set of the divider (and TAP_CAL) flip-flops; released at start-up |
| `VDD_DVM` | the drooping supply net driven by the test bench's droop source |

## Blocks and cells

| Name | Meaning |
|---|---|
| **DVM** | dynamic variation monitor: divider, clock buffer, TRC, TDC and three decision stages (after Bowman *et al.*) |
| **TRC** | tunable replica circuit: 16 buffers + 4:1 mux; stands in for the protected logic and positions the code |
| **TDC** | time-to-digital converter: 32 inverters, each with a D-latch tap |
| **TAP_CAL** | this project's calibration block: three 4:1 muxes choose the flag taps per die, followed by decision stages retimed to the end of the hold phase |
| **Decision stage** | Mux2_1_TG + DFFSX1: holds during the window, loads the tap during the hold phase |
| **DFFSX1** | D flip-flop with active-low set |
| **Mux2_1_TG** | 2:1 multiplexer built from two transmission gates |
| **MX4X1** | 4:1 multiplexer |
| **TG** | transmission gate: an NMOS and a PMOS in parallel, used as a switch |
| **`DVM_DUT`** | design under test: DVM (`DVM_I0`) + TAP_CAL on one supply |
| **`DVM_TB`** | test bench: droop source, 0-V probe, clock, `SN`, `T`, `S` sources |
| **`DVM_TOP`** | top cell: `TB` + `DUT`, with a `config` view selecting the extracted views |

## Timing quantities

| Symbol | Meaning | TT value |
|---|---|---|
| `T_w` | sampling window (`clkdiv_b` high), ≈ one clock period | 1.278 ns |
| `t_TRC` | replica delay, `clkdiv_b` → `TRC_Out` | 325.6 ps (`T = 00`) |
| `t_s` | average TDC stage delay | 47.1–47.6 ps (alternating 60 / 28 ps) |
| `t_clk2div` | divider clock-to-output, `CLK` → `clkdiv` | 192.6 ps |
| `t_buf` | clock-buffer delay, `clkdiv` → `clkdiv_b` | 124.0 ps |
| Clock path | `t_clk2div + t_buf`: when the window starts and ends relative to `CLK` | 317 ps |
| τ<sub>FO1</sub> | delay of an inverter driving one identical inverter | 10.78 ps (extracted) |
| κ | `t_s` / τ<sub>FO1</sub>: the TDC stage in units of a lightly loaded inverter | 4.4 |
| Latency | droop start (supply 10 mV below nominal) → flag at V<sub>DD</sub>/2 | 1.9–4.5 ns |

## Measurement and metrics

| Term | Meaning |
|---|---|
| **Code** | number of taps reached in a window: `32 − Σ O<k> / V_DD` (report eq. 3); 20 with no droop at TT |
| **Thermometer code** | a run of reached taps followed by unreached ones; the code is its length |
| **Tap** | one TDC latch output |
| **Hold phase** | the half of the measurement when the latches are closed and the result is read |
| **Bubble** | a tap that reads out of order in the thermometer code |
| **Aliasing** | the TDC captures an edge left over from the previous measurement, so the code jumps up instead of falling (TDC out of range) |
| **LSB** | least significant bit: one code step (13.3 mV on average) |
| **DNL** | differential nonlinearity: (width of a code − average width) / average width, in LSB |
| **INL** | integral nonlinearity: deviation of each code transition from a straight line through the end points, in LSB |
| **FWHM** | full width at half maximum: how long a droop stays deeper than half its depth |
| **False warning** | a flag level above the droop actually applied (including any flag with no droop) |
| **Over-graded / under-graded** | a droop flagged as a deeper / shallower level than it is |
| **E<sub>tot</sub>**, `E_det` | energy the DVM draws from droop start until flag0 rises |
| **Energy per cycle** | active power × clock period (173 fJ) |
| **RWP** | resolution–window product: mV/LSB × T<sub>w</sub> |
| **ERP** | energy–resolution product: energy per cycle × mV/LSB |
| **FoM1**, **FoM2** | RWP × ERP, and FoM1 × area (µm²); course figures of merit, lower is better |

## Process, corners and statistics

| Term | Meaning |
|---|---|
| **gpdk045** | Cadence generic 45-nm process design kit used for the design |
| **tt, ff, ss, fs, sf** | process corners: typical, fast, slow, fast NMOS + slow PMOS, slow NMOS + fast PMOS |
| **PVT** | process, voltage, temperature |
| **Monte Carlo (MC)** | many simulations with randomly varied device parameters |
| **Global (process) variation** | variation shared by every device on a die (die-to-die) |
| **Local variation, mismatch** | random differences between nominally identical neighbouring devices |
| **LHS** | Latin hypercube sampling: a Monte Carlo sampling method that covers the distribution evenly with few samples |
| **Pelgrom's law** | mismatch σ(ΔV<sub>T</sub>) ∝ 1/√(W·L): bigger devices match better |
| **Retiming** | moving the sampling edge of a flip-flop (here from `CLKn` to `CLK`) to gain timing margin |

## Tools and views

| Term | Meaning |
|---|---|
| **Virtuoso** | Cadence schematic and layout editor |
| **Spectre** | Cadence circuit simulator |
| **ADE L / ADE XL** | Cadence analog design environments: single runs and parametric sweeps (L), corners and Monte Carlo (XL) |
| **State** | a saved ADE setup (variables, analyses, outputs); here saved as cellviews on `DVM_TOP` |
| **Assura** | Cadence physical verification: DRC, LVS, extraction |
| **DRC** | design rule check |
| **LVS** | layout versus schematic |
| **PEX, RC extraction** | parasitic extraction of wire resistance and capacitance |
| **`av_extracted`** | the extracted view produced by Assura, simulated in place of the schematic |
| **`config` view** | a hierarchy configuration that chooses which view (schematic or `av_extracted`) each cell uses |
| **Verilog-A** | behavioural modelling language; used here only for the test-bench droop sources |

---

[← 10. FAQ](10-faq.md) · [Documentation index](README.md)
