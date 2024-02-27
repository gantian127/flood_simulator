# Flood Simulator

This repository includes a Flood Simulator which uses the  
[Overlandflow component](https://landlab.readthedocs.io/en/master/user_guide/overland_flow_user_guide.html) 
from [Landlab](https://landlab.readthedocs.io/en/master/)to simulate the overland flow process for 
a given study area. Example input and output files are provided.

### Run Flood Simulator
Method 1: use Python

```python
from flood_simulator import FloodSimulator

fs = FloodSimulator.from_file('config_file.toml')
fs.run()

```
Method 2: use command
```bash
$ python flood_simulator.py config_file.toml
```
