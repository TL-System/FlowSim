flowsim

A.k.a. FlowSimulator
A.k.a. FlowsImproved

An generic event-driven flow-level network simulator for fast prototype implementation.
The goal is to evaluate rate control transport schemes for data center networks.

Topologies:
- FatTree
- SpineLeaf

Traffic arrival models:
- Poisson
- On/Off

Load balancing:
- ECMP
- Hedera
- Conga


How to run the code?

1. "cd FlowSim/TestHuawei"
2. "python Runner.py [-r routing_scheme]"                 //the routing_scheme can be "ECMP" or "LB"

a brief introduction to the code:

- Routing
  - ECMP_SpineLeaf.py: Implement the ECMP routing scheme on SpineLeaf topology.
  - LB_SpineLeaf.py:  Implement one load balancing (LB) scheme on SpineLeaf topology.
- Src
  - Link.py, Node.py: Define two classes to describe the links and nodes (servers and switches) of data center topologies, respectively.
  - Flow.py, Coflow.py: Define two lasses to describe the flow and coflow, respectively.
  - FlowScheduler.py: The code to do flow scheduling of all input flows with varying start times and flow sizes.
  - Topology.py: A class used to describe the attributes of data center topologies.
  - Routing.py: A class specify some virtual functio that routing schemes. 
  - Simulator.py: The code of simulator.

