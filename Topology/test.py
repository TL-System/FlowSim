__author__ = 'lich'

from FatTree import *

topo = FatTree(K=4)
topo.CreateTopology()
f = open("output.txt", "w")
for linkId in topo.links:
    print >> f, linkId
f.close()



