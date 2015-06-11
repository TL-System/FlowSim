__author__ = 'lich'

from Unit import *

# This file describes the class Flow.
# Any specific flow class should inherit from this class

class Flow:
    def __init__(self):
        # Flow Id
        self.flowId = -1

        # Flow size
        self.flowSize = 0.0

        # Remain size
        self.remainSize = 0.0

        # Obtained bandwidth
        self.bw = 0.0

        # Start&End node id for this flow
        self.startId = -1
        self.endId = -1

        # Path nodes
        self.pathNodeIds = []

        # Path links
        self.pathLinkIds = []

        # Start time
        self.startTime = 0.0

        # Update time
        # # The time of last update of flow states
        self.updateTime = 0.0

        # Finish time
        self.finishTime = 0.0

        # Job Id: this flow may be contained by a job
        # Each flow is only contained by one job and one
        # a job have many tasks, a task has many coflows, a asdcoflow has many flows.
        self.jobId = 0
        self.taskId = 0
        self.coflowId = 0

        # Priority / Service
        self.priority = -1

    def SetFlowSize(self, size):
        self.flowSize = size
        self.remainSize = size

    # Routing with give a list of nodes that this flow traverses
    # BuildPath() builds a path with pathNodeIds[:]
    def BuildPath(self, pathNodeIds):
        # Build path in node ids
        #self.pathNodeIds = pathNodeIds[:]
        self.pathNodeIds = pathNodeIds
        # Build path in link ids
        # Append tuple of nodes as links.
        for i in range(1, len(pathNodeIds)):
            self.pathLinkIds.append((pathNodeIds[i - 1], pathNodeIds[i]))
