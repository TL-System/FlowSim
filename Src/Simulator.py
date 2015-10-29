from Unit import *
from TestHuawei.Input.make_trace import *
import time

# from Src.Flow import *
# import sys
# sys.path.append("..")
# Flow-level simulator written in python.
# This file describes the design of class Simulator.
# from Topology.SpineLeaf import *
# print sys.path
# from Routing.ECMP_SpineLeaf import *
# from Routing.LB_SpineLeaf import *
# from Routing.Qlearning_SpineLeaf import *
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

    def AssignRoutingEngine(self, max_episodes, reward_type, features, number_hidden_nodes_per_layer, exploration_type,
                            epsilon, setting, Routing):
        """
        Assign the routing method in a centralized way.
        Routing is a function that takes topo as input
        """
        self.stateId = 0
        self.number_state_vectors = len(features)
        self.reward_type = reward_type
        self.features = features
        self.setting = setting
        self.max_episodes = max([1, max_episodes])
        if str(Routing) == "Routing.Qlearning_SpineLeaf.Qlearning":
            self.routing = Routing(self.number_state_vectors, number_hidden_nodes_per_layer, exploration_type, epsilon,
                                   self.topo)
        else:
            self.routing = Routing(self.topo)
        self.Qlearning_enable = 0
        self.logDir = "LogInfo/"
        print "Start changing Qlearning_enable"
        if str(Routing) == "Routing.Qlearning_SpineLeaf.Qlearning":
            self.Qlearning_enable = 1
            print "linkNum between Switches: ", self.topo.GetLinkNumbetweenSwitch()
            self.LinkUtilization = [0.0] * self.topo.GetLinkNumbetweenSwitch()
            self.ActiveFlowNum = [0] * self.topo.GetLinkNumbetweenSwitch()
            self.ActiveElephantFlowNum = [0] * self.topo.GetLinkNumbetweenSwitch()
            self.ActiveFlowRemainSize = [0.0] * self.topo.GetLinkNumbetweenSwitch()
            self.state = []
            # print len(self.topo.GetLinks())
            self.reward = [0.0, 0.0]
            self.stateId = 0
            # self.logfname = "StateLog.csv"
            # self.logf = open(self.logDir + self.logfname, "w")
        # self.updatenum=0
        elif str(Routing) == "Routing.ECMP_SpineLeaf.ECMP":
            self.Qlearning_enable = 2
            self.LinkUtilization = [0.0] * self.topo.GetLinkNumbetweenSwitch()
        elif str(Routing) == "Routing.FlowLB_SpineLeaf.FlowLB":
            self.Qlearning_enable = 3
            self.LinkUtilization = [0.0] * self.topo.GetLinkNumbetweenSwitch()
            # We can get path by
            # path_3_5 = self.routing.GetPath(3,5)             # result is a list with node ids
        print "Qlearning_enable={}".format(self.Qlearning_enable)

    def setSchedType(self, FlowScheduler):
        self.schedType = FlowScheduler

    def setTraceFName(self, TraceFName):
        self.TraceFName = TraceFName

    def AssignScheduler(self, FlowScheduler, args):
        """
        Assign the flow scheduler. It also assign the flows to be scheduled.
        """
        # self.schedType = FlowScheduler
        self.sched = FlowScheduler()
        self.sched.AssignFlows(self.topo, args)
        self.sched.AssignLinks(self.topo.GetLinks())
        self.sched.AssignNodes(self.topo.GetNodes())
        self.flows = self.sched.GetAllFlows()
        self.norm_trans_time = [0.0] * len(self.flows)
        # for flow in self.flows:
        #     self.routing.BuildPath(flow.startId, flow.endId)
        #     pathNodeIds = self.routing.GetPath(flow.startId, flow.endId)
        #     flow.BuildPath(pathNodeIds)

    def AssignLoadBalancer(self, LoadBalancer, args):
        self.lb = LoadBalancer()

    def Update(self, flow):
        # update state list by dimension
        dim_id = 0
        for key in self.sched.Links.keys():
            if key[0] >= self.topo.numOfServers and key[1] >= self.topo.numOfServers:
                self.LinkUtilization[dim_id] = self.sched.Links[key].GetLinkUtilization(self.flows)
                self.ActiveFlowNum[dim_id] = self.sched.Links[key].GetActiveFlowNum()
                self.ActiveElephantFlowNum[dim_id] = self.sched.Links[key].GetActiveElephantFlowNum(self.flows)
                self.ActiveFlowRemainSize[dim_id] = self.sched.Links[key].GetActiveFlowRemainSize(self.flows)
                dim_id += 1

        # reward of type 1
        # r1 = - 1.0 / (flow.bw/(1024.0*1024.0)) * 2
        r1 = flow.bw / (1024.0 * 1024.0 * 1024.0)
        # reward of type 2
        r2 = 0.0
        for linkId in flow.pathLinkIds:
            link = self.sched.Links[linkId]
            if linkId[0] >= self.topo.numOfServers and linkId[1] >= self.topo.numOfServers and link.GetLinkUtilization(
                    self.flows) > r2:
                r2 = link.GetLinkUtilization(self.flows)
        r2 = -r2
        # reward of type 3
        r3 = 0.0
        for linkId in flow.pathLinkIds:
            link = self.sched.Links[linkId]
            if linkId[0] >= self.topo.numOfServers and linkId[
                1] >= self.topo.numOfServers and link.GetActiveElephantFlowNum(self.flows) / 100.0 > r3:
                r3 = link.GetActiveElephantFlowNum(self.flows) / 100.0
        r3 = -r3
        self.reward = [r1, r2, r3]

    def Run(self):
        """
        Fire up the simulator. The function calculates the transferring time for each flow.
        """
        # start all the flows along with updating related flow transfer time
        self.AssignScheduler(FlowScheduler=self.schedType, args=self.TraceFName)
        if self.Qlearning_enable == 1:
            self.logfname = "Reward_QLearning" + self.setting + ".csv"
            self.logfname2 = "FCT_QLearning" + self.setting + ".csv"
        elif self.Qlearning_enable == 2:
            self.logfname = "Reward_ECMP" + self.setting + ".csv"
            self.logfname2 = "FCT_ECMP" + self.setting + ".csv"
        elif self.Qlearning_enable == 3:
            self.logfname = "Reward_FlowLB" + self.setting + ".csv"
            self.logfname2 = "FCT_FlowLB" + self.setting + ".csv"
        else:
            # Most likely for LB
            self.logfname = "Reward_LB" + self.setting + ".csv"
            # self.logf = open(self.logDir + self.logfname, "w").close()
            self.logfname2 = "FCT_LB" + self.setting + ".csv"
            # self.logf2 = open(self.logDir + self.logfname2, "w").close()
        print "erase the previous content for {} and {}".format(self.logfname, self.logfname2)
        open("{0}{1}".format(self.logDir, self.logfname), "w").close()
        open("{0}{1}".format(self.logDir, self.logfname2), "w").close()

        for episode in range(self.max_episodes):
            # print "episode number ", episode+1
            # generate_trace()
            # self.AssignScheduler(FlowScheduler=self.schedType, args=self.TraceFName)
            self.sched.toStartFlows = self.sched.flows[:]
            self.sched.toStartFlows.sort(key=lambda x: x.startTime)
            self.sched.runningFlows = []
            self.finishedFlows = []
            for flow in self.sched.flows:
                flow.bw = 0.0
                flow.pathNodeIds = []
                flow.pathLinkIds = []
                flow.updateTime = 0.0
                flow.finishTime = 0.0
                flow.remainSize = flow.flowSize

            # if self.Qlearning_enable == 1:
            #   self.logfname = "StateLog" + str(episode) + ".csv"
            #   self.logf = open(self.logDir + self.logfname, "w")
            total_reward = 0
            total_reward2 = 0
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
                        self.sched.UpdateFlow2(toFinishFlow, "remove")
                        # Resort runningFlows by endTime
                        self.sched.runningFlows.sort(key=lambda x: x.finishTime)

                        if self.Qlearning_enable == 1:
                            self.action = toFinishFlow.pathNodeIds
                            if len(self.action) == 5:
                                self.pre_LinkUtilization = self.LinkUtilization[:]
                                self.pre_ActiveFlowNum = self.ActiveFlowNum[:]
                                self.pre_ActiveElephantFlowNum = self.ActiveElephantFlowNum[:]
                                self.pre_ActiveFlowRemainSize = self.ActiveFlowRemainSize[:]
                                self.Update(toFinishFlow)
                                # self.printQlearningLog()

                    else:
                        break

                # TODO: Very poor object oriented programming here!!!
                # insert current start flow to running list
                if self.Qlearning_enable == 1:
                    self.routing.BuildPath(curStartFlow.startId, curStartFlow.endId, curStartFlow, self.state)
                elif self.Qlearning_enable == 0:
                    # LB
                    self.routing.BuildPath(curStartFlow.startId, curStartFlow.endId, curStartFlow)
                elif self.Qlearning_enable == 2:
                    # reward ecmp
                    self.routing.BuildPath(curStartFlow.startId, curStartFlow.endId, curStartFlow, self.flows)
                elif self.Qlearning_enable == 3:
                    # flowLB
                    self.routing.BuildPath(curStartFlow.startId, curStartFlow.endId, curStartFlow, self.flows)

                pathNodeIds = self.routing.GetPath(curStartFlow.startId, curStartFlow.endId)
                curStartFlow.BuildPath(pathNodeIds)
                self.sched.runningFlows.append(curStartFlow)
                if self.Qlearning_enable == 2 or self.Qlearning_enable == 3:
                    if self.reward_type == 3:
                        dim_id = 0
                        for key in self.sched.Links.keys():
                            if key[0] >= self.topo.numOfServers and key[1] >= self.topo.numOfServers:
                                self.LinkUtilization[dim_id] = self.sched.Links[key].GetLinkUtilization(self.flows)
                                dim_id += 1
                        self.pre_LinkUtilization = self.LinkUtilization[:]
                # update state and reward for Qlearning algorithm
                self.sched.UpdateFlow2(curStartFlow, "insert")
                # self.updatenum += 1
                # print "updatenum= ",self.updatenum
                if self.Qlearning_enable == 1:
                    self.action = curStartFlow.pathNodeIds
                    if len(self.action) == 5:
                        # self.pre_state = self.state[:]
                        self.pre_LinkUtilization = self.LinkUtilization[:]
                        self.pre_ActiveFlowNum = self.ActiveFlowNum[:]
                        self.pre_ActiveElephantFlowNum = self.ActiveElephantFlowNum[:]
                        self.pre_ActiveFlowRemainSize = self.ActiveFlowRemainSize[:]
                        self.Update(curStartFlow)
                        # self.printQlearningLog()
                        reward = 0
                        if self.reward_type == 0:
                            reward = self.reward[0]
                        elif self.reward_type == 1:
                            reward = self.reward[1]
                        elif self.reward_type == 2:
                            reward = self.reward[2]
                        elif self.reward_type == 3:
                            reward = max([(self.LinkUtilization[i] - self.pre_LinkUtilization[i]) for i in
                                          range(len(self.LinkUtilization))])
                        total_reward += reward
                        self.pre_state = []
                        self.state = []
                        if 0 in self.features:
                            self.pre_state = self.pre_state + [x / 100.0 for x in self.pre_ActiveElephantFlowNum]
                            self.state = self.state + [x / 100.0 for x in self.ActiveElephantFlowNum]
                        if 1 in self.features:
                            self.pre_state = self.pre_state + [x / 1000000000.0 for x in self.pre_ActiveFlowRemainSize]
                            self.state = self.state + [x / 1000000000.0 for x in self.ActiveFlowRemainSize]
                        if 2 in self.features:
                            self.pre_state = self.pre_state + [x for x in self.pre_LinkUtilization]
                            self.state = self.state + [x for x in self.LinkUtilization]
                        if 3 in self.features:
                            self.pre_state = self.pre_state + [x / 100.0 for x in self.pre_ActiveFlowNum]
                            self.state = self.state + [x / 100.0 for x in self.ActiveFlowNum]
                        self.routing.update(self.pre_state, self.action[1], self.action[3], self.action[2], self.state,
                                            reward)
                elif self.Qlearning_enable == 2 or self.Qlearning_enable == 3:
                    if self.reward_type == 0:
                        total_reward2 += curStartFlow.bw / (1024.0 * 1024.0 * 1024.0)
                    elif self.reward_type == 1:
                        r = 0.0
                        for linkId in curStartFlow.pathLinkIds:
                            link = self.sched.Links[linkId]
                            if linkId[0] >= self.topo.numOfServers and linkId[
                                1] >= self.topo.numOfServers and link.GetLinkUtilization(self.flows) > r:
                                r = link.GetLinkUtilization(self.flows)
                        total_reward2 += -r
                    elif self.reward_type == 2:
                        r = 0.0
                        for linkId in curStartFlow.pathLinkIds:
                            link = self.sched.Links[linkId]
                            if linkId[0] >= self.topo.numOfServers and linkId[
                                1] >= self.topo.numOfServers and link.GetActiveElephantFlowNum(self.flows) / 100.0 > r:
                                r = link.GetActiveElephantFlowNum(self.flows) / 100.0
                        total_reward2 += -r
                    elif self.reward_type == 3:
                        dim_id = 0
                        for key in self.sched.Links.keys():
                            if key[0] >= self.topo.numOfServers and key[1] >= self.topo.numOfServers:
                                self.LinkUtilization[dim_id] = self.sched.Links[key].GetLinkUtilization(self.flows)
                                dim_id += 1
                        total_reward2 += max([(self.LinkUtilization[i] - self.pre_LinkUtilization[i]) for i in
                                              range(len(self.LinkUtilization))])
                # Resort runningFlows by endTime
                self.sched.runningFlows.sort(key=lambda x: x.finishTime)
                # remove this flow from start list
                self.sched.toStartFlows.remove(curStartFlow)

            # print "Now, all the flows are started"
            # Iteratively update flow's transfer time in running list until all the flows are finished
            while self.sched.runningFlows:
                # the first flow is always with earliest finish Time
                curFinishFlow = self.sched.runningFlows[0]
                # remove it from running list
                self.sched.runningFlows.remove(curFinishFlow)
                # insert it to finished flows
                self.sched.finishedFlows.append(curFinishFlow)
                # Update related flow's transfer time in removing a flow
                self.sched.UpdateFlow2(curFinishFlow, "remove")
                # Resort runningFlows by endTime
                self.sched.runningFlows.sort(key=lambda x: x.finishTime)

                # update state and reward for Qlearning algorithm
                if self.Qlearning_enable == 1:
                    self.action = curFinishFlow.pathNodeIds
                    if len(self.action) == 5:
                        self.pre_LinkUtilization = self.LinkUtilization[:]
                        self.pre_ActiveFlowNum = self.ActiveFlowNum[:]
                        self.pre_ActiveElephantFlowNum = self.ActiveElephantFlowNum[:]
                        self.pre_ActiveFlowRemainSize = self.ActiveFlowRemainSize[:]
                        self.Update(curFinishFlow)
                        # self.printQlearningLog()

            # print "Finally, all the flows are finished"
            self.sched.PrintFlows()
            # self.printQlearningLog()
            # if self.Qlearning_enable == 1:
            #    self.logf.close()
            # print "final stateId= ", self.stateId

            # collect normalized transmission time of all flows
            self.average_norm_trans_time = 0.0
            for flow in self.flows:
                self.norm_trans_time[flow.flowId] = (flow.finishTime - flow.startTime) / flow.flowSize
                self.average_norm_trans_time += self.norm_trans_time[flow.flowId]
            self.average_norm_trans_time /= len(self.flows)
            # print "average normalized (per bit) transmission time",self.average_norm_trans_time

            print "printing to {} and {}.".format(self.logfname, self.logfname2)
            logf = open("{0}{1}".format(self.logDir, self.logfname), "a")
            logf2 = open("{0}{1}".format(self.logDir, self.logfname2), "a")
            if self.Qlearning_enable == 1:
                print >> logf, "%f" % (total_reward / counter)
                print >> logf2, "%e" % self.average_norm_trans_time
                print "Qlearning={},total_reward={}".format(self.Qlearning_enable, total_reward)
                print total_reward / counter, self.average_norm_trans_time
            elif self.Qlearning_enable == 2 or self.Qlearning_enable == 3:
                print >> logf, "%f" % (total_reward2 / counter)
                print >> logf2, "%e" % self.average_norm_trans_time
                print total_reward2 / counter, self.average_norm_trans_time
            logf.close()
            logf2.close()

    def printQlearningLog(self):
        logf = open("{0}{1}".format(self.logDir, self.logfname), "a")
        # TODO: Everything it needs is not available. Variable Scope is not set properly.
        print >> logf, "%d,%d,%d,%f,%f" % (
        self.stateId, self.stateId + 1, self.action[2], self.reward[0], self.reward[1])
        logf.close()
        #  flag = 0
        statename_list = ["LinkUtilization", "ActiveFlowNum", "ActiveElephantFlowNum", "ActiveFlowRemainSize"]
        for statename in statename_list:
            state_fname = str("state_" + str(statename) + "_" + str(self.stateId))
            statef = open(self.logDir + state_fname, "a")
            # select the flow attribution to print
            flowattr_toprint = getattr(self, "pre_" + statename)
            # print flowattr_toprint
            for a in flowattr_toprint:
                if statename == "LinkUtilization" or statename == "ActiveFlowRemainSize":
                    print >> statef, "%f" % (a)
                elif statename == "ActiveFlowNum" or statename == "ActiveElephantFlowNum":
                    print >> statef, "%d" % (a)
            statef.close()
        self.stateId += 1

        for statename in statename_list:
            state_fname = str("state_" + str(statename) + "_" + str(self.stateId))
            statef = open(self.logDir + state_fname, "a")
            flowattr_toprint = getattr(self, statename)
            # print flowattr_toprint
            for a in flowattr_toprint:
                # print "a= ",a
                if statename == "LinkUtilization" or statename == "ActiveFlowRemainSize":
                    print >> statef, "%f" % (a)
                elif statename == "ActiveFlowNum" or statename == "ActiveElephantFlowNum":
                    print >> statef, "%d" % (a)
            statef.close()
        self.stateId += 1

    def changeSpine(self, curStartFlow, spine):  # aborted
        curStartFlow.pathLinkIds[1] = (curStartFlow.pathLinkIds[1][0], spine.nodeId)
        curStartFlow.pathLinkIds[2] = (spine.nodeId, curStartFlow.pathLinkIds[2][1])
        curStartFlow.pathNodeIds[2] = spine.nodeId
