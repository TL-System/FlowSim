__author__ = 'lich'

import sys
sys.path.append("..")

import random, getopt
from RandomGenerator.Poisson import *
from Src.Unit import *

# The port number of each switch in fat-tree topology
K = 4
# Flow size is in MB
flowSize = 100.0 * MB
# The mean of poisson arrival rate
mean = 10
# The average number of flows generated of each server node
avgFlowNum = 1

opts, args = getopt.getopt(sys.argv[1:], "K:S:L:a:", ["K=", "S=", "L=", "a="])
for o, a in opts:
    if o in ("-K", "--K"):
        K = int(a)
    elif o in ("-S", "--S"):
        flowSize = float(a) * MB
    elif o in ("-L", "--L"):
        mean = int(a)
    elif o in ("-a", "-a"):
        avgFlowNum = int(a)

inDir = "Input/"

def FatTreeFlowInput():
    """
    This is function is used to generate flows launched in a fat-tree topology.
    Each server node in fat-tree starts a flow. The flow arrival rate follows a poisson arrival.
    As default, there are 10 flows starts in every second.
    """
    f_name = inDir + "K%d_S%0.0f_L%d_a%d_flows.txt" % (K, flowSize / MB, mean, avgFlowNum)
    f = open(f_name, "w")
    flowNums = K ** 3 / 4
    startTime = 0.0
    randPoisson = PoissonRand(mean=mean, bound=1.0 / mean * 10.0)
    for j in range(avgFlowNum):
        for i in range(1, flowNums + 1):
            startId = i
            endId = random.randint(1, flowNums)
            if endId == startId:
                endId = (startId + random.randint(1, flowNums / 2)) % flowNums + 1
            startTime += randPoisson.GetPoissonNumber()
            print >> f, "%d\t%d\t%d\t%f" % (startId, endId, flowSize, startTime)

    f.close()

if __name__ == "__main__":
    FatTreeFlowInput()
