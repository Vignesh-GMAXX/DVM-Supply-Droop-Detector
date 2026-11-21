import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from wload import load
plt.rcParams.update({"font.family":"serif","font.size":8,"axes.grid":True,"grid.alpha":0.3,
    "savefig.dpi":300,"savefig.bbox":"tight","savefig.pad_inches":0.02,"lines.linewidth":1.0,
    "legend.fontsize":6.5,"xtick.labelsize":7,"ytick.labelsize":7})
tt27 = lambda k: k[1]=='tt' and k[3]==27
V = load('W1_droop.csv', tt27); A = load('W1_all.csv', tt27)
cols = {0.05:'C0', 0.1:'C1', 0.15:'C3'}
fig, ax = plt.subplots(4, 1, figsize=(7.0, 3.6), sharex=True, gridspec_kw={"height_ratios":[1.2,1,1,1]})
for d in (0.05, 0.1, 0.15):
    t,y = V[('VDD_DVM','tt',d,27)]; ax[0].plot(t*1e9, y, color=cols[d], label=f'{int(d*100)}% droop')
ax[0].set_ylabel(r'$V_{DD}$ (V)'); ax[0].legend(loc='lower left', ncol=1)
for r,d in zip((1,2,3),(0.05,0.1,0.15)):
    for j,off in zip(range(3),(0,1.2,2.4)):
        t,y = A[(f'DVM_O<{j}>','tt',d,27)]; ax[r].plot(t*1e9, y+off, color=cols[d], lw=0.9)
    ax[r].set_yticks([0.5,1.7,2.9]); ax[r].set_yticklabels(['DVM_O<0>','DVM_O<1>','DVM_O<2>'], fontsize=6)
    ax[r].set_ylabel(f'{int(d*100)}%', rotation=0, labelpad=14, va='center')
ax[3].set_xlabel('Time (ns)'); ax[3].set_xlim(5,40)
fig.align_ylabels(ax); fig.savefig('fig_w1.pdf'); fig.savefig('fig_w1.png', dpi=200); plt.close(fig)
