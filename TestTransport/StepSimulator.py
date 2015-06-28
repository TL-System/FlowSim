__author__ = 'li'

import random

from Src import Flow, Link
from Distribution import WeightedChoice
import sys

KB = 1.0
MB = 1024.0 * KB

# looking for examples supporting MCP
# run simulator step by step, running for 100 milliseconds
# simulating multiple flows over one link
RTT = 0.000001 * 80 # 80 us
SIMTIME = 0.1
Steps = int(round(SIMTIME / RTT))
MAXNUMFLOW = 10 * Steps # This is concurrency of flows
FLOWSIZEMEAN = 0.5 * MB
PKTSIZE = 1.5 * KB
FLOWDDLMEAN = 0.001 * 50
PROTO = ['d2tcp', 'mcp', 'tcp', 'dctcp']
# PROTO = ['d2tcp']
# ECN Threshold
ECN = 64 * PKTSIZE
MAXBUFFER = 12 * MB

LINK = Link.Link(1)
LINK.linkCap = 10 * KB  # 1Gbps link

def geninput():
    # Return a list of flows
    flowlist=[]
    # flow format
    print 'Generating input'
    for fid in range(MAXNUMFLOW):
        flow = Flow.Flow()
        flow.flowId = fid
        flow.SetFlowSize(random.expovariate(1/FLOWSIZEMEAN))
        # deadline is in number of RTTs
        ddlinsteps = int(round(random.expovariate(1/FLOWDDLMEAN) / RTT))
        while ddlinsteps >= Steps - 1:
            ddlinsteps = int(round(random.expovariate(1/FLOWDDLMEAN) / RTT))
        flow.SetFlowDeadline(ddlinsteps)
        # print 'flow {} time for choice: {}'.format(fid, (Steps - flow.deadline))
        flow.startTime = random.choice(range(Steps - flow.deadline))
        # choicerange = range(Steps - flow.deadline)
        # weights = [abs(c-Steps+1) for c in choicerange]
        # choices = dict(zip(choicerange,weights))
        # flow.startTime = WeightedChoice.weighted_choice(choices)

        # initial window
        flow.bw = 10*PKTSIZE/RTT
        flow.residualRate = 0
        flowlist.append(flow)
    return flowlist

def Rate(flow, CongestionPercentage, LinkQueue):
    if flow.transport == 'dctcp':
        if CongestionPercentage > 0.002:
            cWin = flow.bw * RTT
            cWin = cWin*(1 - CongestionPercentage/2.0)
            flow.bw = cWin/RTT
        else:
            flow.bw += 0.1*(PKTSIZE/RTT)
    elif flow.transport == 'tcp':
        if CongestionPercentage > 0.002:
            cWin = flow.bw * RTT
            cWin /= 2.0
            flow.bw = cWin/RTT
        else:
            flow.bw += 0.1*(PKTSIZE/RTT)
    elif flow.transport == 'd2tcp':
        if CongestionPercentage > 0.002:
            cWin = flow.bw * RTT
            Urgency = max(0, min(5.0, flow.remainSize/flow.remainTime))
            try:
                cWin = cWin*(1 - (CongestionPercentage**Urgency)/2.0)
            except:
                print 'alpha = {}, urgency = {}'.format(CongestionPercentage, Urgency)
                sys.exit("aa! errors!")
            flow.bw = cWin/RTT
        else:
            flow.bw += (PKTSIZE/RTT)
    elif flow.transport == 'mcp':
        cWin = flow.bw * RTT
        ExpectedRate = flow.remainSize/flow.remainTime
        SourceTerm = flow.residualRate * ExpectedRate / flow.bw
        V = 1
        NetworkTerm = V * LinkQueue / LINK.linkCap
        delta = RTT * (SourceTerm - NetworkTerm)
        cWin += delta
        flow.bw = cWin/RTT
    return flow.bw

# create inputs
Flows = geninput()

fname = 'results.txt'
open(fname, 'w').close()

for proto in PROTO:
    for f in Flows:
        f.transport = proto
        if proto == 'dctcp' or proto == 'tcp':
            f.bw = PKTSIZE/RTT

    Flows.sort(key=lambda f: f.startTime)
    ReadyFlow = Flows
    print len(ReadyFlow)
    ActiveFlow = []
    DeadFlow = []
    MissFlow = []
    for t in range(Steps):
        print 'Step {}'.format(t)
        newflows = [f for f in ReadyFlow if f.startTime == t]
        if newflows:
            # print 'These flows, {}, are starting at {}'.format([f.flowId for f in newflows], t)
            # ActiveFlow = itertools.chain(ActiveFlow, newflows)
            ActiveFlow += newflows
        # else:
            # print 'No flow is starting at {}'.format(t)

        InputLoad = sum([f.bw for f in ActiveFlow])
        print 'Input load is {}'.format(InputLoad)
        LINK.queue += (InputLoad * RTT - LINK.linkCap)
        csize = 0.001
        dropsize = 0.001
        if (LINK.queue - ECN) < 0:
            LINK.queue = 0.001
        else:
            # LINK.queue = min(12 * MB, LINK.queue)
            csize = max(0.001, LINK.queue - ECN)
            dropsize = max(0.001, LINK.queue - MAXBUFFER)
            LINK.queue = min(MAXBUFFER, LINK.queue)
        print 'Queue is {}'.format(LINK.queue)

        for f in ActiveFlow:
            cpercent = max(0.001, min(1, f.bw*RTT/csize))
            if f.remainTime > 0:
                f.bw = Rate(f, cpercent, LINK.queue)
                f.residualRate += f.remainSize/f.remainTime - f.bw
                f.residualRate = max(0.001, f.residualRate)
            # print 'flow {} rate {}'.format(f.flowId, f.bw)
            f.bw = max(0.001, f.bw)
            droprate = 1
            f.remainSize = min(f.remainSize, f.remainSize - f.bw * RTT + droprate * cpercent * dropsize)
            f.remainTime -= 1

        for f in ActiveFlow:
            if f.remainSize <= 0.0 and f.remainTime >= 0:
                print 'flow {} is finished at {}'.format(f.flowId, t)
                f.finishTime = t
                DeadFlow.append(f)
                ActiveFlow.remove(f)
            elif f.remainSize > 0 and f.remainTime <= 0:
                print 'flow {} missed deadline at {}'.format(f.flowId, t)
                f.finishTime = t
                MissFlow.append(f)
                ActiveFlow.remove(f)

    with open(fname, "a") as f:
        f.write('{}: Total number of flows: {}\n'.format(proto, len(Flows)))
        f.write('{}: Completed flows: {}\n'.format(proto, len(DeadFlow)))
        f.write('{}: Missed flows: {}\n'.format(proto, len(MissFlow)))
        f.write('{}: Miss Rate: {}\n'.format(proto, 1.0*len(MissFlow)/len(Flows)))
        f.write('\n')
    f.close()