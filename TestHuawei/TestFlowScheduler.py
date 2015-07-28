__author__ = 'lich'
import sys

sys.path.append("..")

from Src.FlowScheduler import *
from Src.Flow import *

inDir = "Input/"
outDir = "Output/"


class TestFlowScheduler(FlowScheduler):
    def AssignFlows(self, filename="Input/trace.csv"):
        f = open(filename, "r")
        for line in f.readlines():
            l = line.rstrip('\r\n').split(',')
            # print l
            flow = Flow()
            flow.startId = int(l[0])
            flow.endId = int(l[2])
            flow.SetFlowSize(float(l[6]))
            flow.startTime = float(l[4])
            flow.coflowId = int(l[5])
            flow.flowId = len(self.flows) + 1
            self.flows.append(flow)
        FlowScheduler.AssignFlows(self)
        f.close()

    def PrintFlows(self):
        f_name = outDir + "out.txt"
        f = open(f_name, "w")
        f_name = outDir + "plot.dat"
        f_plot = open(f_name, "w")
        for flow in self.finishedFlows:
            flowTransTime = flow.finishTime - flow.startTime
            print >> f, "%d\t%f\t%f\t%f" % (flow.flowId, flowTransTime, flow.startTime, flow.finishTime)
            flow.bw = flow.flowSize / flowTransTime
        # print bandwidth (in Mbps) in each line with sorted format
        bwList = [flow.bw for flow in self.finishedFlows]
        bwList.sort()
        num = len(bwList)
        for i in range(num):
            print >> f_plot, "%f\t%f" % (bwList[i] / Mb, float(i + 1) / num)
        f.close()
        f_plot.close()


if __name__ == "__main__":
    tfs = TestFlowScheduler()
    tfs.AssignFlowsCSV()
