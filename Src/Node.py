__author__ = 'lich'

# This file describes the base class of node
# All the specific node class should inherit this class

class Node:

    def __init__(self):
        # node ID
        self.nodeId = -1

        # neibor node Id list
        self.adjNodeIds = []

        # current flows on this node, elements are flow id
        self.flowIds = []

    def __del__(self):
        pass
