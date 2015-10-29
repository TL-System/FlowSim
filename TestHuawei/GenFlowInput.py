

import sys
sys.path.append("..")

import random, getopt
from RandomGenerator.Poisson import *
from Src.Unit import *

# Flow size is in MB
flowSize = 100.0 * MB
# The mean of poisson arrival rate
mean = 10
# The average number of flows generated of each server node
avgFlowNum = 1

opts, args = getopt.getopt(sys.argv[1:], "S:L:a:", ["S=", "L=", "a="])
for o, a in opts:
    if o in ("-S", "--S"):
        flowSize = float(a) * MB
    elif o in ("-L", "--L"):
        mean = int(a)
    elif o in ("-a", "-a"):
        avgFlowNum = int(a)

inDir = "Input/"

def SpineLeafFlowInput():
    """
    This is function is used to generate flows launched in a Spine-Leaf topology.
    Each server node starts a flow. The flow arrival rate follows a poisson arrival.
    As default, there are 10 flows starts in every second.
    """
    f_name = inDir + "S%0.0f_L%d_a%d_flows.txt" % (flowSize / MB, mean, avgFlowNum)
    f = open(f_name, "w")
    #
    flowNums = 16  # SpineLeaf.numberOfServers
    startTime = 0.0
    randPoisson = PoissonRand(mean=mean, bound=1.0 / mean * 10.0)
    for j in range(avgFlowNum):
        for i in range(0, flowNums):
            startId = i
            endId = random.randint(0, flowNums-1)
            if endId == startId:
                endId = (startId + random.randint(1, flowNums / 2)) % flowNums
            startTime += randPoisson.GetPoissonNumber()
            print >> f, "%d\t%d\t%d\t%f" % (startId, endId, flowSize, startTime)

    f.close()

if __name__ == "__main__":
    SpineLeafFlowInput()
