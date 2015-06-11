__author__ = 'lich'

# This file describes the base class of Routing
# All the specific routing class should inherit from this class

class Routing:
    def __init__(self, topo=None):
        # path is identified by source node ID and destination node ID
        self.pathList = {}
        self.topo = topo

    def BuildAllPath(self):
        """
        This method build path for each pair of nodes in topo.
        This is the core component since it indicates the routing mechanism: how to build path bewteen a source and a destination.
        """
    def BuildPath(self, srcId, dstId):
        """
        This method can be inherited as requiring.
        Only compute one path presented by source and destination id
        """

    def GetPath(self, srcId, dstId):
        """
        After calling BuildPath, a path exists between each source and destination.
        This return a node id list start from sourceId and terminated at destination Id.
        """
        return self.pathList[srcId, dstId]

    def BFS(self):
        """
        For each node, use BFS to generate shortest path from this node to each other nodes
        Path length is calculated by hop numbers.
        """
        nodes = self.topo.GetNodes()
        # the first node is None, node id is start from 1
        for curNode in nodes[1:]:
            # clean nodes color and parent node id
            for node in nodes[1:]:
                # 0 means unmarked, 1 means marked
                node.color = 0
                # parent node(id) is itself
                node.parent = node.nodeId
            curNodeId = curNode.nodeId
            # path towards self is only self id
            self.pathList[curNodeId, curNodeId] = [curNodeId]
            curNode.color = 1
            # enqueue & dequeue
            queue = []
            queue.append(curNode)
            while queue:
                visitNode = queue.pop(0)
                visitNodeId = visitNode.nodeId
                for adjId in visitNode.adjNodeIds:
                    adjNode = nodes[adjId]
                    if adjNode.color == 0:
                        adjNode.parent = visitNodeId
                        adjNode.color = 1
                        self.pathList[curNodeId, adjId] = self.pathList[curNodeId, visitNodeId][:]
                        self.pathList[curNodeId, adjId].append(adjId)
                        queue.append(adjNode)


    def __del__(self):
        pass
