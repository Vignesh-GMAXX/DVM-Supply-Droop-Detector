from fig import Fig, save, BLUE

# =====================================================================  TRC
f = Fig("TRC", 930, 330)
y0 = 90
f.text(20, y0, "clkdiv_b", italic=True)
x = 80
f.wire([(62, y0), (x, y0)])
taps = []
for g in range(4):
    gx0 = x
    for j in range(4):
        i, o = f.buf(x, y0)
        nx = x + 34
        f.wire([o, (nx, y0)])
        x = nx
    taps.append(x - 6)
    # bracket under each group
    f.wire([(gx0, y0 + 16), (gx0, y0 + 20), (x - 14, y0 + 20), (x - 14, y0 + 16)], color="#777777")
    f.text((gx0 + x - 14) / 2, y0 + 30, "4 buffers", align="center", fs=8, color="#555555")
    x += 18
    if g < 3:
        f.wire([(x - 18, y0), (x, y0)])
mx = f.mux4(740, 150, 44, 116, labels=("11", "10", "01", "00"))
f.text(762, 140, "MX4X1", align="center", fs=9, bold=True)
# tap k (k=0 shortest) -> input "00" at bottom ... tap 3 (longest) -> "11" at top: no crossings
for k, tx in enumerate(taps):
    yi = mx["ins"][3 - k][1]
    f.dot(tx, y0) if k < 3 else None
    f.wire([(tx, y0), (tx, yi), (740, yi)])
    f.text(tx - 4, yi - 8, f"T = {k:02b}", fs=8, color="#555555", align="right")
f.wire([mx["s"], (mx["s"][0], 296)])
f.text(mx["s"][0], 306, "T<1:0>", align="center", italic=True)
f.wire([mx["o"], (850, mx["o"][1])], arrow=True)
f.text(856, mx["o"][1], "TRC_Out", italic=True)
f.png("prev_TRC.png")
TRC = f

# =====================================================================  TDC
f = Fig("TDC", 900, 520)
yc = 70
f.text(20, yc, "TRC_Out", italic=True)
x = 78
f.wire([(70, yc), (x, yc)])
stages = [31, 30, 29, 28, None, 1, 0]
pitch = 110
EN_Y = 270
xs_en = []
for k in stages:
    if k is None:
        f.text(x + 28, yc, "· · ·", align="center", fs=14)
        f.wire([(x, yc), (x + 8, yc)])
        f.wire([(x + 48, yc), (x + 60, yc)])
        f.text(x + 28, 160, "· · ·", align="center", fs=14)
        x += 60
        continue
    i, o = f.inv(x, yc)
    nx = o[0] + 18
    f.wire([o, (nx + 30, yc)])
    f.dot(nx, yc)
    L = f.latch(nx + 14, 112, w=58)
    f.wire([(nx, yc), (nx, L["d"][1]), L["d"]])
    ex = nx + 6
    f.wire([(ex, EN_Y), (ex, L["en"][1]), L["en"]])
    f.dot(ex, EN_Y)
    xs_en.append(ex)
    qx, qy = L["q"]
    if k % 2 == 0:
        ii, oo = f.inv(qx, qy + 8, 16, 14, "south")
        f.wire([(qx, qy), ii])
        f.wire([oo, (qx, 240)])
    else:
        f.wire([(qx, qy), (qx, 240)])
    f.text(qx, 250, f"O<{k}>", align="center", italic=True, fs=9)
    x = nx + 30
f.wire([(30, EN_Y), (xs_en[-1], EN_Y)], arrow=False)
f.text(26, EN_Y, "clkdiv_b", align="right", italic=True) if False else f.text(20, EN_Y - 12, "clkdiv_b (EN)", italic=True, fs=9)
# ---- timing diagram
T0, Y1, Y2, Y3 = 120, 350, 400, 450
f.text(20, Y1 - 8, "clkdiv_b", italic=True, fs=9)
f.wire([(T0, Y1), (180, Y1), (180, Y1 - 22), (480, Y1 - 22), (480, Y1), (720, Y1)])
f.text(330, Y1 - 32, "sample window  T<sub>w</sub> = t<sub>clk</sub>", align="center", fs=9, w=200)
f.text(600, Y1 - 10, "hold: latches keep the code", align="center", fs=9, w=180)
f.text(20, Y2 - 8, "TRC_Out", italic=True, fs=9)
f.wire([(T0, Y2), (250, Y2), (250, Y2 - 22), (720, Y2 - 22)])
f.wire([(180, Y2 + 10), (250, Y2 + 10)], arrow=True); f.wire([(250, Y2 + 10), (180, Y2 + 10)], arrow=True)
f.text(215, Y2 + 20, "t<sub>TRC</sub>", align="center", fs=9)
f.text(20, Y3 - 8, "edge in TDC", italic=True, fs=9)
for j, xx in enumerate(range(260, 480, 24)):
    f.wire([(xx, Y3), (xx, Y3 - 14)], color="#555555")
f.wire([(250, Y3), (480, Y3)], color="#555555")
f.text(370, Y3 + 14, "one tick per stage (t<sub>s</sub>)", align="center", fs=8, color="#555555", w=160)
f.wire([(480, Y1 + 4), (480, Y3 + 4)], dashed=True, color="#777777")
f.text(492, Y3 - 6, "code = ⌊(T<sub>w</sub> − t<sub>TRC</sub>) / t<sub>s</sub>⌋", fs=10, w=220)
f.png("prev_TDC.png")
TDC = f


# =====================================================================  decision stage helper
def decision(f, xm, yc, tap_label, out_label, clk_label, clk_color="#000000", fb_up=True):
    m = f.mux2(xm, yc - 23)
    d = f.dff(xm + 66, yc - 16 - 12)
    # mux out -> D
    f.wire([m["o"], (m["o"][0] + 12, m["o"][1]), (m["o"][0] + 12, d["d"][1]), d["d"]])
    # tap -> input 1
    # Q -> out, feedback -> input 0
    qx, qy = d["q"]
    fbx = qx + 14
    f.wire([d["q"], (qx + 70, qy)], arrow=True)
    f.text(qx + 76, qy, out_label, italic=True)
    f.dot(fbx, qy)
    top = yc - 40
    f.wire([(fbx, qy), (fbx, top), (xm - 12, top), (xm - 12, m["i0"][1]), m["i0"]])
    # select and clock stubs
    f.wire([m["s"], (m["s"][0], yc + 34)])
    f.text(m["s"][0], yc + 42, "hold", align="center", italic=True, fs=8)
    cx = d["ck"][0] - 10
    f.wire([(cx, yc + 34), (cx, d["ck"][1]), d["ck"]], color=clk_color, lw=1.5 if clk_color != "#000000" else 1)
    f.text(cx, yc + 42, clk_label, align="center", italic=True, fs=8, color=clk_color)
    return m


# =====================================================================  TAP_CAL
f = Fig("TAP_CAL", 680, 560)
BX = 110
f.wire([(BX, 46), (BX, 500)], lw=3)
f.text(BX, 34, "O<26:15>  (from DVM TDC)", align="center", italic=True, fs=10, w=200)
taps = [("O<15>", "O<17>", "O<21>"), ("O<19>", "O<20>", "O<23>"), ("O<22>", "O<21>", "O<24>")]
lvl = ["5%", "10%", "15%"]
for r in range(3):
    yc = 120 + r * 160
    m4 = f.mux4(250, yc - 52, 40, 104)
    for k in range(3):
        yy = m4["ins"][k][1]
        f.dot(BX, yy)
        f.wire([(BX, yy), m4["ins"][k]])
        f.text(BX + 10, yy - 7, taps[r][k], italic=True, fs=8)
    yy = m4["ins"][3][1]
    f.wire([(222, yy), m4["ins"][3]])
    f.text(218, yy, "V<sub>SS</sub>", align="right", fs=8)
    f.wire([m4["s"], (m4["s"][0], yc + 62)])
    f.text(m4["s"][0], yc + 70, "S<1:0>", align="center", italic=True, fs=8)
    f.wire([m4["o"], (360, yc + 12 - 12 + 11)]) if False else None
    m = decision(f, 380, yc, "", f"CAL_O<{r}>  ({lvl[r]})", "CLK", BLUE)
    f.wire([m4["o"], (360, m4["o"][1]), (360, m["i1"][1]), m["i1"]])
    f.text(322, m4["o"][1] - 8, f"sel{r}", italic=True, fs=8)
f.png("prev_TAPCAL.png")
TAP = f

# =====================================================================  DVM top level
f = Fig("DVM", 1060, 470)
YM, YC = 170, 300           # TRC/TDC row, clock row
# divide-by-2: DFFSX1 with an inverter from Q back to D
f.text(14, YC + 14, "CLK", italic=True)
f.wire([(40, YC + 14), (86, YC + 14)])
dv = f.dff(86, YC - 28, 46, 56)
f.text(109, YC + 38, "÷2", align="center", fs=8)
f.dot(142, YC - 12)
f.wire([dv["q"], (150, YC - 12), (150, YC), (176, YC)])
f.wire([(142, YC - 12), (142, YC - 50), (122, YC - 50)])
f.tri(102, YC - 57, 20, 14, "west"); f.ell(96, YC - 53, 6, 6)
f.wire([(96, YC - 50), (72, YC - 50), (72, dv["d"][1]), dv["d"]])
f.text(163, YC - 22, "clkdiv", italic=True, fs=8, align="center")
# CLKn for the decision DFFs
f.dot(56, YC + 14)
f.wire([(56, YC + 14), (56, YC + 72), (80, YC + 72)])
ic, oc = f.inv(80, YC + 72, 22, 18)
f.wire([oc, (140, YC + 72)], arrow=True)
f.text(146, YC + 72, "CLKn", italic=True, fs=9)
i, o = f.inv(176, YC, 24, 20)
f.text(188, YC + 20, "4×", align="center", fs=8)
f.wire([o, (226, YC)])
i, o = f.inv(226, YC, 28, 24)
f.text(240, YC + 22, "16×", align="center", fs=8)
f.wire([o, (300, YC)])
f.dot(300, YC)
f.text(306, YC + 12, "clkdiv_b", italic=True, fs=9)
# TRC
f.wire([(300, YC), (300, YM), (340, YM)])
f.rect(340, YM - 34, 96, 68, "TRC", bold=True, fs=12)
f.wire([(388, 100), (388, YM - 34)], arrow=True)
f.text(388, 90, "T<1:0>", align="center", italic=True)
f.wire([(436, YM), (500, YM)])
f.text(468, YM - 10, "TRC_Out", italic=True, fs=8, align="center")
# TDC
f.rect(500, YM - 60, 190, 120, "", fs=11)
f.text(595, YM - 44, "TDC", align="center", bold=True, fs=12)
f.wire([(500, YM), (510, YM), (510, YM - 8), (516, YM - 8)])
for j in range(4):
    i, o = f.inv(516 + j * 36, YM - 8, 18, 14)
    f.wire([o, (o[0] + 12, YM - 8)])
    f.dot(o[0] + 6, YM - 8)
    f.wire([(o[0] + 6, YM - 8), (o[0] + 6, YM + 14)])
    f.rect(o[0] - 7, YM + 14, 26, 20, "L", fs=8)
f.text(670, YM - 8, "…", align="center", fs=12)
f.wire([(300, YC), (595, YC), (595, YM + 60)], arrow=True)
f.text(600, YC - 14, "EN (all latches)", fs=8, italic=True)
# bus
f.wire([(690, YM), (740, YM)], lw=3)
f.wire([(740, 70), (740, 410)], lw=3)
f.text(732, 420, "O<31:0>", italic=True, fs=9, align="right")
lab = [("O<15>", "DVM_O<0>  (5%)"), ("O<19>", "DVM_O<1>  (10%)"), ("O<22>", "DVM_O<2>  (15%)")]
for r in range(3):
    yc = 100 + r * 105
    m = decision(f, 800, yc, "", lab[r][1], "CLKn")
    f.dot(740, m["i1"][1])
    f.wire([(740, m["i1"][1]), m["i1"]])
    f.text(746, m["i1"][1] - 8, lab[r][0], italic=True, fs=8)
# TAP_CAL block
f.dot(740, 400)
f.wire([(740, 400), (800, 400)], lw=3, arrow=False)
f.rect(800, 370, 130, 60, "TAP_CAL\n(this work)", bold=True, fill="#dae8fc", stroke=BLUE, lw=1.5, fs=11)
f.text(772, 390, "O<26:15>", italic=True, fs=8, align="center")
f.wire([(930, 400), (990, 400)], arrow=True, color=BLUE)
f.text(996, 400, "CAL_O<2:0>", italic=True, fs=9, color=BLUE)
f.wire([(865, 450), (865, 430)], arrow=True, color=BLUE)
f.text(865, 460, "S<1:0>   CLK", align="center", italic=True, fs=8, color=BLUE)
f.png("prev_DVM.png")
DVM = f

save([DVM, TRC, TDC, TAP], "P1G11_DVM_figures.drawio")
for F, n in [(DVM, "DVM_top"), (TRC, "DVM_TRC"), (TDC, "DVM_TDC"), (TAP, "TAP_CAL")]:
    save([F], f"P1G11_{n}.drawio")
print("ok")
