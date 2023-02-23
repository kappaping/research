## Main function

from math import *
import numpy as np
import time

import sys
sys.path.append('../lattice')
import lattice as ltc
import tightbinding as tb


ltype='ka'
print(ltc.ltcname(ltype))
Nbl=[2,2,1]
Nsl=ltc.slnum(ltype)
Nltc=[Nbl,Nsl]
Nfl=1
Nall=[Nltc,Nfl]
Nst=tb.stnum(Nall)
print('State number = ',Nst)
bc=1
rs=ltc.ltcsites(Nall[0])

[print([r,fl],tb.stid(r,fl,Nall)) for r in rs for fl in range(Nfl)]

htb=[0.,-1.,0.]
time1=time.time()
H=tb.tbham(htb,rs,Nall,bc,ltype)
time2=time.time()
print('time = ',time2-time1)
print(H)



