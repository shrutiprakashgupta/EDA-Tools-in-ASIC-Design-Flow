# EDA-tools-in-ASIC-Design-flow:
EDA tools largely use heuristic methods to arrive at solutions for the various stages of design flow. The implementation of general algorithms and data structures becomes more interesting when mixed with the constraint requirements of the VLSI Design. This repository includes the core implementation of a few of these algorithms and methods, pertaining to the Place and Route steps and Boolean complement calculation. Although these tools are highly complex, the fundamental ideas lying behind them are included in this repository. 
# Modules included:
1. Boolean complement computation using Unate Recursive Paradigm
2. Placer 
* Hill climbing Method
* Simulated Annealing Method
* Quadratic Placement Method (with variable block size)
3. Router 
* Plain router (Single layer)
* Router considering bend penalties
* Multi layer router  
# Parameters involved in optimization:
1. Half Perimeter Wirelength 
2. Squared Distance 
3. Weighted Wirelength 
4. Bend Penalties 
5. Via Penalties 
6. Weighted mesh for routing
# Workflow:
1. All of the modules take input as a text file and generate output as a text file.
2. In case of placer and router, a display window opens up which shows the final layout of the chip (along with the placed gates and the wires connecting them).
