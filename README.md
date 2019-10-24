# Social_Network_Simulation
Python code to implement graph simulation of a social network.

Social networks are modelled as a directed graph of users.

## Environment

To prepare your environment to run this code, first install conda.
Then, while in the top-level directory, run the commands:

```conda env create -f environment.yaml```

```conda activate social-network-sim```

This code can be run without using the conda environment (requires Python 3.7).
However, graphical representation of the social network will not work.

Code can be found in the ```src``` directory.
The main program can be found in SocialNetworkSim.py,
while the gridsearch data collection program can be found in
SocialNetworkSimRunner.py.

## Documentation

Documentation is generated using sphinx, and can be created by changing into the
src directory and running ```make```.

The documentation, report, and UML files can be found in the report directory.
Pdf files were generated using lualatex.
UML files were generated using dot.

Example data provided by the unit coordinator can be found in the example directory.

## Testing

To run unit tests, change into the src directory and run the command:

```python3 -m unittest discover . -p '*'```

This automatically executes all unittests in the program.
