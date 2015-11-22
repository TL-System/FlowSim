import sys
sys.path.append("../..")

import csv
import math
from random import choice
import getopt

#the size of flows to be generate (in KB)
f_sizes= [1, 2, 3, 7, 267, 2107, 6667, 666667]

# the percentage of flows of different sizes under longtailed distribution
longtailed_percent = {"1":0.4, "2":0.12, "3":0.11, "7":0.1, "267":0.1, "2107":0.06, "6667":0.06, "666667":0.05}

# the percentage of flows of different sizes under uniform distribution
uniform_percent = {"1":0.12, "2":0.13, "3":0.12, "7":0.13, "267":0.12, "2107":0.13, "6667":0.12, "666667":0.13}
opts, args = getopt.getopt(sys.argv[1:], "n:i:server:tor:t:p:", ["number=", "input=", "server=", "tor=", "t=", "pattern="])

flow_num = 1000
trace_flag = 0
c_pattern = "random"
SERVER = 10
TOR = 10

for o, a in opts:
    if o in ("-n", "--number"):
        # input total flow number 
        flow_num = int(a)
    if o in ("-t", "--t"):
        # input trace type
        trace_type = a
        if trace_type == "longtailed":
            trace_flag = 0
        elif trace_type == "uniform":
            trace_flag = 1
    if o in ("-server", "--server"):
        # input number of servers
        SERVER = int(a)
    if o in ("-tor", "--tor"):
        # input number of ToR switches
        TOR = int(a)
    if o in ("-p", "--pattern"):
        # input communication pattern
        c_pattern = a

#assign hop value of stride pattern
stride_hop = TOR/4
#assgin probability value of staggered pattern
staggered_prob = 0.1
#generate a permutation circuit chain
p_chain_list = [0]*TOR
p_hash_table = [0]*TOR
sender = 0
for i in range(TOR):
    #receriver = choice(range(TOR))
    #while p_hash_table[recierve] == 1 or sender == receiver:
    #    receiver = (receiver+1)%TOR
    p_chain_list[i] = (i+1)%TOR
    #p_hash_table[receiver] = 1
    #sender = receiver
#initialize flow infomation
f_info = [0.0]*7
#initialize current time
current_time = 0.0

def get_sender_and_receiver():
    if c_pattern == 'random':
        sToR = choice(range(TOR))
        rToR = choice(range(TOR))
        if sToR == rToR:
            rToR = (rToR + 1)% TOR
        sender = choice(range(SERVER))+ sToR*SERVER
        receiver = choice(range(SERVER)) + rToR*SERVER
        return [sender, receiver]
    if c_pattern == 'stride':
        global stride_hop
        sToR = choice(range(TOR))
        rToR = ( sToR + stride_hop ) % TOR
        if sToR == rToR:
           rToR = (rToR + 1)% TOR
        sender = choice(range(SERVER))+ sToR*SERVER
        receiver = choice(range(SERVER)) + rToR*SERVER
        return [sender, receiver]
    if c_pattern == 'staggered':
        global staggered_prob
        sToR = choice(range(TOR))
        prob_hit = 1
        if choice(range(1000)) > 1000*staggered_prob:
            prob_hit = 0
        if prob_hit == 1:
            rToR = sToR
            s1 = choice(range(SERVER))
            s2 = choice(range(SERVER))
            if s1 == s2:
                s2 = (s2+1)%SERVER
            sender = s1 + sToR*SERVER
            receiver = s2 + rToR*SERVER
        else:
            rToR = choice(range(TOR))
            if sToR == rToR:
                rToR = (rToR + 1)% TOR
            sender = choice(range(SERVER))+ sToR*SERVER
            receiver = choice(range(SERVER)) + rToR*SERVER
        return [sender, receiver]
    if c_pattern == 'permutation':
        global p_chain_list
        sToR = choice(range(TOR))
        rToR = p_chain_list[sToR]
        sender = choice(range(SERVER))+ sToR*SERVER
        receiver = choice(range(SERVER)) + rToR*SERVER
        return [sender, receiver]


# enumerate flow sizes
for fsize in f_sizes:
    # get the number of flows of fsize
    if trace_flag == 0:
       fnum_of_fsize = int(flow_num*longtailed_percent[str(fsize)])
    elif trace_flag == 1:
       fnum_of_fsize = int(flow_num*uniform_percent[str(fsize)])
    for i in range(fnum_of_fsize):
        # compute sender and receiver servers
        #f_info[0] = choice(range(SERVER*TOR))
        #f_info[2] = choice(range(SERVER*TOR))
        #if f_info[0]/SERVER == f_info[2]/SERVER:
            #f_info[0] = (f_info[0]+SERVER)%(SERVER*TOR)
        [ f_info[0], f_info[2] ] = get_sender_and_receiver()
        f_info[0] = str(f_info[0])
        f_info[2] = str(f_info[2])

    #compute arrival time of current flow, arrival_time_delta is the arrival interval of the current flow
        arrival_time_delta = choice(range(1,5))/10000000.0
        current_time += arrival_time_delta
        f_info[4] = current_time
        f_info[4] = str(f_info[4])
        #compute coflow ID, now on average let one coflow have 100 flows
        f_info[5] = choice(range(max(1,flow_num/100)))
        f_info[5] = str(f_info[5])
        #compute flow size. Note that here we add some variation to the flow size
        fsize_delta_factor = choice(range(100))/100.0
        fsize_delta_factor = 0.0
        f_info[6] = fsize*8*1024*(1.0+fsize_delta_factor)
        f_info[6] = str(f_info[6])
        # print flow infomation
        line_toprint = ','.join(map(str, f_info))
        print line_toprint.rstrip('\r\n')

