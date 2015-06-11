__author__ = 'lich'

import sys
sys.path.append("..")

from Src.Topology import *
from Src.Node import *
from Src.Link import *

SERVER = 0
TOR = 1
AGGR = 2
CORE = 3

class FatTree(Topology):
    def __init__(self, K=4):
        # initialize nodes and links
        Topology.__init__(self)
        # default topology size is K=4
        self.K = K
        # calculate servers number
        self.CalServerNums()
        # calculate tor switch number
        self.CalToRNums()
        # calculate aggregate switch number
        self.CalAggrNums()
        # calculate core switch number
        self.CalCoreNums()

    def CreateTopology(self):
        # create nodes
        self.CreateNodes()
        # create links
        self.CreateLinks()

    def CreateLinks(self):
        """
        We build this topology as a directed graph.
        It indicates n1 --- n2 will translate into to edges: (1, 2) and (2, 1)
        """
        for serverId in range(1, self.numOfServers + 1):
            s2torId = (serverId - 1) / (self.K / 2) + 1
            torNodeId = self.ConvertToNodeId(s2torId, TOR)
            self.links[serverId, torNodeId] = Link((serverId, torNodeId))
            self.links[torNodeId, serverId] = Link((torNodeId, serverId))
        for torId in range(1, self.numOfToRs + 1):
            podId = (torId - 1) / (self.K / 2) + 1
            torNodeId = self.ConvertToNodeId(torId, TOR)
            for i in range(0, self.K / 2):
                t2aggrId = (podId - 1) * (self.K / 2) + 1 + i
                aggrNodeId = self.ConvertToNodeId(t2aggrId, AGGR)
                self.links[torNodeId, aggrNodeId] = Link((torNodeId, aggrNodeId))
                self.links[aggrNodeId, torNodeId] = Link((aggrNodeId, torNodeId))
        for aggrId in range(1, self.numOfAggrs + 1):
            aggrNodeId = self.ConvertToNodeId(aggrId, AGGR)
            for j in range(0, self.K / 2):
                a2coreId = ((aggrId - 1) % (self.K / 2)) * (self.K / 2) + 1 + j
                coreNodeId = self.ConvertToNodeId(a2coreId, CORE)
                self.links[aggrNodeId, coreNodeId] = Link((aggrNodeId, coreNodeId))
                self.links[coreNodeId, aggrNodeId] = Link((coreNodeId, aggrNodeId))

    def CreateNodes(self):
         # node id is start from 1
        self.nodes.append(None)
        # append server node
        self.AddNodes(self.numOfServers)
        # append tor switch node
        self.AddNodes(self.numOfToRs)
        # append aggregate switch node
        self.AddNodes(self.numOfAggrs)
        # append core switch nodes
        self.AddNodes(self.numOfCores)

    # calculate related metircs
    def CalServerNums(self):
        self.numOfServers = self.K ** 3 / 4

    def CalToRNums(self):
        self.numOfToRs = self.K ** 2 / 2

    def CalAggrNums(self):
        self.numOfAggrs = self.K ** 2 / 2

    def CalCoreNums(self):
        self.numOfCores = self.K ** 2 / 4

    def GetRackId(self, serverId):
        return (serverId - 1) / (self.K / 2) + 1

    def GetSameRack(self, serverId):
        # return the server in the same rack next to self
        neighborId = serverId + 1
        # we say, if the neighborId mods 1 by K/2, it must be the first server in the next rack
        if neighborId % (self.K / 2) == 1:
            neighborId -= self.K / 2
        return neighborId

    def GetOtherRack(self, serverId, n):
        """
        This will return a serverId in another rack.
        """
        # return the server in the next rack with the same location, an offset of K/2
        neighborId = (serverId + self.K / 2) % n
        # neighborId is 0 means, this is the n'th server
        if neighborId == 0:
            neighborId = n
        return neighborId


    def GetPodId(self, rackId):
        return (rackId - 1) / (self.K / 2) + 1

    def ConvertToNodeId(self, id, role):
        """
        Convert regular device id into node id.
        Four roles are defined: 0:server, 1:tor switch, 2:aggregate switch, 3:core switch
        """
        if role == 0:
            return id
        elif role == 1:
            return id + self.numOfServers
        elif role == 2:
            return id + self.numOfServers + self.numOfToRs
        elif role == 3:
            return id + self.numOfServers + self.numOfToRs + self.numOfAggrs
        else:
            return 0
    # add n nodes to topology instance
    def AddNodes(self, n):
        for id in range(1, n + 1):
            node = Node()
            node.nodeId = len(self.nodes)
            self.nodes.append(node)

    # return corresponding role
    def GetServerNode(self, serverId):
        nodeId = self.ConvertToNodeId(serverId, SERVER)
        return self.nodes[nodeId]
    def GetToRNode(self, torId):
        nodeId = self.ConvertToNodeId(torId, TOR)
        return self.nodes[nodeId]
    def GetAggrNode(self, aggrId):
        nodeId = self.ConvertToNodeId(aggrId, AGGR)
        return self.nodes[nodeId]
    def GetCoreNode(self, coreId):
        nodeId = self.ConvertToNodeId(coreId, CORE)
        return self.nodes[nodeId]


    def __del__(self):
        pass
