__author__ = 'lich'

import sys
sys.path.append("..")

from Topology.FatTree import *
from Src.Routing import *

import gc

class ECMP(Routing):
    """
    This routing approach is specific for fat-tree topology
    """
    def __init__(self, topo):
        Routing.__init__(self, topo)
        self.K = topo.K
        self.numOfServers = topo.numOfServers

    def BuildAllPath(self):
        self.CalculateAllPath()

    def BuildPath(self, srcId, dstId):
        self.CalculatePath(srcId, dstId)

    def CalculateAllPath(self):
        """
        This function calculate path between each pair of servers with ECMP
        The path selection for upward is based on the downward port id on tor switch, which is fixed for each server
        For example, on a tor switch, for the flows send from a local server with downward port id x,
        the upward port id is x + K/2. The similar mechanism is used in aggregate switches
        As for downward port selection, it is fixed and no need to apply ECMP
        Note that besides serverId, switch Id is required to convert into node id
        """
        for srcId in range(1, self.numOfServers + 1):
            #gc.collect()        
            for dstId in range(1, self.numOfServers + 1):
                self.CalculatePath(srcId=srcId, dstId=dstId)

    def CalculatePath(self, srcId, dstId):
        # only self id is contained, if destination is self
        if srcId == dstId:
            self.pathList[srcId, dstId] = [srcId]
            return
        srcToRId = self.GetToRId(srcId)
        dstToRId = self.GetToRId(dstId)
        srcToRNodeId = self.topo.ConvertToNodeId(srcToRId, TOR)
        dstToRNodeId = self.topo.ConvertToNodeId(dstToRId, TOR)
        # if src and dst are in the same parent tor switch
        if srcToRId == dstToRId:
            self.pathList[srcId, dstId] = [srcId, srcToRNodeId, dstId]
            return
        srcAggrId = self.GetAggrId(srcId, srcToRId)
        srcAggrNodeId = self.topo.ConvertToNodeId(srcAggrId, AGGR)
        # if src and dst are in the same pod
        if self.IsSamePod(srcToRId, dstToRId):
            self.pathList[srcId, dstId] = [srcId, srcToRNodeId, srcAggrNodeId, dstToRNodeId, dstId]
            return
        # finally, this is the longest path: src->tor->aggr->core->aggr->tor->dst
        coreId = self.GetCoreId(srcToRId, srcAggrId)
        coreNodeId = self.topo.ConvertToNodeId(coreId, CORE)
        dstAggrId = self.GetAggrIdFromCore(coreId, dstToRId)
        dstAggrNodeId = self.topo.ConvertToNodeId(dstAggrId, AGGR)
        self.pathList[srcId, dstId] = [srcId, srcToRNodeId, srcAggrNodeId, coreNodeId, dstAggrNodeId,
                                       dstToRNodeId, dstId]

    def GetToRId(self, serverId):
        return (serverId - 1) / (self.K / 2) + 1

    def GetAggrId(self, serverId, torId):
        podId = (torId - 1) / (self.K / 2) + 1
        headAggrId = (podId - 1) * (self.K / 2) + 1
        return headAggrId + (serverId - 1) % (self.K / 2)

    def GetCoreId(self, torId, aggrId):
        headCore = ((aggrId - 1) % (self.K / 2)) * (self.K / 2) + 1
        return headCore + (torId - 1) % (self.K / 2)

    def IsSamePod(self, torA, torB):
        return (torA - 1) / (self.K / 2) == (torB - 1) / (self.K / 2)

    def GetAggrIdFromCore(self, coreId, torId):
        podId = (torId - 1) / (self.K / 2) + 1
        headAggrId = (podId - 1) * (self.K / 2) + 1
        return headAggrId + (coreId - 1) / (self.K / 2)

    def __del__(self):
        pass
