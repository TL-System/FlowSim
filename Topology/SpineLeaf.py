__author__ = 'lich'

import sys

sys.path.append("..")

from Src.Topology import *
from Src.Node import *
from Src.Link import *
from math import ceil, floor

SERVER = 10
TOR = 20
CORE = 10


class SpineLeaf(Topology):
    def __init__(self, s=SERVER, t=TOR, c=CORE):
        # initialize nodes and links
        Topology.__init__(self)
        self.serverPerRack = s
        self.numOfServers = s * t
        self.numOfToRs = t
        self.numOfCores = c
        self.name = "spineleaf"

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
        # add links between servers and tors
        for s in range(0, self.numOfServers):
            # Get the tor that server s is connected to
            # servers with ID 0 to SERVER-1 is connected to switch with ID self.numberOfServers
            # t = self.numOfServers + s / self.serverPerRack
            t = self.numOfServers + s / self.serverPerRack
            # print s, self.serverPerRack, ceil(s / self.serverPerRack),
        
            self.links[s, t] = Link((s, t))
            self.links[t, s] = Link((t, s))

        # add links between tors and cores
        for t in range(self.numOfServers, self.numOfServers + self.numOfToRs):
            for c in range(self.numOfServers + self.numOfToRs,
                           self.numOfServers + self.numOfToRs + self.numOfCores):
                self.links[t, c] = Link((t, c))
                self.links[c, t] = Link((c, t))

    def CreateNodes(self):
        # node id start from 1
        #self.nodes.append(None)
        # append server node
        # [0, SERVER * TOR-1] are servers
        self.AddNodes(self.numOfServers)
        # append tor switch node
        # [SERVER * TOR, SERVER * TOR + TOR-1] are leaves
        self.AddNodes(self.numOfToRs)
        # append core switch nodes
        # [SERVER * TOR * CORE + TOR, SERVER * TOR * CORE + TOR + CORE-1] are spines
        self.AddNodes(self.numOfCores)

    # Given id of server, return id of rack
    # server and rack are numbered starting from 0
    def GetRackId(self, serverId):
        return serverId / SERVER

    def GetSameRack(self, serverId):
        # return the list of servers in the same rack with serverId
        rackId = self.GetRackId
        rackFirst = rackId * SERVER
        rackLast = rackFirst + SERVER
        rackList = range(rackFirst, rackLast)
        return rackList

    def GetOtherRack(self, serverId):
        """
        This will return a serverId in another rack.
        """
        # return the server in the next rack with the same location, an offset of K/2
        neighborId = (serverId + SERVER) % self.numOfServers
        return neighborId

    def ConvertToNodeId(self, id, role):
        """
        Convert regular device id into node id.
        Four roles are defined: 0:server, 1:tor switch, 2:core switch
        """
        if role == 0:
            return id
        elif role == 1:
            return id + self.numOfServers
        elif role == 2:
            return id + self.numOfServers + self.numOfToRs
        else:
            return 0

    # add n nodes to topology instance
    def AddNodes(self, n):
        for id in range(0, n):
            node = Node()
            node.nodeId = len(self.nodes)
            # print "len= ", len(self.nodes)
            # print "nodeid= ", node.nodeId
            self.nodes.append(node)
            # print node.nodeId

    # return corresponding role
    def GetServerNode(self, serverId):
        nodeId = self.ConvertToNodeId(serverId, 0)
        return self.nodes[nodeId]

    def GetToRNode(self, torId):
        nodeId = self.ConvertToNodeId(torId, 1)
        return self.nodes[nodeId]

    def GetCoreNode(self, coreId):
        nodeId = self.ConvertToNodeId(coreId, 2)
        return self.nodes[nodeId]

    def GetCores(self):
        return range(self.numOfServers+self.numOfToRs,
                     self.numOfServers+self.numOfToRs+self.numOfCores)

    def GetCoreLeastFlow(self):   #aborted 
        cores = []
        for i in range(self.numOfCores):
            cores.append(self.GetCoreNode(i))
        # print "cores {}".format(cores)
        dc = dict([(c, len(c.flowIds)) for c in cores])
        return min(dc, key=dc.get)

    def GetCoreLeastQ(self):     #aborted 
        cores = []
        for i in range(self.numOfCores):
            cores.append(self.GetCoreNode(i))
        # print "cores {}".format(cores)
        dc = dict([(c, len(c.qvalue)) for c in cores])
        return min(dc, key=dc.get)

    def __del__(self):
        pass
