"""One large hierarchical figure: leaf cells -> building blocks -> DVM + TAP_CAL.
Every component is drawn in its own local frame, measured, then centred in its tile."""
import copy
import build                       # builds DVM / TAP primitives
from build import decision, DVM, TAP
from fig import Fig, save, BLUE

W = 1900
GREY = "#666666"
BAND = "#f4f7fb"
f = Fig("DVM_hierarchy", W, 100)


def bounds(src):
    src._fm = 1.0
    x0, x1, y0, y1 = src.bounds()
    return x0 + 10, x1 - 10, y0 + 10, y1 - 10      # remove the bounds() margin


def place(src, dx, dy):
    for p in src.P:
        q = copy.deepcopy(p)
        if q["t"] == "wire":
            q["pts"] = [(a + dx, b + dy) for a, b in q["pts"]]
        else:
            q["x"] += dx; q["y"] += dy
        f.P.append(q)


def centre(src, x, y, w, h):
    bx0, bx1, by0, by1 = bounds(src)
    dx, dy = x + (w - (bx1 - bx0)) / 2 - bx0, y + (h - (by1 - by0)) / 2 - by0
    place(src, dx, dy)
    return dx, dy


def band(y0, y1, title):
    f.text(30, y0 + 18, title, bold=True, fs=13, w=700)


def tile(x, y, w, h, name, sub, comp, name_h=40):
    f.text(x + w / 2, y + h - 26, name, align="center", bold=True, fs=11, w=w - 10)
    f.text(x + w / 2, y + h - 11, sub, align="center", fs=8, color=GREY, w=w - 10)
    centre(comp, x + 8, y + 8, w - 16, h - name_h - 12)


def arrow_between(y0, y1):
    f.wire([(W / 2, y0), (W / 2, y1)], arrow=True, lw=3, color="#7f8c99")
    f.text(W / 2 + 10, (y0 + y1) / 2, "used in", fs=9, color=GREY, italic=True)


# ----------------------------------------------------------------- leaf-cell drawings
def c_inv():
    c = Fig("c", 1, 1); i, o = c.inv(0, 0, 36, 30)
    c.wire([(-30, 0), i]); c.wire([o, (o[0] + 30, 0)]); return c


def c_buf():
    c = Fig("c", 1, 1); i, o = c.inv(0, 0, 28, 24); c.wire([(-22, 0), i]); c.wire([o, (o[0] + 16, 0)])
    i2, o2 = c.inv(o[0] + 16, 0, 28, 24); c.wire([o2, (o2[0] + 22, 0)]); return c


def c_tg():
    c = Fig("c", 1, 1)
    c.tri(-22, -16, 44, 32, "east"); c.tri(-22, -16, 44, 32, "west")
    c.wire([(-52, 0), (-22, 0)]); c.wire([(22, 0), (52, 0)])
    c.wire([(0, -8), (0, -34)]); c.text(5, -32, "S", italic=True, fs=9)
    c.ell(-3, 8, 6, 6); c.wire([(0, 14), (0, 34)]); c.text(5, 32, "SB", italic=True, fs=9)
    return c


def c_latch():
    c = Fig("c", 1, 1); L = c.latch(0, 0, 52, 60)
    c.wire([(L["d"][0] - 26, L["d"][1]), L["d"]]); c.wire([(L["en"][0] - 26, L["en"][1]), L["en"]])
    c.wire([L["q"], (L["q"][0], L["q"][1] + 12)]); return c


def c_mux2():
    c = Fig("c", 1, 1); m = c.mux2(0, 0, 32, 52)
    c.wire([(m["i0"][0] - 26, m["i0"][1]), m["i0"]]); c.wire([(m["i1"][0] - 26, m["i1"][1]), m["i1"]])
    c.wire([m["o"], (m["o"][0] + 26, m["o"][1])]); c.wire([m["s"], (m["s"][0], m["s"][1] + 14)]); return c


def c_mux4():
    c = Fig("c", 1, 1); m = c.mux4(0, 0, 40, 88)
    for p in m["ins"]:
        c.wire([(p[0] - 22, p[1]), p])
    c.wire([m["o"], (m["o"][0] + 24, m["o"][1])]); c.wire([m["s"], (m["s"][0], m["s"][1] + 12)]); return c


def c_dff():
    c = Fig("c", 1, 1); d = c.dff(0, 0, 50, 58)
    c.wire([(d["d"][0] - 24, d["d"][1]), d["d"]]); c.wire([d["q"], (d["q"][0] + 24, d["q"][1])])
    c.wire([(d["ck"][0] - 24, d["ck"][1]), d["ck"]])
    c.wire([(25, 0), (25, -12)]); c.text(29, -14, "SN", fs=8); return c


# ----------------------------------------------------------------- building blocks
def b_clock():
    c = Fig("c", 1, 1); yc = 0
    c.text(0, yc, "CLK", italic=True, fs=10)
    c.wire([(30, yc), (50, yc)])
    c.rect(50, yc - 26, 56, 52, "TFF\n÷2", fs=10)
    c.wire([(106, yc), (146, yc)]); c.text(126, yc - 10, "clkdiv", italic=True, fs=8, align="center")
    i, o = c.inv(146, yc, 24, 20); c.text(158, yc + 22, "4×", align="center", fs=8)
    c.wire([o, (196, yc)])
    i, o = c.inv(196, yc, 30, 26); c.text(211, yc + 24, "16×", align="center", fs=8)
    c.wire([o, (300, yc)], arrow=True)
    c.text(245, yc - 12, "clkdiv_b", italic=True, fs=9)
    return c


def b_trc():
    c = Fig("c", 1, 1)
    x0, pitch = 0, 46
    rows = []
    for k in range(4):
        yk = k * pitch
        x = x0
        c.wire([(x, yk), (x + 10, yk)])
        x += 10
        for j in range(4):
            i, o = c.buf(x, yk, 22, 18)
            c.wire([o, (x + 38, yk)])
            x += 38
        rows.append((x, yk))
    mxx = rows[0][0] + 40
    m4 = c.mux4(mxx, -pitch / 2, 40, 4 * pitch)
    for k, (xe, yk) in enumerate(rows):
        c.dot(xe, yk)
        c.wire([(xe, yk), (mxx, yk)])
        if k < 3:
            c.wire([(xe, yk), (xe, yk + pitch / 2), (x0 - 14, yk + pitch / 2), (x0 - 14, yk + pitch), (x0, yk + pitch)])
    c.wire([(x0 - 40, 0), (x0, 0)])
    c.text(x0 - 40, -12, "clkdiv_b", italic=True, fs=8)
    c.wire([m4["s"], (m4["s"][0], m4["s"][1] + 16)])
    c.text(m4["s"][0], m4["s"][1] + 25, "T<1:0>", italic=True, fs=8, align="center")
    c.wire([m4["o"], (m4["o"][0] + 50, m4["o"][1])], arrow=True)
    c.text(m4["o"][0] + 6, m4["o"][1] - 12, "TRC_Out", italic=True, fs=8)
    return c


def b_tdc():
    c = Fig("c", 1, 1)
    yc = 0
    c.text(0, yc - 14, "TRC_Out", italic=True, fs=8)
    x = 18
    c.wire([(0, yc), (x, yc)])
    EN_Y = 205
    xs = []
    for k in [31, 30, 29, 28, None, 1, 0]:
        if k is None:
            c.text(x + 28, yc, "· · ·", align="center", fs=14)
            c.wire([(x, yc), (x + 8, yc)]); c.wire([(x + 48, yc), (x + 60, yc)])
            c.text(x + 28, yc + 90, "· · ·", align="center", fs=14)
            x += 60
            continue
        i, o = c.inv(x, yc)
        nx = o[0] + 18
        c.wire([o, (nx + 30, yc)])
        c.dot(nx, yc)
        L = c.latch(nx + 14, yc + 42, w=58)
        c.wire([(nx, yc), (nx, L["d"][1]), L["d"]])
        ex = nx + 6
        c.wire([(ex, EN_Y), (ex, L["en"][1]), L["en"]]); c.dot(ex, EN_Y); xs.append(ex)
        qx, qy = L["q"]
        if k % 2 == 0:
            ii, oo = c.inv(qx, qy + 8, 16, 14, "south"); c.wire([(qx, qy), ii]); c.wire([oo, (qx, qy + 58)])
        else:
            c.wire([(qx, qy), (qx, qy + 58)])
        c.text(qx, qy + 68, f"O<{k}>", align="center", italic=True, fs=9)
        x = nx + 30
    c.wire([(0, EN_Y), (xs[-1], EN_Y)])
    c.text(0, EN_Y + 13, "clkdiv_b (EN)", italic=True, fs=8)
    return c


def b_dec():
    c = Fig("c", 1, 1)
    m = decision(c, 60, 0, "", "flag", "CLKn / CLK")
    c.wire([(0, m["i1"][1]), m["i1"]]); c.text(0, m["i1"][1] - 10, "tap", italic=True, fs=8)
    return c


# ====================================================================== Level 1
L1_Y = 30
band(L1_Y, L1_Y + 222, "Level 1 · Full-custom leaf cells")
cells = [("INV", "W<sub>n</sub>/W<sub>p</sub> = 260/390 nm", c_inv()), ("BUF", "2 × INV", c_buf()),
         ("D-latch", "TG based, transparent high", c_latch()),
         ("Mux2_1_TG", "two TGs", c_mux2()), ("MX4X1", "4:1 mux", c_mux4()), ("DFFSX1", "D flip-flop with set", c_dff())]
n = len(cells); gap = 22; tw = (W - 70 - gap * (n - 1)) / n
for i, (nm, sub, comp) in enumerate(cells):
    tile(35 + i * (tw + gap), L1_Y + 38, tw, 170, nm, sub, comp)
arrow_between(L1_Y + 224, L1_Y + 250)

# ====================================================================== Level 2
L2_Y = L1_Y + 252
BH = 300
band(L2_Y, L2_Y + BH + 54, "Level 2 · Building blocks")
blocks = [("TRC", "16 BUF folded in 4 rows + MX4X1", b_trc(), 1.0),
          ("TDC", "32 × (INV + D-latch)", b_tdc(), 2.0), ("Decision stage", "Mux2_1_TG + DFFSX1", b_dec(), 1.0)]
tot = sum(b[3] for b in blocks); gap = 22; avail = W - 70 - gap * (len(blocks) - 1)
x = 35
for nm, sub, comp, wt in blocks:
    w = avail * wt / tot
    tile(x, L2_Y + 38, w, BH, nm, sub, comp)
    x += w + gap
arrow_between(L2_Y + BH + 56, L2_Y + BH + 82)

# ====================================================================== Level 3
L3_Y = L2_Y + BH + 84
L3_H = 640
band(L3_Y, L3_Y + L3_H, "Level 3 · DVM (baseline) and TAP_CAL (novelty)")
# DVM on the left, TAP_CAL (expanded) on the right in a dashed box
dvm_box = (35, L3_Y + 40, 1080, L3_H - 55)
tap_box = (1140, L3_Y + 40, W - 35 - 1140, L3_H - 55)
ddx, ddy = centre(DVM, *dvm_box)
f.rect(*tap_box, "", fill="none", stroke=BLUE, dashed=True, lw=1.5)
# novelty badge
bx, by = tap_box[0] + tap_box[2] - 330, tap_box[1] + tap_box[3] - 48
f.rect(bx, by, 320, 40, "", fill=BLUE, stroke=BLUE)
f.text(bx + 160, by + 13, "★ NOVELTY: TAP_CAL", align="center", bold=True, fs=11, color="#ffffff", w=300)
f.text(bx + 160, by + 29, "per-corner tap select + retimed DFFs", align="center", fs=8.5,
       color="#ffffff", w=300)
centre(TAP, tap_box[0] + 10, tap_box[1] + 34, tap_box[2] - 20, tap_box[3] - 96)
# DVM's TAP_CAL block -> expanded view
f.wire([(1072 + ddx, 400 + ddy), (tap_box[0], 400 + ddy)], arrow=True, dashed=True, color=BLUE, lw=1.5)

f.H = L3_Y + L3_H + 15
f.png("prev_hierarchy.png")
save([f], "P1G11_DVM_hierarchy.drawio")
f.pdf("P1G11_DVM_hierarchy.pdf", 16.0, 7.5)
print("ok", f.H)
