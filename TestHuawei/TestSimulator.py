__author__ = 'lich'

import sys

#sys.path.append("..")

import getopt

from TestFlowScheduler import *
# from Topology.SpineLeaf import *
from Routing.ECMP_SpineLeaf import *
from Routing.LB_SpineLeaf import *
from Routing.Qlearning_SpineLeaf import *
from Src.Simulator import *

# TODO: add in topology description for spine leaf
# Flow size is in MB
flowSize = 100.0
# The mean of poisson arrival rate
mean = 10
# The average number of flows generated of each server node
avgFlowNum = 1
# alpha for power-law
alpha = 1.0


routing_dict = {'LB':LB, 'ECMP':ECMP, 'Qlearning':Qlearning}
routing_scheme = LB

opts, args = getopt.getopt(sys.argv[1:], "S:L:a:f:r:", ["S=", "L=", "a=", "f=", "routing="])
for o, a in opts:
    if o in ("-S", "--S"):
        flowSize = float(a)
    elif o in ("-L", "--L"):
        mean = int(a)
    elif o in ("-a", "--a"):
        avgFlowNum = int(a)
    elif o in ("-f", "--f"):
        alpha = float(a)
    elif o in ("-r","--routing"):
        routing_scheme = routing_dict[a]


def main():
    #print routing_scheme
    sim = Simulator()
    testTopo = SpineLeaf()
    testTopo.CreateTopology()
    sim.AssignTopology(topo=testTopo, cap=1.0 * Gb)
    sim.AssignRoutingEngine(Routing=routing_scheme)
    sim.AssignScheduler(FlowScheduler=TestFlowScheduler, args="Input/trace.csv")
    sim.Run()

if __name__ == "__main__":
    main()
