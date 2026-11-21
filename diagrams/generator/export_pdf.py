import build  # builds figures
from build import DVM, TRC, TDC, TAP
DVM.pdf("P1G11_DVM_top.pdf", 7.0, 7.0)
TDC.pdf("P1G11_DVM_TDC.pdf", 4.25, 6.0)
TAP.pdf("P1G11_TAP_CAL.pdf", 2.85, 5.4)
