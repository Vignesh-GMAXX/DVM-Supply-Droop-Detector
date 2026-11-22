# 10. Frequently asked questions

[← 9. Design journey](09-design-journey.md) · [Documentation index](README.md) · Next: [Glossary →](glossary.md)

Questions we were asked, or expected to be asked, about this design, with short answers and a pointer to the full explanation. Numbers: post-layout, TT, 27 °C, 800 MHz, unless stated.

**Contents:** [The idea](#the-idea) · [Architecture](#architecture) · [Resolution and linearity](#resolution-and-linearity) · [Decision and timing](#decision-and-timing) · [Performance](#performance) · [Corners and calibration](#corners-and-calibration) · [Monte Carlo and layout](#monte-carlo-and-layout) · [Method](#method)

---

## The idea

<details>
<summary><b>What does this design do, in one sentence?</b></summary>

It turns the supply voltage into a delay measurement every 2.5 ns and raises one, two or three flags when the supply has drooped by 5, 10 or 15 %, using only digital cells (inverters, latches, multiplexers, flip-flops) and the clock. [1. Background](01-background.md)
</details>

<details>
<summary><b>Why monitor supply droops at all?</b></summary>

A droop slows every gate on the die. Without a monitor the clock has to keep a timing margin (guardband) for the worst droop all the time. With a fast monitor the chip can react only when a droop happens (stretch the clock, throttle), so the permanent margin can be smaller. [1.2](01-background.md#12-why-a-droop-matters)
</details>

<details>
<summary><b>Why an all-digital monitor and not a voltage comparator?</b></summary>

A comparator needs a quiet reference voltage and analog bias, and it measures volts, not what the logic actually feels. The DVM needs only the clock, is built from the same kind of cells as the logic it protects, and measures delay, the quantity that causes timing failures. The price is that it also sees process and temperature, which is why it needs calibration. [1.4](01-background.md#14-families-of-droop-monitors)
</details>

<details>
<summary><b>So does it measure voltage or delay?</b></summary>

Delay. The code is the number of inverter stages an edge passes in a fixed time window. A droop slows the stages and lowers the code, but so does a slow die or a hot die. Calibration (`T`, `S`) separates the two. [7.2](07-pvt-and-calibration.md#what-sets-the-code-at-each-corner)
</details>

---

## Architecture

<details>
<summary><b>Why is there a replica delay (TRC) in front of the TDC?</b></summary>

It has two jobs. It stands in for the logic being protected: the TDC measures how much of the clock period is left after the replica, and a droop slows both. And it positions the measurement: it places the no-droop code in the middle of the TDC (20 of 32), with room for faster corners above and droops below. Because it is tunable (`T`), it can also bring a fast die's code back into range. [2.3](02-architecture.md#23-tunable-replica-circuit-trc)
</details>

<details>
<summary><b>Why one measurement every two clock cycles?</b></summary>

The latches are enabled by the clock divided by two: transparent for one period (the measurement window) and holding for the next (the hold phase), during which the result is read. 800 MHz ÷ 2 gives 400 million measurements per second. [2.2](02-architecture.md#22-clocking-one-measurement-every-two-cycles)
</details>

<details>
<summary><b>Why latches and not flip-flops on the TDC taps?</b></summary>

A latch is transparent during the window and freezes its tap when the enable falls, so one edge of `clkdiv_b` captures all 32 taps at once. A latch is also smaller than a flip-flop. [3.2](03-circuits-and-cells.md#32-leaf-cells)
</details>

<details>
<summary><b>Why does a reached tap read 0?</b></summary>

Every chain inverter flips the edge, so consecutive taps see opposite polarities. A polarity inverter after every second latch makes all taps follow one rule: reached = 0. The code is then 32 minus the number of taps still at 1 (eq. 3). [2.5](02-architecture.md#25-from-taps-to-a-code)
</details>

<details>
<summary><b>Why is <code>O&lt;31&gt;</code> the first stage?</b></summary>

That is the naming in the schematic: the edge enters at `O<31>` and travels towards `O<0>`. A droop "un-reaches" the low-index taps first, so the flags use mid-range taps (`O<15>`, `O<19>`, `O<22>`). [2.4](02-architecture.md#24-time-to-digital-converter-tdc)
</details>

<details>
<summary><b>Why 800 MHz when the schematic worked at 1 GHz?</b></summary>

After extraction the TDC stage slowed from 27 to 47 ps. In a 1-ns window too few stages fit after the replica, and the 1-GHz post-layout design flagged a 5 % droop with no droop present. The 1.25-ns window at 800 MHz gives a no-droop code of 20 with room on both sides. [9. Design journey](09-design-journey.md#phase-4-three-fixes)
</details>

<details>
<summary><b>How were the taps <code>O&lt;15&gt;</code>, <code>O&lt;19&gt;</code>, <code>O&lt;22&gt;</code> chosen?</b></summary>

Tap `O<k>` stays unreached (flag = 1) when the code is ≤ 31 − k. The no-droop code is 20 and static supplies of 0.95 / 0.90 / 0.85 V read 16 / 12 / about 9, so the taps are 31 − 16 = 15, 31 − 12 = 19 and 31 − 9 = 22. [2.7](02-architecture.md#27-decision-stages-and-flags)
</details>

---

## Resolution and linearity

<details>
<summary><b>What sets the resolution?</b></summary>

The stage delay relative to the window: a slow-down by the fraction δ moves the code by about δ · T<sub>w</sub> / t<sub>s</sub> ≈ 27 δ codes (eq. 2). Measured: **13.3 mV per code** on average. A finer resolution needs a faster stage (or an interpolating TDC), not more stages; more stages only extend the range. [2.6](02-architecture.md#26-design-equations-with-our-numbers)
</details>

<details>
<summary><b>What is κ, and why is yours 4.4 when Bowman's is 1.4?</b></summary>

κ = t<sub>s</sub> / τ<sub>FO1</sub>: the TDC stage delay in units of an inverter driving one inverter. Ours is higher because each chain inverter also drives a latch transmission gate (3.0 in the schematic) and, after layout, the wiring between stages (4.4). [3.7](03-circuits-and-cells.md#37-measured-cell-delays)
</details>

<details>
<summary><b>Why are even codes 22.5 mV wide and odd codes only 2.5–5 mV?</b></summary>

The edge crosses alternate stages as a rising and a falling transition, and the unit inverter is not sized for equal rise and fall delay, so the taps are alternately ~60 ps and ~28 ps apart. DNL −0.81 to +0.89 LSB. Sizing the inverter for equal t<sub>pLH</sub> and t<sub>pHL</sub> would even it out. [6. Results](06-results.md#static-transfer-curve-resolution-dnl-inl)
</details>

<details>
<summary><b>What is a bubble, and why does the 15 % code include one?</b></summary>

A tap that reads "reached" out of order, so the taps are not a clean run of zeros followed by ones. At a 15 % droop `O<0>`, the last stage, still holds an edge from the previous measurement and reads 0, so the summed code reads 9 instead of 8. The flags use taps 15–22 and are not affected. [6. Results](06-results.md#inside-the-tdc-the-edge-race)
</details>

<details>
<summary><b>What is aliasing here?</b></summary>

When the stages become so slow that the edge of the previous measurement is still travelling through the chain when the latches open again, the latches capture a mix of two edges and the code jumps **up** instead of falling. Below about 0.856 V at TT, and beyond 5 % droop at hot corners. [7.3](07-pvt-and-calibration.md#73-code-under-droop-at-every-corner)
</details>

<details>
<summary><b>Why do the flags switch slightly before 5, 10 and 15 %?</b></summary>

The threshold codes 16 / 12 / 9 are first reached at 0.9575 / 0.905 / 0.8675 V (4.25 / 9.5 / 13.25 % droop). Switching a little early means a droop that reaches the level is always flagged. [6. Results](06-results.md#static-transfer-curve-resolution-dnl-inl)
</details>

---

## Decision and timing

<details>
<summary><b>What does the 2:1 transmission-gate mux in each decision stage do?</b></summary>

During the window it feeds the flip-flop's own output back (hold); during the hold phase it passes the tap. The flag therefore never sees the taps while they are still moving. [2.7](02-architecture.md#27-decision-stages-and-flags)
</details>

<details>
<summary><b>What is wrong with clocking the decision on <code>CLKn</code>?</b></summary>

`CLKn` rises 625 ps after the clock edge that closes the latches, but the latches close only after the clock path (317 ps at TT). That leaves 281 ps at TT, 91 ps at the bottom of a 15 % droop and too little at ss 125 °C, where flip-flops clocked this way stopped loading (found while testing TAP_CAL). [7.5](07-pvt-and-calibration.md#75-why-each-failing-corner-fails)
</details>

<details>
<summary><b>Why does TAP_CAL sample on the rising <code>CLK</code> edge, and what does it cost?</b></summary>

That edge ends the hold phase, 625 ps later, so the latches have long settled at every corner and droop. The cost is about 0.5 ns of latency; TAP_CAL as a whole adds about 11 µW (6 %). [2.8](02-architecture.md#end-of-hold-sampling-retiming)
</details>

---

## Performance

<details>
<summary><b>What sets the detection latency?</b></summary>

The time for the supply to reach the level, plus the wait for a measurement window that sees the full depth (one every 2.5 ns, 1.28 ns long), plus the decision (a few hundred ps from latch close to the flag). Hence 1.9–4.5 ns at TT. [6. Results](06-results.md#droop-response-and-detection-latency)
</details>

<details>
<summary><b>Why is the latency shorter for a 15 % droop (1.95 ns) than for a 5 % one (4.10 ns)?</b></summary>

A 15 % droop passes the 5 % level early in its 2-ns fall, so flag0 fires in the next measurement. A 5 % droop reaches its level only at the bottom, and since the threshold sits exactly on code 16, the next full measurement is needed. [6. Results](06-results.md#droop-response-and-detection-latency)
</details>

<details>
<summary><b>Can it catch a 1-ns droop?</b></summary>

Sometimes. A 10 % or 15 % droop of 1 ns FWHM is flagged (one level low) if it falls inside a measurement window; whether it does depends on its phase relative to the clock. Full grading needs about 8 ns. [6. Results](06-results.md#shortest-flagged-droop)
</details>

<details>
<summary><b>Where does the power go?</b></summary>

Almost all of it is switching power (leakage is 5.67 nW against 138.4 µW): the divider and clock buffer every cycle, and the latch enables, the replica and the TDC chain twice per measurement. [6. Results](06-results.md#power-energy-and-leakage)
</details>

<details>
<summary><b>Why is the energy per cycle 173 fJ but 346 fJ per measurement?</b></summary>

173 fJ is P / f<sub>CLK</sub> = 138.4 µW × 1.25 ns, the course definition. One measurement takes two cycles, so it costs twice that.
</details>

<details>
<summary><b>What are FoM1 and FoM2?</b></summary>

Course figures of merit, lower is better. RWP = resolution × window = 16.6 mV·ns; ERP = energy per cycle × resolution = 2.29 pJ·mV; FoM1 = RWP × ERP = 3.80 × 10⁴; FoM2 = FoM1 × area (µm²) = 2.50 × 10⁷. [6. Results](06-results.md#figure-of-merit-summary)
</details>

---

## Corners and calibration

<details>
<summary><b>Why do fixed thresholds fail at corners?</b></summary>

Process and temperature move the no-droop code from 9 to 28 (with the trim), while a 15 % droop moves it by 11. A slow die looks like a drooped supply: 6 of 15 corners raise flags with no droop. [7. PVT](07-pvt-and-calibration.md)
</details>

<details>
<summary><b>Why can't the trim <code>T</code> fix slow corners?</b></summary>

`T` adds buffers to the replica, so it can only lower the code. `T = 00` is already the shortest replica, so a slow die's low code cannot be raised. TAP_CAL moves the thresholds down instead. [7.6](07-pvt-and-calibration.md#76-the-two-calibration-knobs)
</details>

<details>
<summary><b>How is <code>S</code> chosen?</b></summary>

From one no-droop code reading per die: ≈ 20 → `S = 00`, ≈ 16 → 01, 12–14 → 10, ≈ 9 → 11 (disabled). In this study `S` and `T` are set per corner, i.e. per process and temperature. [7.7](07-pvt-and-calibration.md#calibration-procedure)
</details>

<details>
<summary><b>Why is ss 125 °C disabled rather than fixed?</b></summary>

Its no-droop code is 9, at the bottom of the TDC's range: any droop makes it alias, so no tap gives a reliable answer. Disabling avoids false alarms; fixing it needs a longer or faster TDC. [7.5](07-pvt-and-calibration.md#75-why-each-failing-corner-fails)
</details>

<details>
<summary><b>Why does ff −40 °C miss 5 % and 10 %?</b></summary>

Even with the longest replica its code is 28, and a 5 % droop only brings it to 22, still above every threshold. It needs more trim range. [7.5](07-pvt-and-calibration.md#75-why-each-failing-corner-fails)
</details>

<details>
<summary><b>Does TAP_CAL change the DVM?</b></summary>

No. It is a separate block that reads `O<26:15>`; the DVM, its layout and its flags are unchanged, which is why both sets of flags can be compared in the same run. [3.5](03-circuits-and-cells.md#35-tap_cal)
</details>

---

## Monte Carlo and layout

<details>
<summary><b>Why is the Monte Carlo on the schematic and at 1 GHz?</b></summary>

It was run on the schematic views; at 800 MHz the faster schematic TDC is at or near saturation (30–32), while 1 GHz with `T = 11` puts the nominal code at 22, close to the post-layout operating point. [8.1](08-monte-carlo.md#81-setup)
</details>

<details>
<summary><b>What does "4.3σ" mean?</b></summary>

The mean no-droop code (20.9) is 4.3 standard deviations (1.0) above the point where flag0 would fire (16.5). With mismatch alone it is 8.1σ. No sample of 100 raised a flag. [8.2](08-monte-carlo.md#82-results)
</details>

<details>
<summary><b>Why no common-centroid layout, dummies or guard rings?</b></summary>

They reduce local mismatch, but Monte Carlo shows the variation is mostly global (94 % of the replica's variance), which layout matching cannot remove. Per-die calibration handles it. [8.4](08-monte-carlo.md#84-what-it-means-for-the-design)
</details>

---

## Method

<details>
<summary><b>Is any part of the measurement behavioural?</b></summary>

Only the test-bench droop source is Verilog-A. The code is computed from the 32 latch voltages, the flags are the decision flip-flop outputs, and power is measured at the DVM's own supply terminal. [5.4](05-simulation-setup.md#54-measurement-expressions)
</details>

<details>
<summary><b>How do you know the numbers come from the extracted layout?</b></summary>

A `config` view binds the DVM and TAP_CAL to their `av_extracted` views. There is also a built-in check: the schematic reads code 32 (saturated) at 800 MHz, the extracted design reads 20. [5.9](05-simulation-setup.md#59-pitfalls-we-hit)
</details>

<details>
<summary><b>Is the comparison with published monitors fair?</b></summary>

Only roughly: the others are in 22–90 nm, most are silicon measurements while ours is post-layout simulation, and their energy per cycle is derived here as power / clock frequency. The table marks what each paper did not report. [6. Results](06-results.md#comparison-with-published-supply-droop-monitors)
</details>

<details>
<summary><b>What would you improve first?</b></summary>

Move each tap one code earlier (full grading of short droops), balance the inverter's rise and fall delays (DNL), and extend the TDC's range (hot corners). [9. Design journey](09-design-journey.md#if-we-continued)
</details>

---

[← 9. Design journey](09-design-journey.md) · [Documentation index](README.md) · Next: [Glossary →](glossary.md)
