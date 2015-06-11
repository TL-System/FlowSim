__author__ = 'lich'

from Unit import *

# This file describes the design of class Topology
# Note that each node and link can be customized class by inherit Node and Link

class Topology:

    def __init__(self):
        # node list in topology. Node id is also the index in list. node id is start from 1
        self.nodes = []
        # link list in topology. Indexed by the node id pair (start id, end id).
        self.links = {}

    def CreateTopology(self):
        """
        This function assigns the nodes and links.
        The parameter for this function could be a matrix or other things.
        """
    def SetAllCapacity(self, cap=1.0 * Gb):
        """
        Set capacity to all the links.
        """
        for linkId in self.links:
            self.SetLinkCapacity(linkId, cap)

    def SetLinkCapacity(self, linkId, cap):
        """
        Set link capacity
        """
        if linkId in self.links:
            self.links[linkId].linkCap = cap

    def GetNodes(self):
        """
        Return all the nodes in topology.
        """
        return self.nodes

    def GetNode(self, nodeId):
        return self.nodes[nodeId]

    def GetLinks(self):
        """
        Return all the links in topology
        """
        return self.links

    def GetLink(self, linkId):
        if linkId in self.links:
            return self.links[linkId]
        else:
            print "Link id %d is not found" % linkId
            return None

    def GenTopoFromMatrix(self, topoMatrix, n, NodeType, LinkType):
        """
        topoMatrix is a n*n adjcent matrix.
        n is the number of nodes.
        """
        # node id is start from 1, thus the first element is None
        self.nodes.append(None)

        for i in range(0, n):
            node = NodeType()
            node.nodeId = i + 1
            for j in range(0, n):
                if topoMatrix[i][j] == 1:
                    node.adjNodeIds.append(j + 1)
                    self.links[i + 1, j + 1] = LinkType((i + 1, j + 1))
            self.nodes.append(node)

        







