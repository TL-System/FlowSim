__author__ = 'li'

import random
import csv
import json
import copy

from Src import Flow, Link
from TUnits import *


# looking for examples supporting MCP
# run simulator step by step, running for 100 milliseconds
# simulating multiple flows over one link
PROTO = ['tcp', 'mcp', 'd2tcp', 'dctcp', 'd3', 'mock']


# PROTO = ['d2tcp']

class StepByStepSimulator:
    # setting up environment
    def __init__(self,
                 rtt=0.000001 * 80,  # 80us
                 simtime=0.1,  # 0.1s = 100ms, 0.05s=50ms
                 concurrency=5,
                 flowsizemean=0.01,  # 0.1MB = 100KB 0.1MB/100ms=100KB/50ms=0.0016Gbps
                 # 0.01MB = 10KB =1.6Gbps
                 flowddlmean=0.001 * 50,  # 50ms
                 ecn=64,  # 64 packets
                 maxbuffer=4,  # 4MB
                 linkcap=1000,  # BDP = 10KB -> 1Gbps
                 output='results.txt',
                 inputf=''):  # assuming txt file
        self.RTT = rtt
        self.SIMTIME = simtime
        self.Steps = int(round(simtime / rtt))
        self.MAXNUMFLOW = concurrency * self.Steps  # This is concurrency of flows
        self.FLOWSIZEMEAN = flowsizemean * MB
        self.FLOWDDLMEAN = flowddlmean
        # deadlineSlack = 2
        # self.FLOWDDLMEAN = deadlineSlack * CONCURRENCY * FLOWSIZEMEAN / (LINKCAP*KB/RTT)
        # ECN Threshold
        self.ECN = ecn * PKTSIZE
        self.MAXBUFFER = maxbuffer * MB
        self.LINKCAP = linkcap * KB
        self.LINK = Link.Link(1)
        self.LINK.linkCap = self.LINKCAP
        # 1 Gbps = 1 G(1/8)Bps = (1/8)*1024*MB/s = 128MB/((1s/80us)*80us) = 128 MB/ (125*10^2 * 80us)
        #        = (128/125)*10^-2*MB/RTT = 10*(128/125)*KB/RTT ~ 10KB/RTT

        self.fname = output
        self.missrate = dict(mcp=0, tcp=0, dctcp=0, d2tcp=0)
        self.mcpwins = False
        # clear outputs
        open('Out/' + self.fname, 'w').close()
        if inputf == '':
            self.hasInput = False
        else:
            self.hasInput = True
            self.inputf = inputf

        self.linkrates = {
            'mcp': [],
            'd2tcp': [],
            'dctcp': [],
            'tcp': [],
            'd3': [],
            'mock': []
        }

    def geninput(self):
        # Return a list of flows
        flowlist = []
        # print 'Generating input'
        if not self.hasInput:
            for fid in range(self.MAXNUMFLOW):
                flow = Flow.Flow()
                flow.flowId = fid
                flow.SetFlowSize(round(random.expovariate(1 / self.FLOWSIZEMEAN)))
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
        else:
            with open(self.inputf) as inputf:
                tempflows = json.load(inputf)
            for i in range(len(tempflows)):
                flow = Flow.Flow()
                flow.flowId = i
                flow.SetFlowSize(tempflows['{}'.format(i)]['flowSize'])
                flow.SetFlowDeadline(tempflows['{}'.format(i)]['deadline'])
                flow.startTime = tempflows['{}'.format(i)]['startTime']
                flow.bw = 10 * PKTSIZE / self.RTT
                flow.residualRate = 0
                flowlist.append(flow)

        return flowlist

    def rate(self, flow, CongestionPercentage, LinkQueue, AggRate):
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
                Ts = (4.0 * flow.remainSize / (3.0 * flow.bw * self.RTT))  # following paper
                Urgency = abs(Ts / flow.remainTime)
                cWin *= (1.0 - (CongestionPercentage ** Urgency) / 2.0)
                flow.bw = cWin / self.RTT
            else:
                flow.bw += (PKTSIZE / self.RTT)
                # print "after rate(), {}".format(flow.remainTime)
        elif flow.transport == 'mcp':
            cWin = flow.bw * self.RTT
            ExpectedRate = flow.remainSize / flow.remainTime
            SourceTerm = flow.residualRate * ExpectedRate / flow.bw
            V = 1
            NetworkTerm = V * LinkQueue / self.LINKCAP
            # print ''
            # print 'NetworkTerm={}'.format(NetworkTerm)
            # print 'ExpectedRate={}'.format(ExpectedRate)
            # print 'flow.residualRate={}'.format(flow.residualRate)
            # print 'flow.bw={}'.format(flow.bw)
            # print 'SourceTerm={}'.format(SourceTerm)
            # NetworkTerm = V * (LinkQueue / self.LINKCAP + AggRate)
            # delta = self.RTT * (SourceTerm - NetworkTerm)
            delta = (SourceTerm - NetworkTerm)
            # cWin = max(PKTSIZE / self.RTT, cWin + delta)
            # cWin = max(ExpectedRate * self.RTT, cWin + delta)
            # cWin = max(ExpectedRate * self.RTT + delta, 10 * PKTSIZE / self.RTT)
            flow.bw += delta
            # print 'flow.bw={}'.format(flow.bw)
        elif flow.transport == 'd3':
            flow.bw = flow.flowSize / flow.deadline
        elif flow.transport == 'mock':
            flow.bw = flow.remainSize / flow.remainTime
        else:
            print "Error: Transport protocol not recognized."
        return flow.bw

    def run(self):
        # create inputs
        Flows = self.geninput()
        Flows.sort(key=lambda fs: fs.startTime)

        for proto in PROTO:
            for f in Flows:
                f.transport = proto
                if proto == 'dctcp' or proto == 'tcp' or proto == 'd2tcp':
                    # if proto == 'mcp':
                    # f.bw = f.remainSize / f.remainTime
                    f.bw = 2 * PKTSIZE / self.RTT

            ReadyFlow = copy.deepcopy(Flows)
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
                self.linkrates[proto].append(InputLoad)
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
                        f.bw = self.rate(f, cpercent, self.LINK.queue, InputLoad)
                        f.residualRate += ((f.remainSize / f.remainTime) - f.bw)
                        f.residualRate = max(0.001, f.residualRate)
                    f.bw = max(0.001, f.bw)
                    f.remainTime -= 1
                    # for f in ActiveFlow:
                    if f.remainSize < 0.0:  # and f.remainTime >= 0:
                        print 'flow {} is finished at {}'.format(f.flowId, t)
                        f.finishTime = t
                        DeadFlow.append(f)
                        ActiveFlow.remove(f)
                    elif f.remainTime <= 0:
                        print 'flow {} missed deadline at {}'.format(f.flowId, t)
                        f.finishTime = t  # unfinished
                        MissFlow.append(f)
                        ActiveFlow.remove(f)
                        # f.remainTime -= 1

            for af in ActiveFlow:
                af.finishTime = t
            MissFlow.sort(key=lambda f: f.flowId)
            ActiveFlow.sort(key=lambda f: f.flowId)
            self.missrate[proto] = 100.0 * (len(MissFlow) + len(ActiveFlow)) / len(Flows)
            with open('Out/' + self.fname, "ab") as f:
                f.write('{}: Total number of flows: {}\n'.format(proto, len(Flows)))
                f.write('{}: Completed flows: {}\n'.format(proto, len(DeadFlow)))
                f.write('{}: Missed flows: {}\n'.format(proto, len(MissFlow) + len(ActiveFlow)))
                f.write('{}: Miss Rate: {}\n'.format(proto, self.missrate[proto]))
                f.write('Missed Flows: ')
                for mf in MissFlow:
                    f.write('{} '.format(mf.flowId))
                f.write('\n')
                f.write('Unfinished Flows: ')
                for df in ActiveFlow:
                    f.write('{} '.format(df.flowId))
                f.write('\n')
                f.write('\n')
                f.close()

            # dt = datetime.now()
            dt = ''
            allflow = MissFlow + ActiveFlow + DeadFlow
            with open('In/{}'.format(proto) + str(dt) + '.csv', 'wb') as csvfile:
                flowwriter = csv.writer(csvfile)
                flowwriter.writerow([proto + '_flow_id', proto + '_deadline', proto + '_flowSize',
                                     proto + '_startTime', proto + '_finishTime', proto + '_fct'])
                for f in allflow:
                    flowwriter.writerow([
                        f.flowId,
                        f.deadline,
                        f.flowSize,
                        f.startTime,
                        f.finishTime,
                        max(0, f.finishTime - f.startTime)
                    ])
                csvfile.close()

            with open('Out/{}'.format(proto) + '_rates.csv', 'wb') as csvfile:
                flowwriter = csv.writer(csvfile)
                flowwriter.writerow(self.linkrates[proto])
                csvfile.close()

        mintrans = min(self.missrate, key=self.missrate.get)
        if mintrans == 'mcp':
            #     write flows to csv
            self.mcpwins = True


if __name__ == "__main__":
    Rtt = 0.001
    sim = StepByStepSimulator(
        rtt=Rtt,
        simtime=Rtt * 10,
        concurrency=2,
        flowsizemean=0.002,
        flowddlmean=1 * Rtt,
        linkcap=1000,
        inputf='Out/flow10.json')
    # when in doubt, use brute force
    sim.run()
    # count = 0
    # Attempts = 0
    # while not sim.mcpwins:
    #     if count > Attempts - 1:
    #         break
    #     count += 1
    #     print 'Run {}'.format(count)
    #     with open('Out/'+sim.fname, "ab") as f:
    #         f.write('Run {} at {}\n\n'.format(count, str(datetime.now())))
    #     sim.run()
