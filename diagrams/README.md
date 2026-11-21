# Diagrams

Block diagrams of the design as editable [draw.io](https://app.diagrams.net) files (open in diagrams.net or the draw.io desktop app).

| File | Diagram | Preview |
|---|---|---|
| `P1G11_DVM_hierarchy.drawio` (+ `.pdf`, `.png`) | Design hierarchy: leaf cells → blocks → DVM_DUT (report Fig. 1) | [hierarchy](previews/hierarchy.png) |
| `P1G11_DVM_top.drawio` | DVM top level: divider, clock buffer, TRC, TDC, decision stages, TAP_CAL | [DVM](previews/DVM.png) |
| `P1G11_DVM_TRC.drawio` | Tunable replica circuit with trim `T<1:0>` | [TRC](previews/TRC.png) |
| `P1G11_DVM_TDC.drawio` | 32-stage latch-based TDC | [TDC](previews/TDC.png) |
| `P1G11_TAP_CAL.drawio` | TAP_CAL: three 4:1 tap selectors and retimed decision stages | [TAP_CAL](previews/TAPCAL.png) |
| `P1G11_DVM_figures.drawio` | All four block diagrams, one per page | – |

## Regenerating

The diagrams are generated from code, so every gate and wire sits on exact coordinates:

```bash
cd diagrams/generator
python3 build.py        # DVM top, TRC, TDC, TAP_CAL (.drawio + PNG previews)
python3 big.py          # hierarchy figure (.drawio, .pdf, PNG preview)
python3 export_pdf.py   # optional: PDFs of the block diagrams
```

`fig.py` holds the drawing primitives (gates, latches, muxes, wires, labels) and writes both draw.io XML and matplotlib output.
