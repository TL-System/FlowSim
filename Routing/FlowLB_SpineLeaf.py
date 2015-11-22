__author__ = 'lich'

import sys
sys.path.append("..")

from Topology.SpineLeaf import *
from Src.Routing import *
from random import choice
import gc

class FlowLB(Routing):
    """
    This routing approach is specific for spine-leaf topology
    """
    def __init__(self, topo):
        Routing.__init__(self, topo)
        #self.numOfServers = topo.numOfServers
        #self.serverPerRack = topo.serverPerRack
        #self.numOfToRs = topo.numOfToRs
        #self.numOfCores = topo.numOfCores
        self.topo=topo

    def BuildAllPath(self):
        self.CalculateAllPath()

    def BuildPath(self, srcId, dstId, flow, flows):
        self.CalculatePath(srcId, dstId, flow, flows)

  #  def CalculateAllPath(self):
  #      """
  #      This function calculate path between each pair of servers by choosing a core switch with least traversing        flows. For spine-leaf, choosing a path is essentially choosing a spine to travers
  #      """
  #      for srcId in range(1, self.numOfServers + 1):
  #          #gc.collect()
  #          for dstId in range(1, self.numOfServers + 1):
  #              self.CalculatePath(srcId=srcId, dstId=dstId)

    def GetCoreLeastFlow(self, flows, srcToRId, dstToRId):                            
        cores = []                                         
        for i in range(self.topo.numOfCores):                   
            cores.append(self.topo.GetCoreNode(i))            
        # print "cores {}".format(cores)     
        dc ={}
        for c in cores:
            fsize = 0.0
            for flowId in c.flowIds:
                if ( srcToRId in flows[flowId].pathNodeIds ) or ( dstToRId in flows[flowId].pathNodeIds ):
                   fsize += flows[flowId].remainSize
            dc[c] = fsize
        #for key in dc.keys():
            #print "key= ",key.nodeId," dc[key]= ",dc[key],"    "
        #print "min of dc ",min(dc, key=dc.get).nodeId
        return min(dc, key=dc.get)                         
    
    def GetCoreLeastQ(self):                               
        cores = []                                         
        for i in range(self.topo.numOfCores):                   
            cores.append(self.topo.GetCoreNode(i))         
        # print "cores {}".format(cores)                   
        dc = dict([(c, len(c.qvalue)) for c in cores])     
        return min(dc, key=dc.get)                         

    def CalculatePath(self, srcId, dstId, flow, flows):
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
            # prick random core
           # rcore = choice(range(self.numOfServers+self.numOfToRs+1, self.numOfServers + self.numOfToRs + self.numOfCores + 1))
           # if flow.coflowId == 0: 
            rcore=self.GetCoreLeastFlow(flows, srcToRId, dstToRId)
           #  else:
           #     rcore=self.topo.GetCoreNode(flow.coflowId % self.topo.numOfCores)
            rcoreId=rcore.nodeId
            self.pathList[srcId, dstId] = [srcId, srcToRId, rcoreId, dstToRId, dstId]
   

    def __del__(self):
        pass
