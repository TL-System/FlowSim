__author__ = 'li'

from StepByStepSimulator import *

sim = StepByStepSimulator(rtt=0.000001 * 80,  # 80us
                          simtime=1,  # 1s = 1000ms
                          concurrency=5,
                          flowsizemean=0.1,  # 0.1MB = 100KB 0.1MB/100ms=100KB/100ms=8000bps=8Gbps
                          flowddlmean=0.001 * 50,  # 50ms
                          ecn=64,  # 64 packets
                          maxbuffer=12,  # 12MB
                          linkcap=10,  # 1Gbps
                          output='results.txt')

if __name__ == "__main__":
    for rtt in [80, 100, 120, 160]:
        cclist = [1, 2, 3, 4, 5, 8, 10]
        cclist.reverse()
        for concur in cclist:
            for size in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
                for ddl in [20, 30, 40, 50, 60, 70, 80, 90, 100]:
                    for cap in [10, 100, 400]:
                        sim = StepByStepSimulator(rtt=0.000001 * rtt,
                                                  simtime=0.8,
                                                  concurrency=concur,
                                                  flowsizemean=size,
                                                  flowddlmean=0.001 * ddl,
                                                  ecn=64,
                                                  maxbuffer=12,
                                                  linkcap=cap,
                                                  output='Out/rtt{}concur{}size{}ddl{}cap{}.txt'.format(rtt,
                                                                                                        concur,
                                                                                                        size,
                                                                                                        ddl,
                                                                                                        cap))
                        sim.run()
