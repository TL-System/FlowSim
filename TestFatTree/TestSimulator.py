import sys

sys.path.append("..")

import getopt

from Src.Simulator import *
from TestFlowScheduler import *
from Routing.ECMP_FatTree import *

# The port number of each switch in fat-tree topology
K = 4
# Flow size is in MB
flowSize = 100.0
# The mean of poisson arrival rate
mean = 10
# The average number of flows generated of each server node
avgFlowNum = 1
# alpha for power-law
alpha = 1.0

opts, args = getopt.getopt(sys.argv[1:], "K:S:L:a:f:", ["K=", "S=", "L=", "a=", "f="])
for o, a in opts:
    if o in ("-K", "--K"):
        K = int(a)
    elif o in ("-S", "--S"):
        flowSize = float(a)
    elif o in ("-L", "--L"):
        mean = int(a)
    elif o in ("-a", "--a"):
        avgFlowNum = int(a)
    elif o in ("-f", "--f"):
        alpha = float(a)


def main():
    sim = Simulator()
    testTopo = FatTree(K=K)
    testTopo.CreateTopology()
    sim.AssignTopology(topo=testTopo, cap=1.0 * Gb)
    sim.AssignRoutingEngine(Routing=ECMP)
    sim.AssignScheduler(FlowScheduler=TestFlowScheduler, args=(K, flowSize, mean, avgFlowNum, alpha))
    sim.Run()


if __name__ == "__main__":
    main()
