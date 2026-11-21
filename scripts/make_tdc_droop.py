import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from matplotlib.colors import Normalize, ListedColormap
from matplotlib.cm import ScalarMappable
from matplotlib.lines import Line2D
plt.rcParams.update({"font.family":"serif","font.size":7,"savefig.dpi":300,"savefig.bbox":"tight",
    "savefig.pad_inches":0.02,"xtick.labelsize":6.5,"ytick.labelsize":6,"legend.fontsize":6})
Z = np.load('tt27_all.npz'); g = Z['grid']*1e9
levels = [('0','0%','0.25',1.00,20), ('0.05','5%','C0',0.95,16), ('0.1','10%','C1',0.90,12), ('0.15','15%','C3',0.85,9)]
tapcol = lambda k: plt.colormaps['Blues'](0.25 + 0.75*(31-k)/31)      # O<31> light ... O<0> dark
W0, W1 = 17.7, 20.2; w = (g>=W0)&(g<=W1)                                # one window at the droop bottom
def edges(vd):
    tc, yc, vv = g[w], Z[f'clkdiv_b_{vd}'][w], Z[f'VDD_DVM_{vd}'][w]
    rise = tc[np.where((yc[:-1] < 0.5*vv[:-1]) & (yc[1:] >= 0.5*vv[1:]))[0]]
    fall = tc[np.where((yc[:-1] > 0.5*vv[:-1]) & (yc[1:] <= 0.5*vv[1:]))[0]]
    return rise, fall
fig, ax = plt.subplots(5, 1, figsize=(3.5, 5.3), sharex=True, gridspec_kw={"hspace":0.12, "height_ratios":[0.8,1,1,1,1]})
for vd,lab,c,vdd,code in levels:
    ax[0].plot(g[w], Z[f'clkdiv_b_{vd}'][w], color=c, lw=0.9)
ax[0].set_ylabel('clkdiv_b (V)', fontsize=6.5); ax[0].set_ylim(-0.08, 1.12); ax[0].set_yticks([0, 1])
ax[0].text(0.995, 0.5, '(a) latch clock', transform=ax[0].transAxes, fontsize=5.8, ha='right', va='center')
handles = [Line2D([], [], color=c, lw=1.2, label=f'{lab} droop') for _,lab,c,_,_ in levels]
handles += [Line2D([], [], color='k', lw=0.8, ls=':', label='latches open'), Line2D([], [], color='k', lw=0.9, ls='--', label='latches close')]
fig.legend(handles=handles, ncol=3, loc='lower center', bbox_to_anchor=(0.47, 0.885), frameon=False, handlelength=1.8, columnspacing=1.0)
for r,(vd,lab,c,vdd,code) in enumerate(levels, start=1):
    a = ax[r]; T = Z[f'taps_{vd}']; v = Z[f'VDD_DVM_{vd}']
    for k in range(31, -1, -1): a.plot(g[w], T[k, w], color=tapcol(k), lw=0.7)
    rise, fall = edges(vd)
    for x in rise: a.axvline(x, color=c, lw=0.8, ls=':'); ax[0].axvline(x, color=c, lw=0.6, ls=':')
    for x in fall: a.axvline(x, color=c, lw=1.0, ls='--'); ax[0].axvline(x, color=c, lw=0.6, ls='--')
    i = int(round(20.0e-9/5e-12)); held = [k for k in range(32) if T[k, i] < 0.5*v[i] and k >= 8]
    a.text(0.995, 0.5, f'({"abcde"[r]}) {lab}, {vdd:.2f} V\nO<31:{min(held)}>, code {code}', transform=a.transAxes,
           ha='right', va='center', fontsize=5.8)
    a.set_ylim(-0.1, 1.15); a.set_yticks([0, 1]); a.set_ylabel('O<31:0> (V)', fontsize=6.5)
for a in ax: a.grid(axis='x', alpha=0.25)
ax[-1].set_xlim(W0, W1); ax[-1].set_xlabel('Time (ns)')
fig.align_ylabels(ax)
cax = fig.add_axes([0.93, 0.11, 0.018, 0.58])
cb = fig.colorbar(ScalarMappable(norm=Normalize(-0.5, 31.5), cmap=ListedColormap([tapcol(k) for k in range(32)])), cax=cax)
cb.set_ticks([0, 8, 16, 24, 31]); cb.set_label('k in O<k>  (O<31> = first stage)', fontsize=6); cb.ax.tick_params(labelsize=5.8)
fig.savefig('fig_tdc_droop.pdf'); fig.savefig('fig_tdc_droop.png', dpi=220); plt.close(fig)
print('ok')
