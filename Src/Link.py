from Unit import *


# This file describes the base class of link
# All the specific link class should inherit this class

class Link:
    def __init__(self, id, elephantflow_threshold=1.0 * Mb):
        # link ID is named as tuple of (start node id, destination node id)
        """

        :rtype : int
        """
        self.linkId = id

        self.elephantflow_threshold = elephantflow_threshold

        # link capacity
        self.linkCap = 1.0 * Gb

        # Current Flow ids on this link
        self.flowIds = []

        # Scheduling strategy of this link
        # Weight fair queueing, strict priority queueing, Max-min Fair (Default)
        self.scheduling = 'maxmin'

        self.queue = 0.0

        self.qvalue = 0.0

        self.congestionThreshold = 10

    def SetCap(self, cap):
        self.linkCap = float(cap * Gb)

    def SetScheduling(self, sched):
        if sched == 'maxmin' or sched == 'wfq' or sched == 'sp':
            self.scheduling = sched
        else:
            print("Error: " + sched + ' is unavailable. Try \'maxmin\', \'wfq\', or \'sp\'')

    def GetLinkUtilization(self, flows):
        usedbw = 0.0
        for fid in self.flowIds:
            usedbw += flows[fid].bw
        return usedbw / self.linkCap

    def GetActiveFlowNum(self):
        return len(self.flowIds)

    def GetActiveElephantFlowNum(self, flows):
        elephantflow_count = 0
        for flowid in self.flowIds:
            if flows[flowid].flowSize >= self.elephantflow_threshold:
                elephantflow_count += 1

        return elephantflow_count

    def GetActiveFlowRemainSize(self, flows):
        remainsize = 0.0
        for flowid in self.flowIds:
            remainsize += flows[flowid].remainSize

        return remainsize

    def IsCongested(self):
        if len(self.flowIds) > self.congestionThreshold:
            return True

    def __del__(self):
        pass
