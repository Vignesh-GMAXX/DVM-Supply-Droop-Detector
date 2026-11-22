"""Parser for ADE XL 'corner table' CSV exports (one column per corner, one block per sweep point).

    meta, data = read_corner_table("corners_droop_0_5pct.csv")
    meta["C7"]  -> {"S0": "1", "S1": "0", "T0": "0", "T1": "0", "gpdk045.scs": "ff", "temperature": "125"}
    data[0.05]["code_droop"]["C7"] -> 14.0          (None where ADE reported 'eval err')
"""
import csv
import re


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _vdroop(text):
    m = re.search(r"vdroop=([0-9.eE+-]+)(m?)", text)
    v = float(m.group(1))
    return round(v * (1e-3 if m.group(2) == "m" else 1), 6)


def read_corner_table(path):
    rows = list(csv.reader(open(path, newline="")))
    head = rows[0]
    first = next(i for i, x in enumerate(head) if x and i > 2)
    corners = [c for c in head[first:] if c]
    meta = {c: {} for c in corners}
    i = 1
    while rows[i] and rows[i][2]:
        for j, c in enumerate(corners):
            meta[c][rows[i][2]] = rows[i][first + j]
        i += 1
    data, point = {}, None
    for r in rows[i:]:
        if not r or not any(r):
            continue
        if r[0].startswith("Parameters:"):
            point = _vdroop(r[0])
            data.setdefault(point, {})
            continue
        if point is None or len(r) < first + len(corners) or r[0] == "Point":
            continue
        out = r[2]
        vals = {c: _num(r[first + j]) for j, c in enumerate(corners)}
        if all(v is None for v in vals.values()) and any(r[first + j] == "canceled" for j in range(len(corners))):
            continue
        data[point][out] = vals
    return meta, data


def corner_label(m):
    return f"{m['gpdk045.scs']} {m['temperature']}"
