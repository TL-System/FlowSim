__author__ = 'lich'

import os
import sys
import getopt

routing_scheme = ""

opts, args = getopt.getopt(sys.argv[1:], "r:", ["routing="]) 

for o, a in opts:
    if o in ("-r","--routing"):
        routing_scheme = a

if routing_scheme != "":
   os.system("python TestSimulator.py -r " + routing_scheme)
else:
   os.system("python TestSimulator.py")
