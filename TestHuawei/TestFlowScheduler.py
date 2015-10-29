import sys
import csv

sys.path.append("..")

from Src.FlowScheduler import *
from Src.Flow import *
from Src.Unit import *

inDir = "Input/"
outDir = "Output/"


class TestFlowScheduler(FlowScheduler):
    def AssignFlows(self, topo, filename="Input/trace.csv"):
        # print sum(1 for li in open(filename,'r'))
        f = open(filename, "r")
        coflowsize = {}
        coflowwidth = {}
        line_count = 0
        for line in f.readlines():
            l = line.rstrip('\r\n').split(',')
            line_count += 1
            for i in range(1):
                # print l
                flow = Flow()
                flow.startId = int(l[0])
                flow.endId = int(l[2])
                # flow.startId = choice(range(topo.numOfServers-20)) + int(l[0])
                # flow.endId = choice(range(topo.numOfServers-20)) + int(l[2])
                # if flow.startId/topo.serverPerRack == flow.endId/topo.serverPerRack:
                #    flow.endId = (flow.endId + topo.serverPerRack)%topo.numOfServers
                # flow.SetFlowSize(float(l[6])*1024*1024)
                flow.SetFlowSize(float(l[6]))
                flow.startTime = float(l[4])
                flow.coflowId = int(l[5])
                if flow.coflowId not in coflowsize:
                    coflowsize[flow.coflowId] = flow.flowSize
                    coflowwidth[flow.coflowId] = 1
                else:
                    coflowsize[flow.coflowId] += flow.flowSize
                    coflowwidth[flow.coflowId] += 1
                flow.flowId = len(self.flows)
                self.flows.append(flow)
                # if line_count == 100:
                #    break

        FlowScheduler.AssignFlows(self)
        # print "number of input flows = ",len(self.flows)
        f.close()

        f = open("Input/coflow_in.csv", "w")
        writer = csv.writer(f)
        writer.writerow(['id', 'volume', 'count'])
        for k in coflowsize:
            writer.writerow([k, coflowsize[k], coflowwidth[k]])
        f.close()

    def PrintFlows(self):
        f_name = outDir + "out.txt"
        f = open(f_name, "w")
        f_name = outDir + "plot.dat"
        f_plot = open(f_name, "w")
        f_name = outDir + "coflow.txt"
        f_coflow = open(f_name, "w")
        coflow = {}
        average_flowTransTime = 0.0
        flowTransTimes = []
        for flow in self.finishedFlows:
            flowTransTime = (flow.finishTime - flow.startTime) / flow.flowSize
            average_flowTransTime += flowTransTime
            flowTransTimes.append(flowTransTime)
            print >> f, "%d\t%f\t%f\t%f" % (flow.flowId, flowTransTime, flow.startTime, flow.finishTime)
            flow.bw = flow.flowSize / flowTransTime
            # processing coflows output
            if flow.coflowId not in coflow:
                coflow[flow.coflowId] = (flow.startTime, flow.finishTime, flowTransTime)
            else:
                coflowStart, coflowEnd, coflowCompletion = coflow[flow.coflowId]
                if coflowStart > flow.startTime:
                    coflowStart = flow.startTime
                if coflowEnd < flow.finishTime:
                    coflowEnd = flow.finishTime
                coflowCompletion = coflowEnd - coflowStart
                coflow[flow.coflowId] = (coflowStart, coflowEnd, coflowCompletion)

        average_flowTransTime = average_flowTransTime / len(self.finishedFlows)
        print "average flow transmission time = ", average_flowTransTime
        flowTransTimes.sort()
        # get the 99.99-th percentile flow transmission time.
        FTT_index = int(len(flowTransTimes) - 1)
        flowTransTimes.sort()
        target_flowTransTime = flowTransTimes[FTT_index]
        print "the 99.99-th percentile flow transmission time = ", target_flowTransTime

        for k in coflow:
            print >> f_coflow, "{}\t{}\t{}\t{}".format(k, coflow[k][0], coflow[k][1], coflow[k][2])

        # print bandwidth (in Mbps) in each line with sorted format
        bwList = [flow.bw for flow in self.finishedFlows]
        bwList.sort()
        num = len(bwList)
        for i in range(num):
            print >> f_plot, "%f\t%f" % (bwList[i] / Mb, float(i + 1) / num)

        f.close()
        f_plot.close()
        f_coflow.close()


if __name__ == "__main__":
    tfs = TestFlowScheduler()
    tfs.AssignFlows()
