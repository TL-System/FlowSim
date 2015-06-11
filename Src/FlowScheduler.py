__author__ = 'lich'

from Unit import *
# This file describes the class FlowScheduler
import sys

class FlowScheduler:
    def __init__(self):
        # Flow list in initial time
        self.flows = []

        # Flows to start
        self.toStartFlows = []

        # Running flows
        self.runningFlows = []

        # Finished flows
        self.finishedFlows = []

        # Topology Links. This should not be there. I will remove it in future version.
        self.Links = []

    def AssignLinks(self, links):
        """
        We need links information because we need to update flow info
        """
        self.Links = links

    def AssignFlows(self):
        """
        Assign flows including flow id, flow size, flow start id and end id, flow start time.
        It can read flow info from a configuration file or assigned by some parameters.
        Return the flow list.
        """
        self.toStartFlows = self.flows[:]
        self.toStartFlows.sort(key=lambda x: x.startTime)

    def GetFlow(self, flowId):
        """
        Note that a pair of node ids cannot identify a flow since there may have multiple flows between them.
        Flow id is the only identifier to pick a flow.
        """
        return self.flows[flowId]

    def GetAllFlows(self):
        return self.flows

    def UpdateFlowState(self, curTime, flow):
        # Update remain size
        flow.remainSize -= flow.bw * (curTime - flow.updateTime)
        flow.updateTime = curTime
        
        pathInLink = flow.pathLinkIds
        bw = 1.0 * Gb
        for linkId in pathInLink:
            link = self.Links[linkId]
            curBw = link.linkCap / len(link.flowIds)
            if bw > curBw:
                bw = curBw
        flow.bw = bw

        flow.finishTime = curTime + flow.remainSize / bw

    def UpdateFlow(self, curFlow, flag):
        """
        Find related flows and update their flowBw, transTime, endTime.
        """
        curTime = 0.0
        pathInLink = curFlow.pathLinkIds
        for linkId in pathInLink:
            link = self.Links[linkId]
            if flag == "remove":
                link.flowIds.remove(curFlow.flowId)
                curTime = curFlow.finishTime
            elif flag == "insert":
                link.flowIds.append(curFlow.flowId)
                curTime = curFlow.startTime
        for linkId in pathInLink:
            link = self.Links[linkId]
            for flowId in link.flowIds:
                flow = self.flows[flowId - 1]
                self.UpdateFlowState(curTime, flow)

    def PrintFlows(self):
        """
        print finishedFlows
        """
