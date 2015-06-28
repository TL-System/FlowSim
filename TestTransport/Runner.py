__author__ = 'li'

import StepByStepSimulator

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
LINKCAP = 10 * KB

StepByStepSimulator.
