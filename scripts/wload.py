import csv, re, numpy as np
PAT1 = re.compile(r'(.+?) \(modelFiles=gpdk045\.scs:(\w+),vdroop=([\d.e+-]+),temperature=([\d.e+-]+)\) Y')
PAT2 = re.compile(r'/?(\S+) modelFiles gpdk045\.scs:(\w+) vdroop ([\d.e+-]+) temperature ([\d.e+-]+)')
def load(path, want=None):
    with open(path, newline='') as f:
        r = csv.reader(f); head = next(r)
        keys = {}
        for i in range(1, len(head), 2):
            h = head[i].replace('\\', '')
            m = PAT1.match(h) or PAT2.match(h)
            sig = m.group(1).lstrip('/')
            k = (sig, m.group(2), round(float(m.group(3)), 3), round(float(m.group(4))))
            if want is None or want(k): keys[i] = k
        data = {i: ([], []) for i in keys}
        for row in r:
            for i in keys:
                if i < len(row) and row[i].strip() and row[i-1].strip():
                    data[i][0].append(float(row[i-1])); data[i][1].append(float(row[i]))
    return {keys[i]: (np.array(t), np.array(y)) for i, (t, y) in data.items()}
