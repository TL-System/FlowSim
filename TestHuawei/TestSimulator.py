# sys.path.append("..")

import getopt
import time

from TestFlowScheduler import *

# from Topology.SpineLeaf import *
from Routing.ECMP_SpineLeaf import *
from Routing.LB_SpineLeaf import *
from Routing.FlowLB_SpineLeaf import *
from Routing.Qlearning_SpineLeaf import *
from Src.Simulator import *

# TODO: add in topology description for spine leaf
# Flow size is in MB
flowSize = 100.0
# The mean of poisson arrival rate
mean = 10
# The average number of flows generated of each server node
avgFlowNum = 1
# alpha for power-law
alpha = 1.0

routing_dict = {'LB': LB, 'ECMP': ECMP, 'Qlearning': Qlearning, 'FlowLB': FlowLB}
routing_scheme = FlowLB
trace_FName = "Input/trace.csv"
server = 10
core = 10
tor = 10
number_hidden_nodes_per_layer = [100, 50]
exploration_type = 0
eps = 0.10
reward_type = -1
features = []
setting = ""
max_episodes = 0

opts, args = getopt.getopt(sys.argv[1:], "S:L:a:f:routing:i:server:tor:core:nn:expl:eps:reward:features:setting:max",
                           ["S=", "L=", "a=", "f=", "routing=", "input=", "server=", "tor=", "core=", "nn=", "expl=",
                            "eps=", "reward=", "features=", "setting=", "max="])
for o, a in opts:
    if o in ("-S", "--S"):
        flowSize = float(a)
    elif o in ("-L", "--L"):
        mean = int(a)
    elif o in ("-a", "--a"):
        avgFlowNum = int(a)
    elif o in ("-f", "--f"):
        alpha = float(a)
    elif o in ("-routing", "--routing"):
        routing_scheme = routing_dict[a]
    elif o in ("-i", "--input"):
        # print "a = ",a
        trace_FName = "Input/" + a
    elif o in ("-server", "--server"):
        server = int(a)
    elif o in ("-tor", "--tor"):
        tor = int(a)
    elif o in ("-core", "--core"):
        core = int(a)
    elif o in ("-nn", "--nn"):
        number_hidden_nodes_per_layer = [int(x) for x in a.split(',')]
    elif o in ("-expl", "--expl"):
        exploration_type = int(a)
    elif o in ("-eps", "--eps"):
        epsilon = float(a)
    elif o in ("-reward", "--reward"):
        reward_type = int(a)
    elif o in ("-features", "--features"):
        features = [int(x) for x in a.split(',')]
    elif o in ("-setting", "--setting"):
        setting = str(a)
    elif o in ("-max", "--max"):
        max_episodes = int(a)


def main():
    # print routing_scheme
    sim = Simulator()
    testTopo = SpineLeaf(server, tor, core)
    testTopo.CreateTopology()
    sim.AssignTopology(topo=testTopo, cap=1.0 * Gb)
    sim.AssignRoutingEngine(max_episodes, reward_type, features, number_hidden_nodes_per_layer, exploration_type,
                            epsilon, setting, Routing=routing_scheme)
    # sim.AssignScheduler(FlowScheduler=TestFlowScheduler, args="Input/trace.csv")
    sim.setTraceFName(TraceFName=trace_FName)
    # print trace_FName
    sim.setSchedType(FlowScheduler=TestFlowScheduler)
    start_time = time.time()
    sim.Run()
    # print time.time() - start_time


if __name__ == "__main__":
    main()
