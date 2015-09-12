__author__ = 'lich'

from Unit import *
#from Src.Flow import *
#import sys
#sys.path.append("..")
# Flow-level simulator written in python.
# This file describes the design of class Simulator.
# from Topology.SpineLeaf import *
#print sys.path
#from Routing.ECMP_SpineLeaf import *
#from Routing.LB_SpineLeaf import *  
#from Routing.Qlearning_SpineLeaf import *
class Simulator:
    def __init__(self):
        pass

    def AssignTopology(self, topo, cap=1.0 * Gb):
        """
        Network simulator must have an input graph as the topology
        """
        self.topo = topo
        self.topo.SetAllCapacity(cap)
        # We can get and set topo info:
        # node_2 = self.topo.nodes[2]                       #2 is node id
        # link_3_2 = self.topo.link[3,2]                    #(3,2) is link id
        # self.topo.SetLinkCapacity((5, 7), 10.0 * Gb)      #set link_5_7 with capacity 10Gbps

    def AssignRoutingEngine(self, Routing):
        """
        Assign the routing method in a centralized way.
        Routing is a function that takes topo as input
        """
        self.routing = Routing(self.topo)
        self.Qlearning_enable = 0
        if str(Routing) == "Routing.Qlearning_SpineLeaf.Qlearning":
            self.Qlearning_enable = 1
            print "linkNum between Switches: ", self.topo.GetLinkNumbetweenSwitch()
            self.LinkUtilization = [0.0]*self.topo.GetLinkNumbetweenSwitch()
            self.ActiveFlowNum = [0]*self.topo.GetLinkNumbetweenSwitch()
            self.ActiveElephantFlowNum = [0]*self.topo.GetLinkNumbetweenSwitch()
            self.ActiveFlowRemainSize = [0.0]*self.topo.GetLinkNumbetweenSwitch()
            self.state = self.LinkUtilization
            #print len(self.topo.GetLinks())
            self.reward = [0.0, 0.0]
            self.stateId = 0
            self.logDir = "LogInfo/"
            #self.logfname = "StateLog.csv"
            #self.logf = open(self.logDir + self.logfname, "w")
        #self.updatenum=0

        # We can get path by
        # path_3_5 = self.routing.GetPath(3,5)             # result is a list with node ids

    def AssignScheduler(self, FlowScheduler, args):
        """
        Assign the flow scheduler. It also assign the flows to be scheduled.
        """
        self.schedType = FlowScheduler
        self.sched = FlowScheduler()
        self.sched.AssignFlows(args)
        self.sched.AssignLinks(self.topo.GetLinks())
        self.sched.AssignNodes(self.topo.GetNodes())
        self.flows = self.sched.GetAllFlows()
        self.norm_trans_time = [0.0]*len(self.flows)
       # for flow in self.flows:
       #     self.routing.BuildPath(flow.startId, flow.endId)
       #     pathNodeIds = self.routing.GetPath(flow.startId, flow.endId)
       #     flow.BuildPath(pathNodeIds)

    def AssignLoadBalancer(self, LoadBalancer, args):
        self.lb = LoadBalancer()

    def Update(self, flow):

        #update state list by dimension
        dim_id = 0
        for key in self.sched.Links.keys():
            if key[0] >= self.topo.numOfServers and key[1] >= self.topo.numOfServers:
             #  print key
             #  print "dim_id= ", dim_id
               self.LinkUtilization[dim_id] = self.sched.Links[key].GetLinkUtilization()
               self.ActiveFlowNum[dim_id] = self.sched.Links[key].GetActiveFlowNum()
               self.ActiveElephantFlowNum[dim_id] = self.sched.Links[key].GetActiveElephantFlowNum(self.flows)
               self.ActiveFlowRemainSize[dim_id] = self.sched.Links[key].GetActiveFlowRemainSize(self.flows)
               dim_id += 1
        #print "dim_id= ", dim_id
        
        # reward of type 1
        #r1 = - 1.0 / (flow.bw/(1024.0*1024.0)*len(flow.pathLinkIds))
        r1 = - 1.0 / (flow.bw/(1024.0*1024.0)) * 2
        # reward of type 2
        r2 = 0.0
        for linkId in flow.pathLinkIds:
            link = self.sched.Links[linkId]
            if link.GetLinkUtilization() > r2:
                r2 = link.GetLinkUtilization()
            #print link.GetLinkUtilization()
        r2 = -r2
        self.reward = [r1, r2]

    def Run(self):
        """
        Fire up the simulator. The function calculates the transferring time for each flow.
        """
       # print "len of tostartFlows ", len(self.sched.toStartFlows)
        # start all the flows along with updating related flow transfer time
        max_episodes = 1
        for episode in range(max_episodes):
            self.AssignScheduler(FlowScheduler=self.schedType, args="Input/trace.csv")
            self.logfname = "StateLog" + str(episode) + ".csv"
            self.logf = open(self.logDir + self.logfname, "w")
            counter = 0
            while self.sched.toStartFlows:
                # print counter
                counter += 1
                # the first flow is with earliest startTime
                curStartFlow = self.sched.toStartFlows[0]
                # update flows if there are flows has already finished
                while self.sched.runningFlows:
                    # the first flow is with earliest finishTime
                    toFinishFlow = self.sched.runningFlows[0]
                    if toFinishFlow.finishTime <= curStartFlow.startTime:
                        # remove this flow from running flows
                        self.sched.runningFlows.remove(toFinishFlow)
                        # add this flow to finished flows
                        self.sched.finishedFlows.append(toFinishFlow)
                        # Update related flow's transfer time in removing a flow
                        self.sched.UpdateFlow(toFinishFlow, "remove")
                        # Resort runningFlows by endTime
                        self.sched.runningFlows.sort(key=lambda x: x.finishTime)

                        if self.Qlearning_enable == 1:
                            self.action = toFinishFlow.pathNodeIds
                            if len(self.action) == 5:
                               self.pre_LinkUtilization = self.LinkUtilization[:]
                               self.pre_ActiveFlowNum = self.ActiveFlowNum[:]
                               self.pre_ActiveElephantFlowNum = self.ActiveElephantFlowNum[:]
                               self.pre_ActiveFlowRemainSize = self.ActiveFlowRemainSize[:]
                               # self.pre_state = self.state[:]
                               self.Update(toFinishFlow)
                               #self.printQlearningLog()
                        #self.routing.update(self.pre_state, self.action, self.state, self.reward)
                        #self.Update(self.pre_state, self.action, self.state, self.reward)

                    else:
                        break
                # insert current start flow to running list
                if self.Qlearning_enable == 1:
                    self.routing.BuildPath(curStartFlow.startId, curStartFlow.endId, curStartFlow, self.state)
                else:
                    self.routing.BuildPath(curStartFlow.startId, curStartFlow.endId, curStartFlow)
                pathNodeIds = self.routing.GetPath(curStartFlow.startId, curStartFlow.endId)
                curStartFlow.BuildPath(pathNodeIds)
                self.sched.runningFlows.append(curStartFlow)
                # Update related flow's transfer time in removing a flow
                # self.lb(curStartFlow)
                # self.topo.GetLinkOfLeastFlow()
                # Step 1 find out which spine is less loaded

                # Hedera load balancing for spine leaf
                # print self.topo.GetCoreLeastFlow()
          #      if self.topo.name == "spineleaf":
          #          if self.topo.GetCoreLeastFlow() not in curStartFlow.pathNodeIds:
          #              if len(curStartFlow.pathNodeIds) == 5:
          #                  if curStartFlow.coflowId == 0:
          #                      self.changeSpine(curStartFlow, self.topo.GetCoreLeastFlow())
          #                      # print "general flow reroute to spine {}".format(self.topo.GetCoreLeastFlow().nodeId)
          #                  else:
          #                      self.changeSpine(curStartFlow,
          #                                       self.topo.GetCoreNode((curStartFlow.coflowId % self.topo.numOfCores)+1))
                                # print "coflow reroute to spine {}".format(self.topo.GetCoreNode((curStartFlow.coflowId % self.topo.numOfCores)+1).nodeId)
                            #print curStartFlow.pathNodeIds
                    # Less loaded in terms of more flows

                # update state and reward for Qlearning algorithm
                self.sched.UpdateFlow(curStartFlow, "insert")
                #self.updatenum += 1
                #print "updatenum= ",self.updatenum
                if self.Qlearning_enable == 1:
                    self.action = curStartFlow.pathNodeIds
                    if len(self.action) == 5:
                        #self.pre_state = self.state[:]
                        self.pre_LinkUtilization = self.LinkUtilization[:]
                        self.pre_ActiveFlowNum = self.ActiveFlowNum[:]
                        self.pre_ActiveElephantFlowNum = self.ActiveElephantFlowNum[:]
                        self.pre_ActiveFlowRemainSize = self.ActiveFlowRemainSize[:]
                        self.Update(curStartFlow)
                        self.printQlearningLog()
                        #reward = self.reward[0]
                        reward = self.reward[1]
                        self.pre_state = self.pre_LinkUtilization
                        self.state = self.LinkUtilization
                        #print self.pre_state
                        #print "len of self.pre_state", len(self.pre_state)
                        #print self.state
                        #print "len of self.state", len(self.state)
                       # self.routing.update(self.pre_state, self.action[1], self.action[3], self.action[2], self.state, reward)
                        #self.Update(self.pre_state, self.action, self.state, self.reward)

                # Resort runningFlows by endTime
                self.sched.runningFlows.sort(key=lambda x: x.finishTime)
                # remove this flow from start list
                self.sched.toStartFlows.remove(curStartFlow)
                #print "finished"
                #print len(self.sched.toStartFlows)

            # Now, all the flows are started
            # Iteratively update flow's transfer time in running list until all the flows are finished
            while self.sched.runningFlows:
                # the first flow is always with earliest finish Time
                curFinishFlow = self.sched.runningFlows[0]
                # remove it from running list
                self.sched.runningFlows.remove(curFinishFlow)
                # insert it to finished flows
                self.sched.finishedFlows.append(curFinishFlow)
                # Update related flow's transfer time in removing a flow
                self.sched.UpdateFlow(curFinishFlow, "remove")
                # Resort runningFlows by endTime
                self.sched.runningFlows.sort(key=lambda x: x.finishTime)

                # update state and reward for Qlearning algorithm
                if self.Qlearning_enable == 1:
                    self.action = curFinishFlow.pathNodeIds
                    if len(self.action) == 5:
                       # self.pre_state = self.state[:]
                       self.pre_LinkUtilization = self.LinkUtilization[:]
                       self.pre_ActiveFlowNum = self.ActiveFlowNum[:]
                       self.pre_ActiveElephantFlowNum = self.ActiveElephantFlowNum[:]
                       self.pre_ActiveFlowRemainSize = self.ActiveFlowRemainSize[:]
                       self.Update(curFinishFlow)
                       #self.printQlearningLog()
                    #self.routing.update(self.pre_state, self.action, self.state, self.reward)
                    #self.Update(self.pre_state, self.action, self.state, self.reward)


            # Finally, all the flows are finished
            self.sched.PrintFlows()
            if self.Qlearning_enable == 1:
                self.logf.close()
            # print "final stateId= ", self.stateId
            
            #collect normalized transmission time of all flows
            self.average_norm_trans_time = 0.0
            for flow in self.flows:
                self.norm_trans_time[flow.flowId] = (flow.finishTime-flow.startTime)/flow.flowSize
                self.average_norm_trans_time += self.norm_trans_time[flow.flowId]
            self.average_norm_trans_time /= len(self.flows)
    
    def printQlearningLog(self):
        print >> self.logf, "%d,%d,%d,%f,%f" % (self.stateId, self.stateId + 1, self.action[2], self.reward[0], self.reward[1])
      #  flag = 0
        statename_list =["LinkUtilization","ActiveFlowNum","ActiveElephantFlowNum","ActiveFlowRemainSize"]
        for statename in statename_list:
            state_fname = str("state_" + str(statename) + "_" + str(self.stateId))
            statef = open(self.logDir + state_fname, "w")
            # select the flow attribution to print
            flowattr_toprint= getattr(self, "pre_" + statename)
            # print flowattr_toprint
            for a in flowattr_toprint:
                if statename == "LinkUtilization" or statename == "ActiveFlowRemainSize":
                    print >> statef, "%f" % (a)
                elif statename == "ActiveFlowNum" or statename == "ActiveElephantFlowNum":
                    print >> statef, "%d" %(a)

            statef.close()
        self.stateId += 1

        for statename in statename_list:
            state_fname = str("state_" + str(statename) + "_" + str(self.stateId))
            statef = open(self.logDir + state_fname, "w")
            flowattr_toprint= getattr(self, statename)
            #print flowattr_toprint
            for a in flowattr_toprint:
               # print "a= ",a
                if statename == "LinkUtilization" or statename == "ActiveFlowRemainSize":
                    print >> statef, "%f" % (a)
                elif statename == "ActiveFlowNum" or statename == "ActiveElephantFlowNum":
                    print >> statef, "%d" %(a)
            statef.close()
        self.stateId += 1

    def changeSpine(self, curStartFlow, spine):  #aborted
        curStartFlow.pathLinkIds[1] = (curStartFlow.pathLinkIds[1][0], spine.nodeId)
        curStartFlow.pathLinkIds[2] = (spine.nodeId, curStartFlow.pathLinkIds[2][1])
        curStartFlow.pathNodeIds[2] = spine.nodeId
