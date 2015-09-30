__author__ = 'lich'

import sys
sys.path.append("..")

from Topology.SpineLeaf import *
from Src.Routing import *
from random import choice
import gc

class ECMP(Routing):
    """
    This routing approach is specific for spine-leaf topology
    """
    def __init__(self, topo):
        Routing.__init__(self, topo)
        self.numOfServers = topo.numOfServers
        self.serverPerRack = topo.serverPerRack
        self.numOfToRs = topo.numOfToRs
        self.numOfCores = topo.numOfCores

    def BuildAllPath(self):
        self.CalculateAllPath()

    def BuildPath(self, srcId, dstId, flow, flows):
        self.CalculatePath(srcId, dstId, flow)

    def CalculateAllPath(self):
        """
        This function calculate path between each pair of servers with ECMP
        For spine-leaf, choosing a path is essentially choosing a spine to traverse
        """
        for srcId in range(self.numOfServers):
            #gc.collect()
            for dstId in range(self.numOfServers):
                self.CalculatePath(srcId=srcId, dstId=dstId)

    def CalculatePath(self, srcId, dstId, flow):
        # only self id is contained, if destination is self
        if srcId == dstId:
            self.pathList[srcId, dstId] = [srcId]
            return
        srcToRId = self.numOfServers + srcId / self.serverPerRack
        dstToRId = self.numOfServers + dstId / self.serverPerRack
        # if src and dst are in the same tor switch
        if srcToRId == dstToRId:
            self.pathList[srcId, dstId] = [srcId, srcToRId, dstId]
            return
        # src-dst must traverse core
        else:
            # prick random core
            rcore = choice(range(self.numOfServers + self.numOfToRs, self.numOfServers + self.numOfToRs + self.numOfCores))
            self.pathList[srcId, dstId] = [srcId, srcToRId, rcore, dstToRId, dstId]

    def __del__(self):
        pass
