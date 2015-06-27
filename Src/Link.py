__author__ = 'lich'

from Unit import *

# This file describes the base class of link
# All the specific link class should inherit this class

class Link:

    def __init__(self, id):
        # link ID is named as tuple of (start node id, destination node id)
        self.linkId = id

        # link capacity
        self.linkCap = 1.0 * Gb

        # Current Flow ids on this link
        self.flowIds = []

        self.flowRates = dict()

        # Scheduling strategy of this link
        # Weight fair queueing, strict priority queueing, Max-min Fair (Default)
        self.scheduling = 'maxmin'

    def SetCap(self, cap):
        self.linkCap = float(cap * Gb)

    def SetScheduling(self, sched):
        if sched == 'maxmin' or sched == 'wfq' or sched == 'sp':
            self.scheduling = sched
        else:
            print("Error: " + sched + ' is unavailable. Try \'maxmin\', \'wfq\', or \'sp\'')

    def UpdateRates(self, flow):
        # Assign rates to all flows, and return the rate of input flow
        if self.scheduling == 'maxmin':
            curBw = self.linkCap / len(self.flowIds)
        elif self.scheduling == 'wfq':
            # Active queues
            # Shares of this flow's queue
            # share = bw * weightOwnQ / sumActiveWeights
            # Share of this flow in its queue
            # curBw = share / len(flowsInSameQueue)
            pass
        elif self.scheduling == 'sp':
            # highest = max(self.flowIds, key=lambda x: x.priority)
            # if flow.priority == highest.priority:
            #   all_highest = [f for f in self.flowIds if f.priority == highest.priority]
            #    curBw = self.linkCap / len(all_highest)
            # else:
            #    curBw = 0.0001 # to avoid division by zero errors
            pass

        for fid in self.flowIds:
            self.flowRates[fid] = curBw

        # self.flowRates[flow] = curBw
        return self.flowRates[flow.flowId]

    def __del__(self):
        pass
