__author__ = 'lich'

from Flow import *

class Job:
    """
    Deprecated as of Jun.10.2015
    Each job contains at least one flow. Each flow in the job
    For example, flow 3 will start just after flow 2 finished transferring.
    """
    def __init__(self, id = 0):
        self.jobId = id
        pass

    def SetFlows(self, flowNums, flowInfoList, startTime):
        """
        flowInfList contain <flowNums> element and each element is formed as:
        (startId, endId, flowSize)
        """
        self.flowNums = flowNums
        self.jobStartTime = startTime
        self.jobFinishTime = startTime
        self.flows = [None]
        # add each flow into flow list
        for i in range(flowNums):
            f = Flow()
            f.startId = flowInfoList[i][0]
            f.endId = flowInfoList[i][1]
            f.remainSize = flowInfoList[i][2]
            f.startTime = startTime
            f.finishTime = startTime
            self.flows.append(f)
        self.curFlowId = 0

    def GetNewFlow(self):
        self.curFlowId += 1
        if self.curFlowId > self.flowNums:
            return None
        return self.flows[self.curFlowId]

    def __del__(self):
        pass
