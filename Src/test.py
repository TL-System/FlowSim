
from Routing import *
from Topology import *
from Node import *
from Link import *

def BuildMatrix():
    topo = []
    topo.append([0,1,0,1,0,0])
    topo.append([1,0,1,0,1,0])
    topo.append([0,1,0,1,1,0])
    topo.append([1,0,1,0,0,0])
    topo.append([0,1,1,0,0,1])
    topo.append([0,0,0,0,1,0])
    return topo

def main():
    topoMatrix = BuildMatrix()
    topo = Topology()
    topo.GenTopoFromMatrix(topoMatrix, 6, Node, Link)
    routing = Routing()
    routing.BFS(topo)
    for path in routing.pathList:
        print path, "\t", routing.pathList[path]

if __name__ == "__main__":
    main()
