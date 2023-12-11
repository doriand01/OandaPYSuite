from numpy import diff

import decimal

decimal.getcontext().prec = 6
D = decimal.Decimal

secx = 1
minx = secx * 60
hrx = minx * 60
dayx = hrx * 24
weex = dayx * 7

candlex = {
    'S5'   : secx * 5,
    'S10'  : secx * 10,
    'S30'  : secx * 30,
    'M1'   : minx,
    'M5'   : minx * 5,
    'M10'  : minx * 10,
    'M30'  : minx * 30,
    'H1'   : hrx,
    'H2'   : hrx * 2,
    'H4'   : hrx * 4,
    'H12'  : hrx * 12,
    'D'    : dayx,
    'W'    : weex,
    'M'    : dayx * 30 # problematic
}








