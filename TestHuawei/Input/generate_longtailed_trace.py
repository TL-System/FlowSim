import sys
sys.path.append("../..")

import csv
import math
from random import choice
from Topology.SpineLeaf import *

for line in sys.stdin:
    l = line.rstrip('\r\n').split(',')
    repeat_number = int(math.ceil(10.0/float(l[6])))
    l[6] = float(l[6])*1024*1024
    l[6] = str(l[6])
    l[4] = float(l[4])/1000
    l[4] = str(l[4])
   # print repeat_number
    for i in range(repeat_number*8):
        l[0] = choice(range(SERVER*TOR))
        l[2] = choice(range(SERVER*TOR))
        if l[0]/SERVER == l[2]/SERVER:
            l[0] = (l[0]+SERVER)%(SERVER*TOR)
        l[0] = str(l[0])
        l[2] = str(l[2])
        line_toprint = ','.join(map(str, l))
        print line_toprint.rstrip('\r\n')

