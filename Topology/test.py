from SpineLeaf import *

# topo1 = FatTree(K=4)
# topo1.CreateTopology()
# f = open("fat.txt", "w")
# for linkId in topo1.links:
#    print >> f, linkId
# f.close()

topo2 = SpineLeaf()
topo2.CreateTopology()
f = open("spine.txt", "w")
print >> f, '%i Servers' % topo2.numOfServers
print >> f, '%i Leaves' % topo2.numOfToRs
print >> f, '%i Spines' % topo2.numOfCores
# for linkId in topo2.links:
# print >> f, linkId
# for node in topo2.nodes:
# print >>f, node.nodeId
# f.close()
print >> f, topo2.GetServerNode(0).nodeId
print >> f, topo2.GetToRNode(0).nodeId
print >> f, topo2.GetCoreNode(0).nodeId
