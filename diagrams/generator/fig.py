"""Paper-style block diagrams (black line art, gate symbols) for the P1G11 DVM.
Every primitive is placed at exact coordinates; the same list is written to .drawio and to a PNG preview."""
import re
from xml.sax.saxutils import quoteattr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Ellipse, FancyArrowPatch

FONT = "Helvetica"
BLUE = "#1f4e9c"


TAGS = r"(?!/?(?:sub|b|i|br)\b)"


def esc(s):
    """escape '<' that is not one of our HTML tags (so O<15> survives draw.io's HTML labels)"""
    return re.sub("<" + TAGS, "&lt;", s)


def clean(s):
    return re.sub(r"</?(?:sub|b|i|br)\s*/?>", "", s)


class Fig:
    def __init__(self, name, W, H):
        self.name, self.W, self.H, self.P = name, W, H, []

    # ------------------------------------------------ primitives
    def rect(self, x, y, w, h, label="", bold=False, dashed=False, fill="#ffffff", fs=11, stroke="#000000",
             valign="middle", lw=1):
        self.P.append(dict(t="rect", x=x, y=y, w=w, h=h, label=label, bold=bold, dashed=dashed, fill=fill, fs=fs,
                           stroke=stroke, valign=valign, lw=lw))

    def tri(self, x, y, w, h, d="east"):
        self.P.append(dict(t="tri", x=x, y=y, w=w, h=h, d=d))

    def ell(self, x, y, w, h, filled=False):
        self.P.append(dict(t="ell", x=x, y=y, w=w, h=h, filled=filled))

    def trap(self, x, y, w, h, s=10):
        self.P.append(dict(t="trap", x=x, y=y, w=w, h=h, s=s))

    def wire(self, pts, arrow=False, lw=1, dashed=False, color="#000000"):
        self.P.append(dict(t="wire", pts=pts, arrow=arrow, lw=lw, dashed=dashed, color=color))

    def text(self, x, y, s, align="left", italic=False, fs=10, bold=False, color="#000000", w=None):
        self.P.append(dict(t="text", x=x, y=y, s=s, align=align, italic=italic, fs=fs, bold=bold, color=color, w=w))

    def dot(self, x, y):
        self.ell(x - 2.5, y - 2.5, 5, 5, True)

    # ------------------------------------------------ composite symbols
    def inv(self, x, yc, w=22, h=18, d="east"):
        """inverter; returns (in_pt, out_pt)"""
        if d == "east":
            self.tri(x, yc - h / 2, w, h)
            self.ell(x + w, yc - 3, 6, 6)
            return (x, yc), (x + w + 6, yc)
        # south: input at top, output at bottom; x is the centre line
        self.tri(x - h / 2, yc, h, w, "south")
        self.ell(x - 3, yc + w, 6, 6)
        return (x, yc), (x, yc + w + 6)

    def buf(self, x, yc, w=20, h=16):
        self.tri(x, yc - h / 2, w, h)
        return (x, yc), (x + w, yc)

    def dff(self, x, y, w=46, h=56, clk_y=None):
        self.rect(x, y, w, h)
        self.text(x + 4, y + 16, "D", fs=9)
        self.text(x + w - 4, y + 16, "Q", align="right", fs=9)
        cy = y + h - 14 if clk_y is None else clk_y
        self.wire([(x, cy - 5), (x + 7, cy), (x, cy + 5)])
        return dict(d=(x, y + 16), q=(x + w, y + 16), ck=(x, cy))

    def latch(self, x, y, w=46, h=50):
        self.rect(x, y, w, h)
        self.text(x + 4, y + 14, "D", fs=9)
        self.text(x + 4, y + h - 12, "EN", fs=8)
        self.text(x + w / 2, y + h - 8, "Q", align="center", fs=9)
        return dict(d=(x, y + 14), en=(x, y + h - 12), q=(x + w / 2, y + h))

    def mux2(self, x, y, w=28, h=46):
        self.trap(x, y, w, h, 8)
        self.text(x + 5, y + 12, "0", fs=8)
        self.text(x + 5, y + h - 12, "1", fs=8)
        return dict(i0=(x, y + 12), i1=(x, y + h - 12), o=(x + w, y + h / 2), s=(x + w / 2, y + h - 4))

    def mux4(self, x, y, w=40, h=104, labels=("00", "01", "10", "11")):
        self.trap(x, y, w, h, 12)
        ins = []
        for k, lb in enumerate(labels):
            yy = y + h * (2 * k + 1) / 8
            ins.append((x, yy))
            self.text(x + 4, yy, lb, fs=8)
        return dict(ins=ins, o=(x + w, y + h / 2), s=(x + w / 2, y + h - 6))

    # ------------------------------------------------ outputs
    def drawio(self):
        cells, n = [], [1]

        def nid():
            n[0] += 1
            return f"c{n[0]}"
        for p in self.P:
            t = p["t"]
            if t == "rect":
                st = (f"rounded=0;whiteSpace=wrap;html=1;fillColor={p['fill']};strokeColor={p['stroke']};"
                      f"fontFamily={FONT};fontSize={p['fs']};verticalAlign={p['valign']};strokeWidth={p['lw']};"
                      + ("dashed=1;" if p["dashed"] else "") + ("fontStyle=1;" if p["bold"] else ""))
                cells.append(self._v(nid(), esc(p["label"]).replace("\n", "<br>"), st, p))
            elif t == "tri":
                st = f"triangle;html=1;fillColor=#ffffff;strokeColor=#000000;direction={p['d']};"
                cells.append(self._v(nid(), "", st, p))
            elif t == "ell":
                st = f"ellipse;html=1;fillColor={'#000000' if p['filled'] else '#ffffff'};strokeColor=#000000;"
                cells.append(self._v(nid(), "", st, p))
            elif t == "trap":
                st = (f"shape=trapezoid;perimeter=trapezoidPerimeter;fixedSize=1;size={p['s']};direction=south;"
                      f"html=1;fillColor=#ffffff;strokeColor=#000000;")
                cells.append(self._v(nid(), "", st, p))
            elif t == "wire":
                pts = p["pts"]
                st = (f"endArrow={'block' if p['arrow'] else 'none'};endFill=1;endSize=6;html=1;rounded=0;"
                      f"strokeColor={p['color']};strokeWidth={p['lw']};" + ("dashed=1;" if p["dashed"] else ""))
                mid = "".join(f'<mxPoint x="{a}" y="{b}"/>' for a, b in pts[1:-1])
                cells.append(
                    f'<mxCell id="{nid()}" style={quoteattr(st)} edge="1" parent="1"><mxGeometry relative="1" '
                    f'as="geometry"><mxPoint x="{pts[0][0]}" y="{pts[0][1]}" as="sourcePoint"/>'
                    f'<mxPoint x="{pts[-1][0]}" y="{pts[-1][1]}" as="targetPoint"/>'
                    + (f'<Array as="points">{mid}</Array>' if mid else "") + "</mxGeometry></mxCell>")
            elif t == "text":
                w = p["w"] or max(20, 6.2 * len(re.sub(r"<[^>]+>", "", p["s"])) * p["fs"] / 10 + 6)
                x = {"left": p["x"], "center": p["x"] - w / 2, "right": p["x"] - w}[p["align"]]
                fsty = (2 if p["italic"] else 0) + (1 if p["bold"] else 0)
                st = (f"text;html=1;align={p['align']};verticalAlign=middle;fontFamily={FONT};fontSize={p['fs']};"
                      f"fontStyle={fsty};fontColor={p['color']};spacing=0;whiteSpace=wrap;")
                lines = p["s"].count("\n") + 1
                h = 14 * lines
                cells.append(f'<mxCell id="{nid()}" value={quoteattr(esc(p["s"]).replace(chr(10), "<br>"))} '
                             f'style={quoteattr(st)} vertex="1" parent="1"><mxGeometry x="{x}" y="{p["y"] - h / 2}" '
                             f'width="{w}" height="{h}" as="geometry"/></mxCell>')
        return (f'<diagram id="{self.name}" name="{self.name}"><mxGraphModel dx="1000" dy="700" grid="0" gridSize="10" '
                f'guides="1" tooltips="1" connect="0" arrows="1" fold="1" page="1" pageScale="1" '
                f'pageWidth="{self.W}" pageHeight="{self.H}" math="0" shadow="0" background="#ffffff"><root>'
                f'<mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + "</root></mxGraphModel></diagram>")

    @staticmethod
    def _v(cid, label, st, p):
        return (f'<mxCell id="{cid}" value={quoteattr(label)} style={quoteattr(st)} vertex="1" parent="1">'
                f'<mxGeometry x="{p["x"]}" y="{p["y"]}" width="{p["w"]}" height="{p["h"]}" as="geometry"/></mxCell>')

    def bounds(self):
        xs, ys = [], []
        for p in self.P:
            if p["t"] == "wire":
                for a, b in p["pts"]:
                    xs.append(a); ys.append(b)
            elif p["t"] == "text":
                w = 6.8 * len(clean(p["s"])) * p["fs"] / 10 * self._fm
                x0 = {"left": p["x"], "center": p["x"] - w / 2, "right": p["x"] - w}[p["align"]]
                xs += [x0, x0 + w]; ys += [p["y"] - 8 * self._fm, p["y"] + 8 * self._fm]
            else:
                xs += [p["x"], p["x"] + p["w"]]; ys += [p["y"], p["y"] + p["h"]]
        m = 10
        return min(xs) - 2 * m, max(xs) + m, min(ys) - m, max(ys) + m

    _fm = 1.0

    def pdf(self, fn, width_in, font_pt=6.8):
        """print version: cropped to content, text at about font_pt for fs=10"""
        self._fm = 1.0
        x0, x1, y0, y1 = self.bounds()
        ppu = width_in * 72 / (x1 - x0)
        self._fm = font_pt / (10 * ppu)
        x0, x1, y0, y1 = self.bounds()
        ppu = width_in * 72 / (x1 - x0)
        self._fs_scale = font_pt / 10 / 0.62
        self._lw = 0.8
        self.png(fn, figsize=(width_in, width_in * (y1 - y0) / (x1 - x0)), lims=(x0, x1, y0, y1), tight=False,
                 fsk=font_pt / 10)
        self._fm = 1.0

    def png(self, fn, scale=1.0, figsize=None, lims=None, tight=True, fsk=None):
        fig, ax = plt.subplots(figsize=figsize or (self.W / 90 * scale, self.H / 90 * scale))
        if lims:
            ax.set_position([0, 0, 1, 1]); ax.set_xlim(lims[0], lims[1]); ax.set_ylim(lims[3], lims[2])
        else:
            ax.set_xlim(0, self.W); ax.set_ylim(self.H, 0)
        ax.set_aspect("equal"); ax.axis("off")
        k = fsk if fsk else 0.62
        for p in self.P:
            t = p["t"]
            if t == "rect":
                ax.add_patch(Rectangle((p["x"], p["y"]), p["w"], p["h"], fc=p["fill"], ec=p["stroke"], lw=p["lw"],
                                       ls="--" if p["dashed"] else "-"))
                if p["label"]:
                    yy = p["y"] + p["h"] / 2 if p["valign"] == "middle" else p["y"] + 4
                    ax.text(p["x"] + p["w"] / 2, yy, clean(p["label"]), ha="center",
                            va="center" if p["valign"] == "middle" else "top", fontsize=p["fs"] * k,
                            fontweight="bold" if p["bold"] else "normal")
            elif t == "tri":
                x, y, w, h = p["x"], p["y"], p["w"], p["h"]
                pts = {"east": [(x, y), (x + w, y + h / 2), (x, y + h)],
                       "west": [(x + w, y), (x, y + h / 2), (x + w, y + h)],
                       "south": [(x, y), (x + w, y), (x + w / 2, y + h)]}[p["d"]]
                ax.add_patch(Polygon(pts, fc="white", ec="k", lw=1))
            elif t == "ell":
                ax.add_patch(Ellipse((p["x"] + p["w"] / 2, p["y"] + p["h"] / 2), p["w"], p["h"],
                                     fc="k" if p["filled"] else "white", ec="k", lw=1))
            elif t == "trap":
                x, y, w, h, s = p["x"], p["y"], p["w"], p["h"], p["s"]
                ax.add_patch(Polygon([(x, y), (x + w, y + s), (x + w, y + h - s), (x, y + h)], fc="white", ec="k", lw=1))
            elif t == "wire":
                xs, ys = zip(*p["pts"])
                ax.plot(xs, ys, color=p["color"], lw=p["lw"], ls="--" if p["dashed"] else "-", solid_capstyle="butt")
                if p["arrow"]:
                    ax.annotate("", xy=p["pts"][-1], xytext=p["pts"][-2],
                                arrowprops=dict(arrowstyle="-|>", color=p["color"], lw=p["lw"], shrinkA=0, shrinkB=0))
            elif t == "text" and "⌊" in p["s"]:
                ax.text(p["x"], p["y"], r"$\mathrm{code} = \lfloor (T_w - t_{TRC})\,/\,t_s \rfloor$", ha=p["align"],
                        va="center", fontsize=p["fs"] * k)
            elif t == "text":
                ax.text(p["x"], p["y"], re.sub(r"(\w)<sub>(.*?)</sub>", lambda m: "$" + m.group(1) + "_{" + m.group(2) + "}$", p["s"]).replace("<b>", "").replace("</b>", ""), ha=p["align"], va="center", fontsize=p["fs"] * k,
                        style="italic" if p["italic"] else "normal", fontweight="bold" if p["bold"] else "normal",
                        color=p["color"])
        if tight:
            fig.savefig(fn, dpi=170, bbox_inches="tight", facecolor="white")
        else:
            fig.savefig(fn, facecolor="white")
        plt.close(fig)


def save(figs, fn):
    open(fn, "w").write('<mxfile host="app.diagrams.net">' + "".join(f.drawio() for f in figs) + "</mxfile>")
