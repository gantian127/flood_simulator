"""
This code is used to create the analytical solution for the use case
"""
import numpy as np
import pandas as pd


# define functions
def calculate_hx(x, n, u, t):
    hx = ((-7/3) * (n**2 * u**2 * (x-u*t))) ** (3/7)

    return hx


def calculate_h0(t, n, u):
    h0 = ((7 / 3) * (n ** 2) * (u ** 3) * t) ** (3 / 7)

    return h0


# set parameters
t = 9000
u = 0.4
n = 0.01
dx = 25

# result for hx at t=9000 ###############
# define dataframe
df = pd.DataFrame(columns=['x','hx'])
df['x'] = np.arange(0, u*t+dx, dx)
df['hx'] = df['x'].apply(calculate_hx, args=(n, u, t))

# make plot
df.plot(x='x', y='hx')

# save result
df.to_csv('./paper_use_case/analytical_hx_result.csv')


# result for h0 at t = [0,9000] #############
# define dataframe
df2 = pd.DataFrame(columns=['t', 'h0'])
dt = 50
df2['t'] = np.arange(0, t+dt, dt)
df2['h0'] = df2['t'].apply(calculate_h0, args=(n, u))

# make plot
df2.plot(x='t', y='h0')

# save result
df2.to_csv('./paper_use_case/analytical_h0_result.csv')
