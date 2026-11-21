import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, json
plt.rcParams.update({"font.family":"serif","font.size":8,"axes.grid":True,"grid.alpha":0.3,"savefig.dpi":300,
    "savefig.bbox":"tight","savefig.pad_inches":0.02,"xtick.labelsize":7,"ytick.labelsize":7,"legend.fontsize":6})
import csv
_r = [x for x in list(csv.reader(open('state_static.csv')))[1:] if x and x[0]]   # ADE L state_static export
vd = np.array([float(x[0]) for x in _r])
V = 1 - vd                                         # static supply on the droop bottom
c = np.array([int(round(float(x[1]))) for x in _r])
c15 = c.copy()
f = {j: np.array([float(x[3+2*j]) > 0.5 for x in _r]) for j in range(3)}
# transitions (decreasing V): T_k = midpoint where the code first becomes <= k
codes = list(range(19, 8, -1)); T = {}
for k in codes:
    i = np.where(c <= k)[0][0]; T[k] = (V[i-1] + V[i])/2
lsb = (T[19] - T[9]) / 10                          # endpoint LSB over codes 10..19
W = {k: T[k] - T[k-1] for k in range(19, 9, -1)}   # width of code k
dnl = {k: W[k]/lsb - 1 for k in W}
inl = {k: (T[19] - T[k])/lsb - (19 - k) for k in codes}
fsw = {j: V[np.where(f[j])[0][0]] for j in range(3)}
res = dict(lsb_mV=lsb*1e3, T={k: T[k] for k in codes}, W_mV={k: W[k]*1e3 for k in W}, dnl=dnl, inl=inl,
           dnl_min=min(dnl.values()), dnl_max=max(dnl.values()), inl_min=min(inl.values()), inl_max=max(inl.values()),
           flag_switch_V=fsw, mismatch_15_vs_17p5=[(round(V[i],4), int(c15[i]), int(c[i])) for i in range(len(V)) if c15[i]!=c[i]])
json.dump(res, open('dnl_res.json','w'), indent=1, default=float)
fig, (a0, a1) = plt.subplots(2, 1, figsize=(3.4, 2.55), sharex=False, gridspec_kw={"height_ratios":[2.1,1], "hspace":0.95})
a0.step(V, c, where='mid', color='C0', lw=1.0)
for j,(th,col) in enumerate([(16.5,'C1'),(12.5,'C2'),(9.5,'C3')]):
    a0.axvline(fsw[j], color=col, ls='--', lw=0.8)
    a0.text(fsw[j]-0.001, 20.3, f'flag{j}', color=col, fontsize=5.8, ha='right', va='bottom', rotation=0)
a0.set_xlim(0.848, 1.002); a0.set_ylim(7.6, 21.8); a0.set_yticks([8,10,12,14,16,18,20])
a0.set_xlabel(r'Static supply $V_{DD}$ (V)', labelpad=1); a0.set_ylabel('TDC code')
ks = sorted(dnl); a1.bar(ks, [dnl[k] for k in ks], color=['C0' if k%2==0 else 'C3' for k in ks], width=0.6)
a1.plot(sorted(inl), [inl[k] for k in sorted(inl)], 'k.-', lw=0.8, ms=3, label='INL')
a1.axhline(0, color='k', lw=0.5); a1.set_xlabel('Code', labelpad=1); a1.set_ylabel('LSB'); a1.set_xticks(range(10, 20))
a1.set_ylim(-1.05, 1.05); a1.legend(handles=[plt.Rectangle((0,0),1,1,color='C0',label='DNL even'), plt.Rectangle((0,0),1,1,color='C3',label='DNL odd'), a1.lines[0]], ncol=3, loc='upper center', bbox_to_anchor=(0.5, 1.36), frameon=False, handlelength=1.0, columnspacing=0.8)
fig.savefig('fig_static.pdf'); fig.savefig('fig_static.png', dpi=200); plt.close(fig)
print(json.dumps(res, indent=1, default=float))
