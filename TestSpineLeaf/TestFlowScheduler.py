__author__ = 'lich'
import sys
sys.path.append("..")

from Src.FlowScheduler import *
from Src.Flow import *

inDir = "Input/"
outDir = "Output/"

class TestFlowScheduler(FlowScheduler):
    def AssignFlows(self, args):
        """
        The args is a tuple containing: K, S, L, a, which are following the parameters in GenFlowInput.py
        """
        self.flowSize = float(args[0])
        self.mean = int(args[1])
        self.avgFlowNums = int(args[2])
        self.alpha = float(args[3])
        f_name = inDir + "S%0.0f_L%d_a%d_flows.txt" \
                 % (self.flowSize, self.mean, self.avgFlowNums)
        f = open(f_name, "r")
        for line in f.readlines():
            l = line.split()
            flow = Flow()
            flow.startId = int(l[0])
            flow.endId = int(l[1])
            flow.SetFlowSize(float(l[2]))
            flow.startTime = float(l[3])
            flow.flowId = len(self.flows) + 1
            self.flows.append(flow)
        FlowScheduler.AssignFlows(self)
        f.close()

    def PrintFlows(self):
        f_name = outDir + "S%0.0f_L%d_a%0.1f_out.txt" \
                 % (self.flowSize, self.mean, self.alpha)
        f = open(f_name, "w")
        f_name = outDir + "S%0.0f_L%d_a%0.1f_plot.dat" \
                 % (self.flowSize, self.mean, self.alpha)
        f_plot = open(f_name, "w")
        for flow in self.finishedFlows:
            flowTransTime = flow.finishTime - flow.startTime
            print >> f, "flow %d used %f\t%f\t%f" % (flow.flowId, flowTransTime, flow.startTime, flow.finishTime)
            flow.bw = flow.flowSize / flowTransTime
        # print bandwidth (in Mbps) in each line with sorted format
        bwList = [flow.bw for flow in self.finishedFlows]
        bwList.sort()
        num = len(bwList)
        for i in range(num):
            print >> f_plot, "%f\t%f" % (bwList[i] / Mb, float(i + 1) / num)
        f.close()
        f_plot.close()
