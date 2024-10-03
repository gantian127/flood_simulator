"""
keep track of testing code
"""
import numpy as np
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
theta = 0.8 # [0.8, 0.9, 1]
steep_slopes = False

model_run_time = 9000+6000  # sec
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
discharge_input = pd.DataFrame(columns=['t', 'discharge', 'dt'])

while elapsed_time <= model_run_time:
    overland_flow.dt = overland_flow.calc_time_step()

    # needs to set a limit to avoid too large time step at the beginning
    if overland_flow.dt > 10:
        overland_flow.dt = 10
    elapsed_time += overland_flow.dt

    # store h0 result at each time step
    h0 = ((7 / 3) * (mannings_n ** 2) * (u ** 3) * elapsed_time) ** (3 / 7)
    new_row = [elapsed_time, h0, overland_flow.dt]
    result_df.loc[len(result_df.index)] = new_row

    # assign water input data at left edge for node and link
    link_list = [links[0] for links in model_grid.links_at_node[model_grid.nodes_at_left_edge]]
    model_grid.at_link['surface_water__discharge'][link_list] = u*h0
    model_grid.at_node['surface_water__depth'][model_grid.nodes_at_left_edge] = h0

    # store discharge input at each time step
    discharge = overland_flow.discharge_mapper(
        model_grid.at_link["surface_water__discharge"],
        convert_to_volume=True
    )

    # the left edge node discharge value is 0,
    # because discharge_mapper only calculates water that flows
    # into the node as discharge result. So the discharge next to the left edge node
    # is representing the discharge input.
    discharge_left_node = discharge.reshape(32, 240)[15, 1]
    discharge_input.loc[len(result_df.index)] = [elapsed_time, discharge_left_node, overland_flow.dt]

    # run model
    overland_flow.run_one_step(dt=overland_flow.dt)

# show results
# 2D grid plot
fig = plt.figure(figsize=(10, 3))
ax = plt.gca()
imshow_grid(model_grid, 'surface_water__depth',
            plot_name=f'Surface water depth in 2D grid')
fig.savefig('./paper_use_case/2D_plot.png')

# hx plot
hx_df = pd.read_csv('./paper_use_case/analytical_hx_result.csv', index_col=0)
model_result = model_grid.at_node['surface_water__depth'].reshape(32, 240)
model_hx_df = pd.DataFrame(columns=['x', 'hx'])
model_hx_df['x'] = np.arange(0, 240*25, 25)
model_hx_df[f'model_hx_{theta}'] = model_result[15, 0:240]

fig, ax = plt.subplots()
hx_df.plot(x='x', title='Surface water depth in 1D', style='o', markersize=2, ax=ax)
model_hx_df.plot(x='x', style='o', markersize=2, ax=ax)
fig.savefig(f'./paper_use_case/model_hx_{theta}.png')
model_hx_df.to_csv(f'./paper_use_case/model_hx_{theta}.csv')

# h0 plot
h0_df = pd.read_csv('./paper_use_case/analytical_h0_result.csv', index_col=0)
fig, ax = plt.subplots()
result_df.plot(x='t', y='model_h0', ax=ax, style='o', markersize=2)
h0_df.plot(x='t', ax=ax, style='o', markersize=2)
fig.savefig('./paper_use_case/h0_result.png')
result_df.to_csv('./paper_use_case/model_h0_result.csv')


# discharge input at left edge
fig, ax = plt.subplots()
discharge_input.plot(x='t', y='discharge', ax=ax, style='o', markersize=2)
plt.title('Discharge(cms) input at left boundary')
fig.savefig('./paper_use_case/model_h0_discharge.png')

fig, ax = plt.subplots()
discharge_input['vol_input'] = discharge_input['discharge'] * discharge_input['dt']
discharge_input['acc_vol_input'] = discharge_input['vol_input'].cumsum()
discharge_input.plot(x='t', y='acc_vol_input', ax=ax, style='o', markersize=2)
plt.title('Total water volume input for one node at the left boundary')
fig.savefig('./paper_use_case/model_h0_discharge_total.png')
discharge_input.to_csv('./paper_use_case/model_h0_discharge.csv')

# discharge result in a row
hx_discharge = pd.DataFrame(columns=['x', 'discharge'])
hx_discharge['discharge'] = discharge.reshape(32, 240)[15, 1:145]
hx_discharge['x'] = np.arange(25, 145*25, 25)

fig, ax = plt.subplots()
hx_discharge.plot('x', 'discharge', ax=ax, style='o', markersize=2 )
plt.title('Discharge(cms) result at a row')
fig.savefig(f'./paper_use_case/model_hx_discharge_{theta}.png')
hx_discharge.to_csv(f'./paper_use_case/model_hx_discharge_{theta}.csv')

# discharge result as a grid
fig = plt.figure(figsize=(10, 3))
ax = plt.gca()
imshow_grid(model_grid, discharge,
            plot_name=f'Discharge(cms) in 2D grid')
fig.savefig('./paper_use_case/model_hx_discharge_2D.png')