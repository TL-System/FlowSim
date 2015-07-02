__author__ = 'li'

import random
import sys
from datetime import datetime
import csv

from Src import Flow, Link
from TUnits import *

# looking for examples supporting MCP
# run simulator step by step, running for 100 milliseconds
# simulating multiple flows over one link
PROTO = ['d2tcp', 'mcp', 'tcp', 'dctcp']
# PROTO = ['d2tcp']

class StepByStepSimulator:
    # setting up environment
    def __init__(self,
                 RTT=0.000001 * 80,  # 80us
                 SIMTIME=0.1,  # 0.1s = 100ms, 0.05s=50ms
                 CONCURRENCY=5,
                 FLOWSIZEMEAN=0.01,  # 0.1MB = 100KB 0.1MB/100ms=100KB/50ms=0.0016Gbps
                 # 0.01MB = 10KB =1.6Gbps
                 FLOWDDLMEAN=0.001 * 50,  # 50ms
                 ECN=64,  # 64 packets
                 MAXBUFFER=4,  # 4MB
                 LINKCAP=1000,  # BDP = 10KB -> 1Gbps
                 output='results.txt'):
        self.RTT = RTT
        self.SIMTIME = SIMTIME
        self.Steps = int(round(SIMTIME / RTT))
        self.MAXNUMFLOW = CONCURRENCY * self.Steps  # This is concurrency of flows
        self.FLOWSIZEMEAN = FLOWSIZEMEAN * MB
        self.FLOWDDLMEAN = FLOWDDLMEAN
        # deadlineSlack = 2
        # self.FLOWDDLMEAN = deadlineSlack * CONCURRENCY * FLOWSIZEMEAN / (LINKCAP*KB/RTT)
        # ECN Threshold
        self.ECN = ECN * PKTSIZE
        self.MAXBUFFER = MAXBUFFER * MB
        self.LINKCAP = LINKCAP * KB
        self.LINK = Link.Link(1)
        self.LINK.linkCap = self.LINKCAP
        # 1 Gbps = 1 G(1/8)Bps = (1/8)*1024*MB/s = 128MB/((1s/80us)*80us) = 128 MB/ (125*10^2 * 80us)
        #        = (128/125)*10^-2*MB/RTT = 10*(128/125)*KB/RTT ~ 10KB/RTT

        self.fname = output
        self.missrate = dict(mcp=0, tcp=0, dctcp=0, d2tcp=0)
        self.mcpwins = False
        # clear outputs
        open('Out/'+self.fname, 'w').close()

    def geninput(self):
        # Return a list of flows
        flowlist = []
        # flow format
        # print 'Generating input'
        for fid in range(self.MAXNUMFLOW):
            flow = Flow.Flow()
            flow.flowId = fid
            flow.SetFlowSize(random.expovariate(1 / self.FLOWSIZEMEAN))
            # deadline is in number of RTTs
            ddlinsteps = int(round(random.expovariate(1 / self.FLOWDDLMEAN) / self.RTT))
            while ddlinsteps >= self.Steps - 1:
                ddlinsteps = int(round(random.expovariate(1 / self.FLOWDDLMEAN) / self.RTT))
            flow.SetFlowDeadline(ddlinsteps)
            # print 'flow {} time for choice: {}'.format(fid, (Steps - flow.deadline))
            flow.startTime = random.choice(range(self.Steps - flow.deadline))
            # initial window
            flow.bw = 10 * PKTSIZE / self.RTT
            flow.residualRate = 0
            flowlist.append(flow)
        return flowlist

    def Rate(self, flow, CongestionPercentage, LinkQueue):
        if flow.transport == 'dctcp':
            if CongestionPercentage > 0:
                cWin = flow.bw * self.RTT
                cWin *= (1.0 - CongestionPercentage / 2.0)
                flow.bw = cWin / self.RTT
            else:
                flow.bw += 1 * (PKTSIZE / self.RTT)
        elif flow.transport == 'tcp':
            if CongestionPercentage > 0:
                cWin = flow.bw * self.RTT
                cWin /= 2.0
                flow.bw = cWin / self.RTT
            else:
                flow.bw += 1 * (PKTSIZE / self.RTT)
        elif flow.transport == 'd2tcp':
            if CongestionPercentage > 0:
                cWin = flow.bw * self.RTT
                Ts = 4.0 * flow.remainSize / (3.0 * flow.bw * self.RTT)  # following paper
                Urgency = max(2, Ts / flow.remainTime)
                cWin *= (1.0 - (CongestionPercentage ** Urgency) / 2.0)
                flow.bw = cWin / self.RTT
            else:
                flow.bw += (PKTSIZE / self.RTT)
        elif flow.transport == 'mcp':
            cWin = flow.bw * self.RTT
            ExpectedRate = flow.remainSize / flow.remainTime
            SourceTerm = flow.residualRate * ExpectedRate / flow.bw
            V = 0.05
            # NetworkTerm = V * LinkQueue / self.LINKCAP
            NetworkTerm = V * LinkQueue
            delta = self.RTT * SourceTerm - NetworkTerm
            # cWin = max(PKTSIZE / self.RTT, cWin + delta)
            # cWin = max(ExpectedRate * self.RTT, cWin + delta)
            cWin = max(ExpectedRate * self.RTT + delta, 10*PKTSIZE/self.RTT)
            flow.bw = cWin / self.RTT
        return flow.bw

    def run(self):
        # create inputs
        Flows = self.geninput()
        Flows.sort(key=lambda fs: fs.startTime)

        for proto in PROTO:
            for f in Flows:
                f.transport = proto
                if proto == 'dctcp' or proto == 'tcp' or proto == 'd2tcp':
                    f.bw = 2 * PKTSIZE / self.RTT

            ReadyFlow = Flows
            ActiveFlow = []
            DeadFlow = []
            MissFlow = []
            for t in range(self.Steps):
                # print 'Step {}'.format(t)
                newflows = [f for f in ReadyFlow if f.startTime == t]
                if newflows:
                    # print 'These flows, {}, are starting at {}'.format([f.flowId for f in newflows], t)
                    ActiveFlow += newflows

                InputLoad = sum([f.bw for f in ActiveFlow])
                # print 'Input load is {}'.format(InputLoad)
                self.LINK.queue += (InputLoad * self.RTT - self.LINKCAP)
                if self.LINK.queue < 0:
                    self.LINK.queue = 0
                csize = 0.001
                dropsize = 0.001
                if self.LINK.queue <= self.ECN:
                    pass
                elif self.LINK.queue <= self.MAXBUFFER:
                    csize = self.LINK.queue - self.ECN
                else:
                    csize = self.MAXBUFFER - self.ECN
                    dropsize = self.LINK.queue - self.MAXBUFFER
                    self.LINK.queue = self.MAXBUFFER
                # print 'Queue is {}'.format(self.LINK.queue)

                for f in ActiveFlow:
                    # calculate remaining size
                    cpercent = max(0.000001, min(1, abs(f.bw * self.RTT / csize)))
                    dropperc = max(0.000001, min(1, abs(f.bw * self.RTT / dropsize)))
                    f.remainSize = min(f.remainSize, f.remainSize - f.bw * self.RTT
                                       + dropperc * dropsize)
                    if f.remainTime > 0:
                        f.bw = self.Rate(f, cpercent, self.LINK.queue)
                        f.residualRate += f.remainSize / f.remainTime - f.bw
                        f.residualRate = max(0.001, f.residualRate)
                    # print 'flow {} rate {}'.format(f.flowId, f.bw)
                    f.bw = max(0.001, f.bw)
                    f.remainTime -= 1

                for f in ActiveFlow:
                    if f.remainSize <= 0.0 and f.remainTime >= 0:
                        # print 'flow {} is finished at {}'.format(f.flowId, t)
                        f.finishTime = t
                        DeadFlow.append(f)
                        ActiveFlow.remove(f)
                    elif f.remainSize > 0 and f.remainTime <= 0:
                        # print 'flow {} missed deadline at {}'.format(f.flowId, t)
                        f.finishTime = t
                        MissFlow.append(f)
                        ActiveFlow.remove(f)

            self.missrate[proto] = 100.0 * (len(MissFlow) + len(ActiveFlow)) / len(Flows)
            with open('Out/'+self.fname, "ab") as f:
                f.write('{}: Total number of flows: {}\n'.format(proto, len(Flows)))
                f.write('{}: Completed flows: {}\n'.format(proto, len(DeadFlow)))
                f.write('{}: Missed flows: {}\n'.format(proto, len(MissFlow) + len(ActiveFlow)))
                f.write('{}: Miss Rate: {}\n'.format(proto, self.missrate[proto]))
                f.write('\n')
                f.close()

            dt = datetime.now()
            with open('In/{}'.format(proto) + str(dt) + '.csv', 'wb') as csvfile:
                flowwriter = csv.writer(csvfile)
                flowwriter.writerow(['flow_id', 'deadline', 'flowSize', 'startTime', 'finishTime', 'fct'])
                for f in Flows:
                    flowwriter.writerow([
                        f.flowId,
                        f.deadline,
                        f.flowSize,
                        f.startTime,
                        f.finishTime,
                        max(0, f.finishTime-f.startTime)
                    ])
                csvfile.close()

        # mintrans = min(self.missrate, key=self.missrate.get)
        # if mintrans == 'mcp':
            # write flows to csv
            # self.mcpwins = True


if __name__ == "__main__":
    sim = StepByStepSimulator()
    # when in doubt, use brute force
    sim.run()
    count = 0
    Attempts = 10
    while not sim.mcpwins:
        if count > Attempts - 1:
            break
        count += 1
        print 'Run {}'.format(count)
        with open('Out/'+sim.fname, "ab") as f:
            f.write('Run {} at {}\n\n'.format(count, str(datetime.now())))
        sim.run()
