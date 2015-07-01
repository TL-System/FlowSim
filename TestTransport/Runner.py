__author__ = 'li'

from StepByStepSimulator import *

sim = StepByStepSimulator(RTT=0.000001 * 80,  # 80us
                          SIMTIME=1,  # 1s = 1000ms
                          CONCURRENCY=5,
                          FLOWSIZEMEAN=0.1,  # 0.1MB = 100KB 0.1MB/100ms=100KB/100ms=8000bps=8Gbps
                          FLOWDDLMEAN=0.001 * 50,  # 50ms
                          ECN=64,  # 64 packets
                          MAXBUFFER=12,  # 12MB
                          LINKCAP=10,  # 1Gbps
                          output='results.txt')

if __name__ == "__main__":
    for rtt in [80, 100, 120, 160]:
        for concur in [1, 2, 3, 4, 5, 8, 10]:
            for size in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
                for ddl in [20, 30, 40, 50, 60, 70, 80, 90, 100]:
                    for cap in [10, 100, 400]:
                        sim = StepByStepSimulator(RTT=0.000001 * rtt,
                                                  SIMTIME=0.8,
                                                  CONCURRENCY=concur,
                                                  FLOWSIZEMEAN=size,
                                                  FLOWDDLMEAN=0.001 * ddl,
                                                  ECN=64,
                                                  MAXBUFFER=12,
                                                  LINKCAP=cap,
                                                  output='rtt{}concur{}size{}ddl{}cap{}.txt'.format(rtt,
                                                                                                    concur,
                                                                                                    size,
                                                                                                    ddl,
                                                                                                    cap))
                        sim.run()
