# Strategic-feeder-network-for-an-optimized-maritime-gateway
The study proposes a Strategic 
Feeder Network for an Optimized Maritime Gateway (SFNOMG) model to support 
countries lacking strategic ports in building a more efficient maritime transport system. 
The model is designed in a two-stage structure: (1) selecting a hub port on the mainline to 
collect goods from feeder ports and transport them to a fixed gateway port, and (2) from 
the gateway port, goods are distributed to satellite ports in the region. The study uses the 
mixed-integer linear programming (MILP) method and the Adaptive Large Neighborhood 
Search (ALNS) algorithm to solve the optimization problem. Numerical illustrations are 
constructed to illustrate how effective the model is in lowering transportation expenses and 
improving network efficiency. The results show that the SFNOMG model has high 
potential for practical application, especially in developing countries with limited port 
infrastructure. The study contributes to providing a tool to support strategic decision
making in maritime transport planning and port system development in a more sustainable 
and proactive direction. 
Introduction for Running the PYTHON and CPLEX:
1. Required files
Before running the program, make sure you have downloaded all the following files:
a) Python Files:
- user_interface.py: This is the main script to run the whole process. It serve as the entry point for the user.
- configuration_data1.py: This file contains parameter and data configuration required for initializing the algorithm and model.
- ALNS.py: This file implements the Adaptive Large Neighborhood Search (ALNS) algorithm for solving the optimization problem.
b) CPLEX Files:
- Model files: These files defines the CPLEX optimization model (objective function, variables, constraints).
  Thesis.mod: File model for phase 1 and phase 2
  phase2.mod: File model for phase 2 
- Data file: These files provide the input data for the model (e.g., distances, costs, demand).
2. Environment Setup
You need to install the following Python libraries:
pip install PyQt5
pip install matplotlib
pip install numpy
3. Update File Path
4. Run the Program
Once everything is set up, simply run user_interface.py to start the program.



