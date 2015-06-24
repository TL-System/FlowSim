__author__ = 'lich'

from Unit import *

# This file describes the base class of link
# All the specific link class should inherit this class

class Link:

    def __init__(self, id):
        # link ID is named as tuple of (start node id, destination node id)
        self.linkId = id

        # link capacity
        self.linkCap = 1.0 * Gb

        # Current Flow ids on this link
        self.flowIds = []

        self.flowRates = dict()

        # Scheduling strtegy of this link
        # Weight fair queueing, strict priority queueing, Max-min Fair (Default)
        self.scheduling = 'maxmin'

    def SetCap(self, cap):
        self.linkCap = float(cap * Gb)

    def SetScheduling(self, sched):
        if sched == 'maxmin' or sched == 'wfq' or sched == 'sp':
            self.scheduling = sched
        else:
            print("Error: " + sched + ' is unavailable. Try \'maxmin\', \'wfq\', or \'sp\'')

    def UpdateRates(self, flow):
        #TODO: assign rates to all flows, and return the rate of input
        return self.flowRates[flow]

    def __del__(self):
        pass
