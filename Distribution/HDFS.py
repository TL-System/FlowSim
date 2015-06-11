__author__ = 'lich'

import sys
sys.path.append("..")

import random, math
from Topology.FatTree import *

class AllocChunks:
    """
    This class builds the chunks distribution in HDFS.
    """
    def __init__(self, M, d, n, topo):
        """
        M: the rank range of items, it indicates the number of distinct chunks in HDFS
        d: the number of replicas. 3 is default value in HDFS
        n: the number of servers/holders in HDFS.
        topo: the input topology. Note that currently only supports fat-tree topology.
        Note that current version allocator only considers d=3. We will add dynamic allocation mechanism.
        """
        self.M = M
        self.d = d
        self.n = n
        self.topo = topo
        # A list of holders records the instance allocation for each holder
        self.holders = [[] for i in range(n)]
        # A list of chunks records the holder id for each chunk
        self.chunksLocation = [[] for i in range(M)]
        # Also, this list is indexed from 1, not 0
        self.holders.insert(0, None)
        self.chunksLocation.insert(0, None)

        self.InitialItems()
        self.AllocatesNow()
        self.IndexChunkLocation()

    def IndexChunkLocation(self):
        """
        Record the chunk location indexed by chunk Id
        """
        for hId in range(1, self.n + 1):
            for cId in self.holders[hId]:
                self.chunksLocation[cId].append(hId)

    def InitialItems(self):
        """
        Shuffle the item list so as to avoid hot spot allocation.
        """
        self.itemList = [i for i in range(1, self.M + 1)]
        random.shuffle(self.itemList)

    def AllocatesNow(self):
        # the number of slots in each holder
        slots = int(math.ceil(float(self.M) * self.d / self.n))
        # allocates item start from a random holder
        firstHolder = random.randint(1, self.n)
        # a trick flag, to avoid duplicate allocation on the same holder
        offset = 0
        for j in range(1, self.M + 1):
            offset += 1
            # allocates 1st item
            # iteratively find an available Id as the first holder
            counter = 0
            while len(self.holders[firstHolder]) >= slots and counter < self.n:
                firstHolder = (firstHolder + 1) % self.n
                if firstHolder == 0:
                    firstHolder = self.n
                counter += 1
            if counter == self.n:
                print "No more rooms to allocate first items from %d" % j
                sys.exit()
            self.holders[firstHolder].append(j)
            # allocates 2nd item
            secondHolder = self.topo.GetSameRack(firstHolder)
            # iteratively find an available Id as the second holder
            counter = 0
            while len(self.holders[secondHolder]) >= slots and counter < self.n:
                secondHolder = self.topo.GetSameRack(secondHolder)
                counter += 1
            if counter == self.n:
                print "No more rooms to allocate second items from %d" % j
                sys.exit()
            self.holders[secondHolder].append(j)
            # allocate 3rd item
            thirdHolder = self.topo.GetOtherRack(firstHolder, self.n)
            counter = 0
            # iteratively find an available Id as the third holder
            while len(self.holders[thirdHolder]) >= slots and counter < self.n:
                thirdHolder = self.topo.GetSameRack(thirdHolder)
                counter += 1
            if counter == self.n:
                print "No more rooms to allocate third items from %d" % j
                sys.exit()
            self.holders[thirdHolder].append(j)
            # next round, start from the
            firstHolder = (firstHolder + self.topo.K / 2) % self.n
            # the offset is used to make each round allocation is uniform
            # the items in M is allocated topo.numOfToRs in each round, add 1 offset at the end of each round
            # will make the allocation runs uniformly
            if offset % self.topo.numOfToRs == 0:
                firstHolder += 1
            if firstHolder == 0:
                firstHolder = self.n

    def __del__(self):
        pass


