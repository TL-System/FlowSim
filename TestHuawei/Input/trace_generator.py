import sys
sys.path.append("../..")

import csv
import math
from random import choice
from Topology.SpineLeaf import *
import getopt

#the size of flows to be generate (in KB)
f_sizes= [1, 2, 3, 7, 267, 2107, 6667, 666667]

# the percentage of flows of different sizes under longtailed distribution
longtailed_percent = {"1":0.4, "2":0.12, "3":0.11, "7":0.1, "267":0.1, "2107":0.06, "6667":0.06, "666667":0.05}

# the percentage of flows of different sizes under uniform distribution
uniform_percent = {"1":0.12, "2":0.13, "3":0.12, "7":0.13, "267":0.12, "2107":0.13, "6667":0.12, "666667":0.13}
opts, args = getopt.getopt(sys.argv[1:], "n:t:", ["number=", "type="])

flow_num =1000
trace_flag = 0
for o, a in opts:
    if o in ("-n", "--number"):
        # input total flow number 
        flow_num = int(a)
    elif o in ("-t", "--type"):
        # input trace type
        trace_type = a
        if trace_type == "longtailed":
            trace_flag = 0
        elif trace_type == "uniform":
            trace_flag = 1

#initialize flow infomation
f_info = [0.0]*7
#initialize current time
current_time = 0.0

# enumerate flow sizes
for fsize in f_sizes:
    # get the number of flows of fsize
    if trace_flag == 0:
       fnum_of_fsize = int(flow_num*longtailed_percent[str(fsize)])
    elif trace_flag == 1:
       fnum_of_fsize = int(flow_num*uniform_percent[str(fsize)])
    for i in range(fnum_of_fsize):
        # compute sender and receiver servers
        f_info[0] = choice(range(SERVER*TOR))
        f_info[2] = choice(range(SERVER*TOR))
        if f_info[0]/SERVER == f_info[2]/SERVER:
            f_info[0] = (f_info[0]+SERVER)%(SERVER*TOR)
        f_info[0] = str(f_info[0])
        f_info[2] = str(f_info[2])
    #compute arrival time of current flow, arrival_time_delta is the arrival interval of the current flow
        arrival_time_delta = choice(range(10,40))/1000000.0
        current_time += arrival_time_delta
        f_info[4] = current_time
        f_info[4] = str(f_info[4])
        #compute coflow ID, now on average let one coflow have 100 flows
        f_info[5] = choice(range(flow_num/100))
        f_info[5] = str(f_info[5])
        #compute flow size. Note that here we add some variation to the flow size
        fsize_delta_factor = choice(range(100))/100.0
        #fsize_delta_factor = 0.0
        f_info[6] = fsize*8*1024*(1.0+fsize_delta_factor)
        f_info[6] = str(f_info[6])
        # print flow infomation
        line_toprint = ','.join(map(str, f_info))
        print line_toprint.rstrip('\r\n')

