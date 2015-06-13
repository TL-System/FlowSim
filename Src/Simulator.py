__author__ = 'lich'

from Unit import *

# Flow-level simulator written in python.
# This file describes the design of class Simulator.

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
        # We can get path by
        # path_3_5 = self.routing.GetPath(3,5)             # result is a list with node ids

    def AssignScheduler(self, FlowScheduler, args):
        """
        Assign the flow scheduler. It also assign the flows to be scheduled.
        """
        self.sched = FlowScheduler()
        self.sched.AssignFlows(args)
        self.sched.AssignLinks(self.topo.GetLinks())
        self.flows = self.sched.GetAllFlows()
        for flow in self.flows:
            self.routing.BuildPath(flow.startId, flow.endId)
            pathNodeIds = self.routing.GetPath(flow.startId, flow.endId)
            flow.BuildPath(pathNodeIds)

    def Run(self):
        """
        Fire up the simulator. The function calculates the transferring time for each flow.
        """
        # start all the flows along with updating related flow's transfer time
        while self.sched.toStartFlows:
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
                else:
                    break
            # insert current start flow to running list
            self.sched.runningFlows.append(curStartFlow)
            # Update related flow's transfer time in removing a flow
            self.sched.UpdateFlow(curStartFlow, "insert")
            # Resort runningFlows by endTime
            self.sched.runningFlows.sort(key=lambda x: x.finishTime)
            # remove this flow from start list
            self.sched.toStartFlows.remove(curStartFlow)

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

        # Finally, all the flows are finished
        self.sched.PrintFlows()
