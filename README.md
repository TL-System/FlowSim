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
2. "python Runner.py [-r routing_scheme]"                 //the routing_scheme currently can be "ECMP" or "LB" or
                                                          //"Qlearning". E.g., python Runner.py -r Qlearning

Where to implement Qlearning algorithm?

Please open FlowSim/Routing/Qlearning_SpineLeaf.py, and check function "def select_action(self, state)".
 
a brief introduction to the code:

- Routing
  - ECMP_SpineLeaf.py: Code of the ECMP routing scheme on SpineLeaf topology.
  - LB_SpineLeaf.py:  Code of one load balancing (LB) scheme on SpineLeaf topology.
  - Qlearning_SpineLeaf.py: Code of the Qlearning routing scheme on SpineLeaf topology.
- Topology
  - SpineLeaf.py: the code of spine-leaf topology.
- Src
  - Link.py, Node.py: Code of links and nodes (servers and switches) of data center topologies, respectively.
  - Flow.py, Coflow.py: Code of flow and coflow, respectively.
  - FlowScheduler.py: The code to do flow scheduling of all input flows with varying start times and flow sizes.
  - Topology.py: The code of a class called "Topology" which defines a general data topology. All the specific topologies in Topology directory should be a subclass of "Topology" class.
  - Routing.py: The code of a class called "Routing" which defines a general routing scheme. All the specific routing schemes in Routing directory should be a subclass of "Routing" class. 
  - Simulator.py: The code of simulator.
- TestHuawei
  - Input: Input data.
  - Output: Output data.
    - LogInfo: trace of state updates.
  - TestFlowScheduler.py: the code todo input and output.
  - TestSimulator.py: the code to run simulator.py.
  - Runner.py: the script to run simulations with different options.
