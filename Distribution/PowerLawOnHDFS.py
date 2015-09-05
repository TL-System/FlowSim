__author__ = 'lich'

import sys
sys.path.append("..")

import random, getopt
from HDFS import *
from RandomGenerator.PowerLaw import *
from RandomGenerator.Poisson import *
from Topology.FatTree import *
from Src.Unit import *

# The port number of each switch in fat-tree topology
K = 4
# Flow size is in MB
flowSize = 100.0 * MB
# The mean of poisson arrival rate
mean = 10
# The skewness factor of power-law distribution
alpha = 1.0
# This parameter is used to indicates the number of distinct chunks in HDFS by numOfServers*factor
factor = 10
# The number of flows in the simulation
nflows = 35000

opts, args = getopt.getopt(sys.argv[1:], "K:S:L:a:f:N:", ["K=", "S=", "L=", "a=", "f=", "N="])
for o, a in opts:
    if o in ("-K", "--K"):
        K = int(a)
    elif o in ("-S", "--S"):
        flowSize = float(a) * MB
    elif o in ("-L", "--L"):
        mean = int(a)
    elif o in ("-a", "--a"):
        alpha = float(a)
    elif o in ("-f", "--f"):
        factor = int(a)
    elif o in ("-N", "--N"):
        nflows = int(a)

inDir = "PowerlawFlows/"


def AllocateFlows(topo, hdfs, pl, ps):
    # accessList allocates each server's target chunkId list
    accessList = [[] for i in range(topo.numOfServers)]
    # it starts from 1
    accessList.insert(0, None)
    # get power-law distribution
    dist = pl.GetDistribution()
    # chunkId is defined as chunk Id. Here id indicates the index in distinct chunk array.
    chunkId = 1
    # Sequentially allocates chunk to servers by their rank, 1,2,3...
    for accessTimes in dist:
        # accessTimes is the number of access times for current chunk
        # randomly choose a server to start
        serverId = random.randint(1, topo.numOfServers)
        # then allocates the chunk for each next server to access
        while accessTimes > 0:
            accessList[serverId].append(chunkId)
            serverId += 1
            if serverId > topo.numOfServers:
                serverId = 1
            accessTimes -= 1
        # allocates next chunk
        chunkId += 1

    # map target chunkId into server Id
    # Note that this should be the part of routing engine, I will move it to routing engine later

    # flow list
    flowList = [[] for i in range(topo.numOfServers)]
    # index from 1
    flowList.insert(0, None)
    # generate flows in pair of server Id other than serverId-->chunkId
    for sId in range(1, topo.numOfServers + 1):
        for cId in accessList[sId]:
            # bypass the flow that src and dst are equal
            if sId in hdfs.chunksLocation[cId]:
                continue
            # set dst id to server Id other than chunk Id
            flowList[sId].append(random.choice(hdfs.chunksLocation[cId]))
    totalFlows = sum([len(flows) for flows in flowList[1:]])
    # now, print the real flow input, wassssup!!!
    f_name = inDir + "K%d_input_L%d_a%0.1f.txt" % (K, mean, alpha)
    f = open(f_name, "w")
    startTime = 0.0
    flowId = 1
    # This allocation scheme is tricky because we allocate a flow's start time
    # sequentially for all the servers as one round.
    # Next round, we still traverse each server for one flow.
    # This is to avoid to continuously start two flows from the same server.
    round = 0
    while flowId <= totalFlows:
        for sId in range(1, topo.numOfServers + 1):
            # offset indicates the current round
            if len(flowList[sId]) > round:
                # we can allocate a flow to this server in this round
                print >> f, "%d\t%d\t%d\t%f" % (sId, flowList[sId][round], flowSize, startTime)
                startTime += ps.GetPoissonNumber()
                flowId += 1
            else:
                continue
        # next round
        round += 1

    f.close()

def main():
    """
    Now we just provide allocation function for power-law distribution in traditional HDFS distribution.
    """
    topo = FatTree(K)
    # now we only support the number of 3 as the default number of replicas for each chunk
    replicas = 3
    # the total number of distinct chunks in HDFS
    numOfDifChunks = topo.numOfServers * factor
    # allocates the hdfs
    hdfs = AllocChunks(numOfDifChunks, replicas, topo.numOfServers, topo)
    # initialize the power-law generator
    pl = PowerLaw(alpha, nflows, numOfDifChunks)
    # initialize the poisson arrival rate
    ps = PoissonRand(mean=mean, bound=1.0 / mean * 10.0)
    # allocates flows
    AllocateFlows(topo, hdfs, pl, ps)

if __name__ == "__main__":
    main()
