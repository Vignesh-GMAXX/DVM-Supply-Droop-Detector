# 5. Simulation setup and reproduction guide

[← 4. Layout and extraction](04-layout-and-extraction.md) · [Documentation index](README.md) · Next: [6. Results →](06-results.md)

Everything was simulated in Cadence Virtuoso with Spectre (APS) and the gpdk045 generic 45-nm PDK (model sections `tt`, `ss`, `ff`, `fs`, `sf`). The PDK, netlists and extracted views are **not** in this repository; this chapter documents the setup so that every number can be traced and the whole flow rebuilt.

- [5.1 Library structure](#51-library-structure)
- [5.2 Test bench](#52-test-bench-dvm_tb)
- [5.3 The supply-droop stimuli (Verilog-A)](#53-the-supply-droop-stimuli-verilog-a)
- [5.4 Measurement expressions](#54-measurement-expressions)
- [5.5 Saved ADE L states](#55-saved-ade-l-states)
- [5.6 ADE XL runs](#56-ade-xl-runs)
- [5.7 Rebuilding the setup step by step](#57-rebuilding-the-setup-step-by-step)
- [5.8 Exporting data for the plotting scripts](#58-exporting-data-for-the-plotting-scripts)
- [5.9 Pitfalls we hit](#59-pitfalls-we-hit)

---

## 5.1 Library structure

```text
Project/                      Virtuoso library
├── inverter, BUF, D_latch    leaf cells (schematic, symbol, layout, av_extracted)
├── Mux2_1_TG, MX4X1, DFFSX1  leaf cells
├── TRC, TDC                  building blocks
├── DVM                       baseline monitor (instance DVM_I0 in DVM_DUT)
├── TAP_CAL                   calibration block (this work)
├── DVM_DUT                   DVM + TAP_CAL, one shared supply
├── DVM_TB                    stimuli and observation (Verilog-A droop source)
└── DVM_TOP                   DUT + TB, with a config view → av_extracted
```

`DVM_TOP` has exactly two instances, `DUT` and `TB` ([3.6](03-circuits-and-cells.md#36-design-under-test-test-bench-and-top-cell)). `DVM_TOP/config` binds **DVM** and **TAP_CAL** to their **`av_extracted`** views. Open the config view (not the plain schematic) before launching ADE, or set *Setup → Environment → Switch View List* to `spectre av_extracted cmos_sch cmos.sch schematic veriloga`. Loading a saved state does not change which view is simulated.

Top-level nets used by the expressions: `VDD_DVM` (the drooping supply), `VSS`, `CLK`, `SN`, `T0`, `T1`, `S0`, `S1`, `O<31:0>` (TDC taps), `DVM_O<2:0>` (DVM flags), `CAL_O<2:0>` (TAP_CAL flags), `clkdiv`, `clkdivB`, `clkdiv_b`, `TRC_Out`.

---

## 5.2 Test bench (`DVM_TB`)

| Instance | Settings |
|---|---|
| `VDD_droop3` (Verilog-A) | `vnom`, `vdroop`, `mode`, `tdelay`, `tdown`, `twidth`, `tup` → net `VSRC` |
| `V0` vdc 0 V | supply probe between `VSRC` and `VDD_DROOP` (current `IT("/TB/V0/PLUS")`) |
| `V1` vpulse (`CLK`) | `clklo` → `clkhi`, period `tclk`, rise/fall 10 ps, width `tclk/2 − 10p` |
| `V2` vpulse (`SN`) | 0 → 1 with 20-ps rise after 200 ps: active-low set released |
| `V3`–`V6` vdc | `T0`, `T1`, `S0`, `S1` |
| `V7` vdc 0 V | `VSS` → ground |
| noConn × 7 | on the observed outputs, so the top level has no dangling nets |

### Design variables (base values)

| Variable | Value | Meaning |
|---|---|---|
| `vnom` | 1 | nominal supply (V) |
| `vdroop` | 0 | droop depth (V): V<sub>DD</sub> = `vnom − vdroop` at the bottom |
| `mode` | 0 | droop shape (0: raised-cosine edges and flat bottom; 1: RC-like exponential droop) |
| `tdelay` | 9.9n | droop start |
| `tdown` / `twidth` / `tup` | 2n / 10n / 5n | fall, flat bottom, recovery |
| `tauf` / `taur` | 1n / 3n | fall / recovery time constants for `mode = 1` (not used in the results) |
| `tclk` | 1.25n | 800-MHz clock |
| `clklo` / `clkhi` | 0 / 1 | clock levels (`clkhi = 0` stops the clock for leakage) |
| `T0`, `T1` | 0 | TRC trim (`T` = T1 T0) |
| `S0`, `S1` | 0 | TAP_CAL tap table (`S` = S1 S0) |

**Accuracy.** The `state_tt` and leakage states use Spectre's *conservative* error preset; the corner and sweep states use *moderate*. Power, an average of a very spiky supply current, is the output most sensitive to the simulator's time step.

---

## 5.3 The supply-droop stimuli (Verilog-A)

Verilog-A is used **only** to generate the supply; the DVM and TAP_CAL are transistor level. Sources are in [`veriloga/`](../veriloga).

```
V_DD(t) = vnom − vdroop · x(t)
x(t) = ½(1 − cos(π(t − tdelay)/tdown))     during the fall (tdown)
     = 1                                  at the bottom (twidth)
     = ½(1 + cos(π(t − t2)/tup))          during the recovery (tup)
```

| File | Waveform | Used for |
|---|---|---|
| `VDD_droop3.va` | one droop; with `twidth = 0`, `tdown = tup = w` a V-shaped droop of FWHM `w` | every ADE L state; the corner sweep |
| `VDD_droop_train_v3_tt27.va` | six rounded droops of different depth and shape | droop train at tt 27 °C (Fig. 6a) |
| `VDD_droop_train.va` | six droops whose bottom is exactly 5 / 10 / 10 / 15 / 15 / 5 % | droop train at ff 125 °C (Fig. 6b) |
| `VDD_droop_matrix.va` | 40 Gaussian droops: 8 depths × 5 widths, 8-ns gaps | detection map (Fig. 7) |

A `$bound_step` limits the simulator step to `min(tdown, tup)/20` while the supply is moving, so the droop edges are resolved.

---

## 5.4 Measurement expressions

All are evaluated on transistor-level nets of the top cell. `/DUT/DVM_I0/VDD` is the DVM's own supply terminal, so its power excludes TAP_CAL and the test bench. Save the terminal currents `/DUT/VDD` and `/DUT/DVM_I0/VDD` (*Outputs → To Be Saved → Select On Schematic*).

```text
;; --- Code and flags ---
code_droop : 32 - (value(VT("/O<0>") 20n) + ... + value(VT("/O<31>") 20n))
             / value(VT("/VDD_DVM") 20n)                      ; eq. (3), at the droop bottom
code_nom   : same at 10n (before the droop)
code17.5   : same at 17.5n                                    ; state_static
dflag0     : ymax(clip(VT("/DVM_O<0>") 10n 40n))              ; dflag1, dflag2: DVM_O<1>, <2>
cflag0     : ymax(clip(VT("/CAL_O<0>") 10n 40n))              ; cflag1, cflag2 likewise
sflag0     : ymax(clip(VT("/DVM_O<0>") 14n 18n))              ; state_static
droop_true : VAR("vnom") - ymin(clip(VT("/VDD_DVM") 2n 30n))

;; --- Latency and energy per detection ---
latency0 : cross(clip(VT("/DVM_O<0>") 10n 40n) 0.5 1 "rising")
         - cross(VT("/VDD_DVM") (VAR("vnom")-0.01) 1 "falling")    ; latency1, latency2 likewise
clat0    : as latency0 with CAL_O<0>
E_det    : integ(clip((IT("/DUT/DVM_I0/VDD")*VT("/VDD_DVM"))
                 cross(VT("/VDD_DVM") (VAR("vnom")-0.01) 1 "falling")
                 cross(clip(VT("/DVM_O<0>") 10n 40n) 0.5 1 "rising")))

;; --- Power and leakage ---
P_dvm     : average(clip((IT("/DUT/DVM_I0/VDD")*VT("/VDD_DVM")) 12.5n 22.5n))
E_cyc     : P_dvm expression * VAR("tclk")
Pleak_dvm : average(clip((IT("/DUT/DVM_I0/VDD")*VT("/VDD_DVM")) 20n 25n))   ; clkhi = 0
Pleak_tot : same with IT("/DUT/VDD")
clk_swing : ymax(clip(VT("/clkdiv_b") 15n 25n)) - ymin(clip(VT("/clkdiv_b") 15n 25n))   ; ≈ 0: clock really stopped

;; --- Clock path and replica ---
t_clk2div : cross(clip(VT("/clkdiv") 10n 10.9n) 0.5 1 "either")
          - cross(clip(VT("/CLK") 9.9n 10.9n) 0.5 1 "rising")
t_buf     : cross(clip(VT("/clkdiv_b") 10n 11n) 0.5 1 "either")
          - cross(clip(VT("/clkdiv") 10n 10.9n) 0.5 1 "either")
t_TRC     : cross(clip(VT("/TRC_Out") cross(clip(VT("/clkdiv_b") 10n 11n) 0.5 1 "either") 12.5n) 0.5 1 "either")
          - cross(clip(VT("/clkdiv_b") 10n 11n) 0.5 1 "either")
```

**Definitions behind the expressions**

| Quantity | Definition |
|---|---|
| Code | eq. (3): count of reached taps, read from the latch voltages in the hold phase |
| Flag level | highest value of `DVM_O<k>` (or `CAL_O<k>`) during the run; > 0.5 V means the flag fired |
| Detection latency | from the supply crossing `vnom − 10 mV` (droop start) to the flag crossing V<sub>DD</sub>/2 |
| E_det (E<sub>tot</sub>) | energy the DVM draws from its supply terminal between those two instants |
| Active power | average DVM-terminal power over 12.5–22.5 ns (8 clock cycles) |
| Energy per cycle | P<sub>act</sub> × `tclk` (one measurement takes two cycles) |
| Leakage | average DVM-terminal power with the clock held low |

---

## 5.5 Saved ADE L states

Eight states saved as **cellviews** on `DVM_TOP` reproduce the post-layout and worst-corner figures of merit. ADE L does not store parametric sweeps in a state, so each state's *Description* gives the sweep to re-enter (*Tools → Parametric Analysis*).

| State | Corner, settings | Parametric sweep | Stop | Figures of merit | Result |
|---|---|---|---|---|---|
| `state_tt` | tt 27 °C, conservative | vdroop 0 0.05 0.1 0.15 | 40n | levels, latency, power, E/cycle, E<sub>tot</sub> | code 20/16/12/9; flags 000/100/110/111; P<sub>dvm</sub> 138.4 µW; 173 fJ; latency 1.9–4.5 ns |
| `state_static` | tt 27 °C, moderate | vdroop 0:0.0025:0.15 | 18n | resolution, DNL, INL, flag switching | 13.25 mV/LSB; DNL −0.81/+0.89; INL −0.89/+0.08; flags at 0.9575/0.905/0.8675 V |
| `state_short` | tt 27 °C; twidth 0, tdown = tup = `w` | w 1n 1.5n 2n 3n × vdroop 0.05 0.1 0.15 × tdelay 9.9n 11.15n | 30n | shortest flagged droop | 5 %: 2 ns, 10 %: 1 ns, 15 %: 1 ns FWHM (best phase) |
| `state_leak_tt` | tt 27 °C, clkhi 0 | – | 25n | leakage | 5.67 nW DVM (6.67 nW with TAP_CAL) |
| `state_leak_worst` | ff 125 °C, clkhi 0 | – | 25n | worst leakage | 90.2 nW DVM (112 nW) |
| `state_worst` | ff −40 °C, T = 11 | vdroop 0 0.05 0.1 0.15 | 40n | worst active power | code 27/22/18/12; 202.3 µW; 253 fJ |
| `state_ff125` | ff 125 °C, S = 01 | vdroop 0 0.05 0.1 0.15 | 40n | DVM false alarm vs TAP_CAL | DVM 100 at 0 % (false), TAP_CAL 000; 187.3 µW |
| `state_ss27` | ss 27 °C, S = 10 | vdroop 0 0.05 0.1 0.15 | 40n | worst-corner latency, false alarm | TAP_CAL latency 4.94 ns at 10 %; DVM 100 / CAL 000 at 0 % |

The exported results of these states are in [`data/ade_l_states/`](../data/ade_l_states).

---

## 5.6 ADE XL runs

These results are not in the ADE L states (ADE XL was used for sweeps over corners and for Monte Carlo):

| Run | Views | Setup | Data |
|---|---|---|---|
| Corner × droop sweep (report Table V) | DVM extracted, TAP_CAL schematic | 15 corners × vdroop 0 / 0.05 / 0.1 / 0.15, S and T per corner ([§7](07-pvt-and-calibration.md)) | [`data/ade_xl/corners/`](../data/ade_xl/corners) |
| Single droops and TDC taps at tt 27 °C | DVM extracted | vdroop 0 / 0.05 / 0.1 / 0.15, all taps and clocks saved | `W1_*.csv.gz`, `tt27_*.npz` |
| Droop trains (Fig. 6) | DVM extracted, TAP_CAL schematic | tt 27 °C S = 00; ff 125 °C S = 01 | [`data/droop_trains/`](../data/droop_trains) |
| Detection map (Fig. 7) | DVM extracted, TAP_CAL schematic | 40 Gaussian droops in one transient, tt 27 °C | `matrix2_res.json`, `MATRIX2_tt27.csv.gz` |
| Monte Carlo (Fig. 8) | **schematic** | 100 samples, Latin hypercube, tt 27 °C, 1 GHz, T = 11, no droop; process + mismatch and mismatch only | [`data/montecarlo/`](../data/montecarlo) |

Monte Carlo was run on the schematic views, at the pre-layout design point (1 GHz, T = 11), which puts the nominal code (≈ 21) inside the TDC range as in the post-layout design ([8. Monte Carlo](08-monte-carlo.md)).

---

## 5.7 Rebuilding the setup step by step

1. **Leaf cells.** Draw INV (260/390 nm), BUF, the TG D-latch, Mux2_1_TG (145/215 nm), MX4X1 and DFFSX1 with symbols and pin directions. Check and save with no warnings.
2. **Blocks.** TRC: 16 BUF in four groups + MX4X1 on `T1 T0`. TDC: 32 × (INV + latch), latch enable `clkdiv_b`, a polarity inverter after every second latch, taps `O<31:0>` with `O<31>` first.
3. **DVM.** Divider (DFFSX1 + INV feedback), 4× and 16× clock-buffer inverters, `CLKn` inverter, TRC, TDC and three decision stages on `O<15>`, `O<19>`, `O<22>` clocked by `CLKn` ([3.4](03-circuits-and-cells.md#34-dvm-top-level)).
4. **TAP_CAL.** Three MX4X1 on `S1 S0` with the tap table of [§2.8](02-architecture.md#28-tap_cal-corner-calibrated-thresholds-this-work) (D inputs tied to V<sub>SS</sub>) and three decision stages clocked by `CLK`.
5. **Layout, DRC, LVS, extraction** of every cell, then of TRC, TDC, DVM and TAP_CAL; extract to `av_extracted`.
6. **DVM_DUT, DVM_TB, DVM_TOP** as in [3.6](03-circuits-and-cells.md#36-design-under-test-test-bench-and-top-cell); compile `VDD_droop3.va` as a Verilog-A cell view.
7. **Config view** on `DVM_TOP` binding DVM and TAP_CAL to `av_extracted`.
8. **ADE L.** Add the design variables of [§5.2](#52-test-bench-dvm_tb), a 40-ns transient, the outputs of [§5.4](#54-measurement-expressions) and the saved terminal currents. Save each state of [§5.5](#55-saved-ade-l-states) as a cellview **before** running it, and write its sweep into the description.
9. **ADE XL** for corners (one corner per column with its own `S`, `T`) and Monte Carlo.

---

## 5.8 Exporting data for the plotting scripts

| Export | How | Used by |
|---|---|---|
| Scalar outputs of a sweep or state | ADE results → select all → *Send To → Table* → save CSV | `make_dnl.py`, the corner figures |
| ADE XL corner table | *Results → Export → CSV* (one column per corner, one block per sweep point) | [`adexl_table.py`](../scripts/adexl_table.py) parses it |
| Waveforms | waveform window → select traces → *Export → CSV* (X/Y column pairs) | `make_wave.py`, `make_train4.py`, and the prep script that builds `tt27_*.npz` |

Large waveform exports are stored gzip-compressed; [`scripts/reproduce_figures.sh`](../scripts/reproduce_figures.sh) decompresses them into `build/`.

---

## 5.9 Pitfalls we hit

| Pitfall | What happened | Rule |
|---|---|---|
| Latency at points where a flag never fired | ADE subtracts a 1-point family (flag crossing) from a 3-point family (supply crossing) and fills the missing points | read a latency only where that flag actually fired |
| Parametric sweep not stored in ADE L states | loading a state gave a single run | write the sweep in the state description |
| Plain schematic simulated after an export | a state does not set the design view, so the copy simulated schematic views (code 32) | open the config view or set the switch view list |
| Wrong droop source | a test bench still held the droop-train source, so `vdroop` changed nothing | check `droop_true` in every run |
| Power depends on the solver step | the same point gave different averages in different runs | measure power at the DVM terminal, keep one accuracy preset, report the state's value |
| Probe power includes the test bench | the 0-V probe measured DVM + clock-path drivers (181 µW) | use the DVM terminal current (138.4 µW) |
| Virtuoso crash before saving | a state was lost | save the state before running |

---

[← 4. Layout and extraction](04-layout-and-extraction.md) · [Documentation index](README.md) · Next: [6. Results →](06-results.md)
