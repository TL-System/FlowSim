# This file describes the class FlowScheduler


class FlowScheduler:
    def __init__(self):
        # Flow list in initial time
        self.flows = []

        # Flows to start
        self.toStartFlows = []

        # Running flows
        self.runningFlows = []

        # Finished flows
        self.finishedFlows = []

        # Topology Links. This should not be there. I will remove it in future version.
        # self.Links = []
        # self.Nodes = []

    def AssignLinks(self, links):
        """
        Need links to update flow info
        """
        self.Links = links

    def AssignNodes(self, nodes):
        """
        Need links to update flow info
        """
        self.Nodes = nodes

    def AssignFlows(self, topo=None, filename=None):
        """
        Assign flows including flow id, flow size, flow start id and end id, flow start time.
        It can read flow info from a configuration file or assigned by some parameters.
        Return the flow list.
        """
        self.toStartFlows = self.flows[:]
        # Sort the flows in place
        self.toStartFlows.sort(key=lambda x: x.startTime)

    def GetFlow(self, flowId):
        """
        Note that a pair of node ids cannot identify a flow since there may have multiple flows between them.
        Flow id is the only identifier to pick a flow.
        """
        return self.flows[flowId]

    def GetAllFlows(self):
        return self.flows

    def UpdateFlow1(self, curFlow, flag):
        """
        Find related flows and update their flowBw, transTime, endTime.
        """
        curTime = 0.0
        pathInLink = curFlow.pathLinkIds
        for linkId in pathInLink:
            link = self.Links[linkId]
            if flag == "remove":
                link.flowIds.remove(curFlow.flowId)
                curTime = curFlow.finishTime
            elif flag == "insert":
                link.flowIds.append(curFlow.flowId)
                curTime = curFlow.startTime
                curFlow.updateTime = curTime
        current_flows = list(self.runningFlows)
        residual_cap = {}
        residual_flowIds = {}
        for link_id in self.Links:
            link = self.Links[link_id]
            residual_cap[link_id] = link.linkCap
            residual_flowIds[link_id] = list(link.flowIds)
        while current_flows != []:
            bottleneck_rate = 10.0e100
            bottleneck_link = ()
            for link_id in self.Links:
                if len(residual_flowIds[link_id]) != 0:
                    if bottleneck_rate >= residual_cap[link_id] / len(residual_flowIds[link_id]):
                        bottleneck_rate = residual_cap[link_id] / len(residual_flowIds[link_id])
                        bottleneck_link = link_id
            for flowId in residual_flowIds[bottleneck_link]:
                flow = self.flows[flowId]
                flow.remainSize -= flow.bw * (curTime - flow.updateTime)
                flow.updateTime = curTime
                flow.bw = bottleneck_rate
                flow.finishTime = curTime + flow.remainSize / bottleneck_rate
                current_flows.remove(flow)
                pathInLink = flow.pathLinkIds
                for linkId in pathInLink:
                    residual_cap[linkId] = residual_cap[linkId] - bottleneck_rate
                    residual_flowIds[linkId].remove(flowId)
        nodeInPath = curFlow.pathNodeIds
        for nodeId in nodeInPath:
            node = self.Nodes[nodeId]
            if flag == "remove":
                node.flowIds.remove(curFlow.flowId)
            elif flag == "insert":
                node.flowIds.append(curFlow.flowId)

    def UpdateFlow2(self, curFlow, flag):
        """
        Find related flows and update their flowBw, transTime, endTime.
        """
        curTime = 0.0
        pathInLink = curFlow.pathLinkIds
        for linkId in pathInLink:
            link = self.Links[linkId]
            if flag == "remove":
                link.flowIds.remove(curFlow.flowId)
                curTime = curFlow.finishTime
            elif flag == "insert":
                link.flowIds.append(curFlow.flowId)
                curTime = curFlow.startTime
                curFlow.updateTime = curTime
        current_flows = list(self.runningFlows)
        current_links = list(self.Links)
        residual_cap = {}
        residual_flowIds = {}
        for link_id in self.Links:
            link = self.Links[link_id]
            residual_cap[link_id] = link.linkCap
            residual_flowIds[link_id] = list(link.flowIds)
        for flow in current_flows:
            flow.remainSize -= flow.bw * (curTime - flow.updateTime)
            flow.bw = 0.0
        while current_flows:
            bottleneck_rate = link.linkCap
            for link_id in current_links:
                if len(residual_flowIds[link_id]) != 0:
                    if bottleneck_rate >= residual_cap[link_id] / len(residual_flowIds[link_id]):
                        bottleneck_rate = residual_cap[link_id] / len(residual_flowIds[link_id])
            bottleneck_rate = max([min([bottleneck_rate, link.linkCap]), 0.001])
            links_to_remove = []
            for link_id in current_links:
                residual_cap[link_id] -= bottleneck_rate * len(residual_flowIds[link_id])
                if residual_cap[link_id] <= 1.0e-20:
                    links_to_remove.append(link_id)
            for link_id in links_to_remove:
                current_links.remove(link_id)
            flows_to_remove = []
            for flow in current_flows:
                flow.bw += bottleneck_rate
                pathInLink = flow.pathLinkIds
                check = 1
                for link_id in pathInLink:
                    if residual_cap[link_id] <= 1.0e-20:
                        check = 0
                        break
                if check == 0:
                    pathInLink = flow.pathLinkIds
                    for link_id in pathInLink:
                        residual_flowIds[link_id].remove(flow.flowId)
                    flow.updateTime = curTime
                    flow.finishTime = curTime + flow.remainSize / flow.bw
                    flows_to_remove.append(flow)
            for flow in flows_to_remove:
                current_flows.remove(flow)

        nodeInPath = curFlow.pathNodeIds
        for nodeId in nodeInPath:
            node = self.Nodes[nodeId]
            if flag == "remove":
                node.flowIds.remove(curFlow.flowId)
            elif flag == "insert":
                node.flowIds.append(curFlow.flowId)

    def PrintFlows(self, outname=None):
        """
        print finishedFlows
        """
        for f in self.finishedFlows:
            print(f.flowId)
