__author__ = 'lich'

from Flow import *

class Coflow:
    """
    Each job contains at least one flow. Each flow in the job
    For example, flow 3 will start just after flow 2 finished transferring.
    """
    def __init__(self, id = 0):
        self.coflowId = id
        pass

    def SetFlows(self, flowNums, flowInfoList, startTime):
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

    def __del__(self):
        pass
