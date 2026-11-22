# Simulation setup

Everything here was simulated in Cadence Virtuoso (Spectre) with the gpdk045 generic 45-nm PDK. The PDK and the extracted views are **not** in this repository; this page documents the set-up so the numbers in the report can be traced.

## Top cell

`Project/DVM_TOP` has exactly two instances:

| Instance | Cell | Contents |
|---|---|---|
| `DUT` | `DVM_DUT` | `DVM_I0` (the DVM) + `TAP_CAL`, sharing one supply |
| `TB` | `DVM_TB` | droop source, clock, reset, trim/select sources, supply probe |

`DVM_TOP/config` binds **DVM → av_extracted** and **TAP_CAL → av_extracted** (post-layout, parasitic RC). The saved ADE L states also carry the switch view list `spectre av_extracted cmos_sch cmos.sch schematic veriloga`, so opening the plain schematic simulates the extracted views too.

Top-level nets used by the expressions: `VDD_DVM` (droop supply), `VSS`, `CLK`, `SN`, `T0`, `T1`, `S0`, `S1`, `O<31:0>` (TDC taps), `DVM_O<2:0>` (DVM flags), `CAL_O<2:0>` (TAP_CAL flags), `clkdiv`, `clkdivB`, `clkdiv_b`, `TRC_Out`.

## Test bench (`DVM_TB`)

| Instance | Settings |
|---|---|
| `VDD_droop3` (Verilog-A) | `vnom`, `vdroop`, `mode`, `tdelay`, `tdown`, `twidth`, `tup` → net `VSRC` |
| `V0` vdc 0 V | supply probe between `VSRC` and `VDD_DROOP` |
| `V1` vpulse (CLK) | `clklo` → `clkhi`, period `tclk`, rise/fall 10 ps, width `tclk/2 − 10p` |
| `V2` vpulse (SN) | active-low set released at 200 ps |
| `V3`–`V6` vdc | `T0`, `T1`, `S0`, `S1` |

### Design variables (base values)

| Variable | Value | Meaning |
|---|---|---|
| `vnom` | 1 | nominal supply (V) |
| `vdroop` | 0 | droop depth (V); VDD = vnom − vdroop |
| `mode` | 0 | droop shape (0 = raised-cosine edges) |
| `tdelay` | 9.9n | droop start |
| `tdown` / `twidth` / `tup` | 2n / 10n / 5n | fall, hold, recovery |
| `tclk` | 1.25n | 800 MHz clock |
| `clklo` / `clkhi` | 0 / 1 | clock levels (`clkhi = 0` stops the clock for leakage) |
| `T0`, `T1` | 0 | TRC trim (T = 00 nominal, 11 at ff −40 °C) |
| `S0`, `S1` | 0 | TAP_CAL tap-table select (per corner) |

## Saved ADE L states (Cellview, on `DVM_TOP`)

ADE L does not store parametric sweeps in a state, so each state's *Description* lists the sweep to re-enter (Tools → Parametric Analysis).

| State | Corner, settings | Parametric sweep | Stop | FoMs | Result |
|---|---|---|---|---|---|
| `state_tt` | tt 27 °C, conservative | vdroop 0 0.05 0.1 0.15 | 40n | levels, latency, power, E/cycle, E_det | code 20/16/12/9; flags 000/100/110/111; P_dvm 138.4 µW; 173 fJ; latency 1.9–4.5 ns |
| `state_static` | tt 27 °C, moderate | vdroop 0:0.0025:0.15 | 18n | resolution, DNL, INL, flag switching | 13.25 mV/LSB; DNL −0.81/+0.89; INL −0.89/+0.08; flags at 0.9575/0.905/0.8675 V |
| `state_short` | tt 27 °C; twidth 0, tdown = tup = `w` | w 1n 1.5n 2n 3n × vdroop 0.05 0.1 0.15 × tdelay 9.9n 11.15n | 30n | shortest flagged droop | 5 %: 2 ns, 10 %: 1 ns, 15 %: 1 ns FWHM (best phase) |
| `state_leak_tt` | tt 27 °C, clkhi 0 | – | 25n | leakage | 5.67 nW DVM (6.67 nW with TAP_CAL) |
| `state_leak_worst` | ff 125 °C, clkhi 0 | – | 25n | worst leakage | 90.2 nW DVM (112 nW) |
| `state_worst` | ff −40 °C, T = 11 | vdroop 0 0.05 0.1 0.15 | 40n | worst active power | code 27/22/18/12; 202.3 µW; 253 fJ |
| `state_ff125` | ff 125 °C, S = 01 | vdroop 0 0.05 0.1 0.15 | 40n | DVM false alarm vs TAP_CAL | DVM 100 at 0 % (false), TAP_CAL 000; 187.3 µW |
| `state_ss27` | ss 27 °C, S = 10 | vdroop 0 0.05 0.1 0.15 | 40n | worst-corner latency, false alarm | TAP_CAL latency 4.94 ns at 10 %; DVM 100 / CAL 000 at 0 % |

**Reading rule.** A latency output only counts where that flag actually fired: ADE fills missing family points with the existing crossing time, so values at points where a flag stayed low are not real.

## Measurement expressions (ADE L outputs)

```text
;; --- Code and flags ---
code_droop : 32 - (value(VT("/O<0>") 20n) + ... + value(VT("/O<31>") 20n))
             / value(VT("/VDD_DVM") 20n)
code17.5   : same at 17.5n                                  ; state_static
dflag0     : ymax(clip(VT("/DVM_O<0>") 10n 40n))            ; dflag1, dflag2: DVM_O<1>, <2>
cflag0     : ymax(clip(VT("/CAL_O<0>") 10n 40n))            ; cflag1, cflag2 likewise
sflag0     : ymax(clip(VT("/DVM_O<0>") 14n 18n))            ; state_static
droop_true : VAR("vnom") - ymin(clip(VT("/VDD_DVM") 2n 30n))

;; --- Latency and energy per detection ---
latency0 : cross(clip(VT("/DVM_O<0>") 10n 40n) 0.5 1 "rising")
         - cross(VT("/VDD_DVM") (VAR("vnom")-0.01) 1 "falling")   ; latency1, latency2 likewise
clat0    : as latency0 with CAL_O<0>
E_det    : integ(clip((IT("/DUT/DVM_I0/VDD")*VT("/VDD_DVM"))
                 cross(VT("/VDD_DVM") (VAR("vnom")-0.01) 1 "falling")
                 cross(clip(VT("/DVM_O<0>") 10n 40n) 0.5 1 "rising")))

;; --- Power and leakage ---
P_dvm     : average(clip((IT("/DUT/DVM_I0/VDD")*VT("/VDD_DVM")) 12.5n 22.5n))
E_cyc     : P_dvm expression * VAR("tclk")
Pleak_dvm : average(clip((IT("/DUT/DVM_I0/VDD")*VT("/VDD_DVM")) 20n 25n))   ; clkhi = 0
Pleak_tot : same with IT("/DUT/VDD")
clk_swing : ymax(clip(VT("/clkdiv_b") 15n 25n)) - ymin(clip(VT("/clkdiv_b") 15n 25n))   ; about 0

;; --- Clock path and replica ---
t_clk2div : cross(clip(VT("/clkdiv") 10n 10.9n) 0.5 1 "either")
          - cross(clip(VT("/CLK") 9.9n 10.9n) 0.5 1 "rising")
t_buf     : cross(clip(VT("/clkdiv_b") 10n 11n) 0.5 1 "either")
          - cross(clip(VT("/clkdiv") 10n 10.9n) 0.5 1 "either")
t_TRC     : cross(clip(VT("/TRC_Out") cross(clip(VT("/clkdiv_b") 10n 11n) 0.5 1 "either") 12.5n) 0.5 1 "either")
          - cross(clip(VT("/clkdiv_b") 10n 11n) 0.5 1 "either")
```

Save the terminal currents `/DUT/VDD` and `/DUT/DVM_I0/VDD` (Outputs → To Be Saved → Select On Schematic) for the power expressions.

## ADE XL runs (not in the ADE L states)

The corner–droop sweep (Table V of the report, 15 corners × 4 droops), the droop trains (Fig. 6), the detection map (Fig. 7) and Monte Carlo (Fig. 8, schematic, 100 samples) were run in ADE XL. The DVM is extracted in all of them; TAP_CAL is the schematic view in the corner sweep, trains and map. Their exported results are in [`data/`](../data).

## Verilog-A

Verilog-A is used **only** for test-bench stimuli. See [`veriloga/`](../veriloga):

| File | Used for |
|---|---|
| `VDD_droop3.va` | single droop with raised-cosine edges; all ADE L states. With `twidth = 0`, `tdown = tup = w` it gives a V-shaped droop of FWHM `w` (`state_short`). |
| `VDD_droop_train_v3_tt27.va` | six-event droop train with overshoot, tt 27 °C (Fig. 6a) |
| `VDD_droop_train.va` | droop train with exact depths, ff 125 °C (Fig. 6b) |
| `VDD_droop_matrix.va` | 40 Gaussian droops, 8 depths × 5 widths (Fig. 7) |
