#! /usr/bin/env python

"""
Flood Simulator (Tian Gan, 2023 Aug)

Description:
This code is created for the participatory modeling project.
It includes a class to run the overland flow process using Landlab components.

Future Tasks:
- add rain component to support time series or grid rain input
- add infiltration component to simulate infiltration process

Code References:
- https://github.com/gantian127/overlandflow_usecase/blob/master/overland_flow.ipynb
- https://github.com/gregtucker/earthscape_simulator/blob/main/src/evolve_island_world.py
- https://github.com/landlab/landlab/blob/a5b2f68825a36529acd3c451380ec75e9f48e6e3/landlab/grid/voronoi.py#L174

"""

import sys
import os

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from tqdm import trange
import matplotlib.pyplot as plt
import pandas as pd

from landlab.io import read_esri_ascii, write_esri_ascii
from landlab import imshow_grid
from landlab.components.overland_flow import OverlandFlow


class FloodSimulator:
    def __init__(self, input_params, run_params, output_params):
        """ Initialize FloodSimulator """

        self.input_params = input_params
        self.run_params = run_params
        self.output_params = output_params
        self.model_grid = None
        self.outlet_id = None
        self.setup_grid()

    @classmethod
    def from_file(cls, config_file):
        with open(config_file, mode='rb') as fp:
            args = tomllib.load(fp)
        return cls(**args)

    def setup_grid(self):
        """
        create RasterModelGrid and add data fields:
         - topographci__elevation (set boundary condition)
         - water_surface__elevation
        """

        # topographic elevation and set boundary condition
        self.model_grid, dem_data = read_esri_ascii(self.input_params['grid_file'], name='topographic__elevation')

        if self.input_params['outlet_id'] < 0:
            self.outlet_id = self.model_grid.set_watershed_boundary_condition(
                                    dem_data,
                                    nodata_value=self.input_params['nodata_value'],
                                    return_outlet_id=True)
        else:
            self.model_grid.set_watershed_boundary_condition_outlet_id(
                                    outlet_id=self.input_params['outlet_id'],
                                    node_data=dem_data,
                                    nodata_value=self.input_params['nodata_value'])

        # surface water depth
        self.model_grid.add_zeros("surface_water__depth", at='node')
        self.model_grid.at_node["surface_water__depth"].fill(1e-12)

    def run(self):
        """
        run overland flow simulation
        """

        # set model run parameters
        model_run_time = self.run_params['model_run_time'] * 60  # duration of run (s)
        storm_duration = self.run_params['storm_duration'] * 60  # duration of rain (s)
        time_step = self.run_params['time_step'] * 60  #
        rainfall_intensity = self.run_params['rain_intensity'] / (1000 * 3600)  # mm/hr to m/s
        elapsed_time = 0.0

        # output setup
        outlet_times = []
        outlet_discharge = []
        output_folder = self.output_params['output_folder']

        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)

        # instantiate component and run model
        overland_flow = OverlandFlow(self.model_grid,
                                     steep_slopes=self.run_params['steep_slopes'],
                                     alpha=self.run_params['alpha'],
                                     mannings_n=self.run_params['mannings_n'],
                                     g=self.run_params['g'],
                                     theta=self.run_params['theta'],
                                     )

        for time_slice in trange(time_step, model_run_time + time_step, time_step):

            while elapsed_time < time_slice:
                # get adaptive time step
                overland_flow.dt = min(overland_flow.calc_time_step(), time_slice)

                # set rainfall intensity
                if elapsed_time < storm_duration:
                    overland_flow.rainfall_intensity = rainfall_intensity
                else:
                    overland_flow.rainfall_intensity = 0.0

                # run model
                overland_flow.overland_flow(dt=overland_flow.dt)

                # update elapsed time
                elapsed_time += overland_flow.dt

                # get discharge result at outlet
                discharge = overland_flow.discharge_mapper(
                    self.model_grid.at_link["surface_water__discharge"], convert_to_volume=True
                )

                outlet_discharge.append(discharge[self.outlet_id][0])
                outlet_times.append(elapsed_time)

                # save surface water depth at each time step
                write_esri_ascii(os.path.join(output_folder, "water_depth_{}.asc".format(time_slice)),
                                 self.model_grid, 'surface_water__depth', clobber=True)

            # plot results (this is for testing purpose, it will be removed later)
            if self.output_params['plot']:
                fig, ax = plt.subplots(
                    2, 1, figsize=(8, 9), gridspec_kw={"height_ratios": [1, 1.5]}
                )
                fig.suptitle("Results at {} min".format(time_slice / 60))

                ax[0].plot(outlet_times, outlet_discharge, "-")
                ax[0].set_xlabel("Time elapsed (s)")
                ax[0].set_ylabel("discharge (cms)")
                ax[0].set_title("Water discharge at the outlet")

                imshow_grid(
                    self.model_grid,
                    "surface_water__depth",
                    cmap="Blues",
                    vmin=0,
                    vmax=1.2,
                    var_name="surface water depth (m)",
                )
                ax[1].set_title("")
                ax[1].set_xlabel('east-west distance (m)')
                ax[1].set_ylabel('north-south distance (m)')

                plt.close(fig)
                fig.savefig(os.path.join(output_folder, "flow_{}.png".format(time_slice)))

        # save outlet discharge
        outlet_result = pd.DataFrame(list(zip(outlet_times, outlet_discharge)),
                                     columns=['time', 'discharge'])
        outlet_result.to_csv(
            os.path.join(self.output_params['output_folder'] if os.path.isdir(self.output_params['output_folder']) else os.getcwd(),
                         'outlet_discharge.csv')
        )


if __name__ == "__main__":
    """Launch a model run.
    Command-line argument is the path of a configuration file (toml-format). 
    It should include sections for "input_params", "run_params", and "output_params". 
    """

    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        fs = FloodSimulator.from_file(config_file)
        fs.run()
    else:
        print('Please provide a configuration file path to run the model.')

