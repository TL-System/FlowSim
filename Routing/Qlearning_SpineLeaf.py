__author__ = 'lich'

import sys
sys.path.append("..")

from Topology.SpineLeaf import *
from Src.Routing import *
from random import choice
import gc

class Qlearning(Routing):
    """
    This routing approach is specific for spine-leaf topology
    """
    def __init__(self, topo):
        Routing.__init__(self, topo)
        #self.numOfServers = topo.numOfServers
        #self.serverPerRack = topo.serverPerRack
        #self.numOfToRs = topo.numOfToRs
        #self.numOfCores = topo.numOfCores
        self.topo = topo

    def BuildAllPath(self):
        self.CalculateAllPath()

    def BuildPath(self, srcId, dstId, flow, state):
        self.CalculatePath(srcId, dstId, flow, state)

    def CalculateAllPath(self):
        """
        This function calculate path between each pair of servers with ECMP
        For spine-leaf, choosing a path is essentially choosing a spine to traverse
        """
        for srcId in range(self.numOfServers):
            #gc.collect()
            for dstId in range(self.topo.numOfServers):
                self.CalculatePath(srcId=srcId, dstId=dstId)

    def select_action(self, state):
        """
        Run Qleanring algorithm to choose a core switch.
        """
        # randomly choose a core switch. Delete this after implementing Qlearning algorithm
        coreId = choice(range(self.topo.numOfServers + self.topo.numOfToRs, self.topo.numOfServers + self.topo.numOfToRs + self.topo.numOfCores))
        """
        Todo: implement qlearning algorithm
        """
        
        return coreId

    def CalculatePath(self, srcId, dstId, flow, state):
        # only self id is contained, if destination is self
        if srcId == dstId:
            self.pathList[srcId, dstId] = [srcId]
            return
        srcToRId = self.topo.numOfServers + srcId / self.topo.serverPerRack
        dstToRId = self.topo.numOfServers + dstId / self.topo.serverPerRack
        # if src and dst are in the same tor switch
        if srcToRId == dstToRId:
            self.pathList[srcId, dstId] = [srcId, srcToRId, dstId]
            return
        # src-dst must traverse core
        else:
            self.pathList[srcId, dstId] = [srcId, srcToRId, self.select_action(state), dstToRId, dstId]
    def __del__(self):
        pass
