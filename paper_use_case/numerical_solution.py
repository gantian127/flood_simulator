"""
keep track of testing code
"""
from landlab.io import read_esri_ascii
from landlab import imshow_grid
from landlab.components import OverlandFlow

import matplotlib.pyplot as plt
import pandas as pd

# load dem data
grid_file = './paper_use_case/flat_domain.asc'
model_grid, dem_data = read_esri_ascii(grid_file, name='topographic__elevation')

# add surface waer depth
model_grid.add_full("surface_water__depth", 1e-12)

# set model boundary
# remember to set the close boundary (status number as 4)
# remember to set the left boundary as fixed value not fixed gradient.
model_grid.status_at_node[model_grid.nodes_at_left_edge] = model_grid.BC_NODE_IS_FIXED_VALUE
model_grid.status_at_node[model_grid.nodes_at_right_edge] = model_grid.BC_NODE_IS_CLOSED
model_grid.status_at_node[model_grid.nodes_at_top_edge] = model_grid.BC_NODE_IS_CLOSED
model_grid.status_at_node[model_grid.nodes_at_bottom_edge] = model_grid.BC_NODE_IS_CLOSED

# set model parameters
mannings_n = 0.01  # manning's n
u = 0.4  # constant velocity at boundary m/s
alpha = 0.7
theta = 0.8  # [0.8, 0.9, 1]
steep_slopes = False

model_run_time = 9000  # sec
elapsed_time = 0.0

# instantiate overland flow component
overland_flow = OverlandFlow(model_grid,
                             steep_slopes=steep_slopes,
                             alpha=alpha,
                             mannings_n=mannings_n,
                             theta=theta,
                             )


# run model
result_df = pd.DataFrame(columns=['t', 'model_h0', 'dt'])

while elapsed_time <= model_run_time:
    overland_flow.dt = overland_flow.calc_time_step()
    if overland_flow.dt > 10:
        overland_flow.dt = 10
    elapsed_time += overland_flow.dt
    h0 = ((7 / 3) * (mannings_n ** 2) * (u ** 3) * elapsed_time) ** (3 / 7)
    new_row = [elapsed_time, h0, overland_flow.dt]
    result_df.loc[len(result_df.index)] = new_row

    #model_grid.at_link["surface_water__discharge"][model_grid.fixed_links] = u * h0
    link_list = [links[0] for links in model_grid.links_at_node[model_grid.nodes_at_left_edge]]
    model_grid.at_link['surface_water__discharge'][link_list] = u*h0

    node_list = [item for sublist in model_grid.nodes_at_link[model_grid.fixed_links]
                 for item in sublist]
    model_grid.at_node["surface_water__depth"][node_list] = h0
    model_grid.at_node['surface_water__depth'][model_grid.nodes_at_left_edge] = h0

    overland_flow.run_one_step(dt=overland_flow.dt)
    # node_list = [item for sublist in model_grid.nodes_at_link[model_grid.fixed_links]
    #              for item in sublist]
    # model_grid.at_node["surface_water__depth"][node_list] = h0


# show results
# 2D grid plot
imshow_grid(model_grid, 'surface_water__depth',
            plot_name='Surface water depth in 2D grid')

# hx plot
model_result = model_grid.at_node['surface_water__depth'].reshape(32, 240)
hx_df = pd.read_csv('./paper_use_case/analytical_hx_result.csv', index_col=0)
hx_df['model_hx_row16'] = model_result[15, 0:145]
hx_df['model_hx_row29'] = model_result[28, 0:145]
hx_df['model_hx_row5'] = model_result[4, 0:145]
hx_df.plot(x='x', title='Surface water depth in 1D', style='o', markersize=2)

# h0 plot
h0_df = pd.read_csv('./paper_use_case/analytical_h0_result.csv', index_col=0)
fig, ax = plt.subplots()
result_df.plot(x='t', y='model_h0', ax=ax, style='o', markersize=2)
h0_df.plot(x='t', ax=ax, style='o', markersize=2)


