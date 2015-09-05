__author__ = 'lich'

import sys

sys.path.append("..")

import getopt

from Src.Simulator import *
from TestFlowScheduler import *
# from Topology.SpineLeaf import *
from Routing.ECMP_SpineLeaf import *

# TODO: add in topology description for spine leaf
# Flow size is in MB
flowSize = 100.0
# The mean of poisson arrival rate
mean = 10
# The average number of flows generated of each server node
avgFlowNum = 1
# alpha for power-law
alpha = 1.0

opts, args = getopt.getopt(sys.argv[1:], "S:L:a:f:", ["S=", "L=", "a=", "f="])
for o, a in opts:
    if o in ("-S", "--S"):
        flowSize = float(a)
    elif o in ("-L", "--L"):
        mean = int(a)
    elif o in ("-a", "--a"):
        avgFlowNum = int(a)
    elif o in ("-f", "--f"):
        alpha = float(a)


def main():
    sim = Simulator()
    testTopo = SpineLeaf()
    testTopo.CreateTopology()
    sim.AssignTopology(topo=testTopo, cap=1.0 * Gb)
    sim.AssignRoutingEngine(Routing=ECMP)
    sim.AssignScheduler(FlowScheduler=TestFlowScheduler, args=(flowSize, mean, avgFlowNum, alpha))
    sim.Run()

if __name__ == "__main__":
    main()
