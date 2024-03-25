"""
This is used to create the domain file
all units in meter
"""
import numpy as np

# define header info
elevation = 10

nrows = 32
ncols = 240
cellsize = 25
xllcorner = 0
yllcorner = 0

# Define the data (example elevation data)
data = np.empty([nrows, ncols])
data[:] = elevation

# Open a new text file
with open('./paper_use_case/flat_domain.asc', 'w') as f:
    # Write header information
    f.write(f'ncols {ncols}\n')
    f.write(f'nrows {nrows}\n')
    f.write(f'xllcorner {xllcorner}\n')
    f.write(f'yllcorner {yllcorner}\n')
    f.write(f'cellsize {cellsize}\n')

    # Write data values
    for row in data:
        f.write(' '.join(map(str, row)) + '\n')

print("Esri ASCII file has been generated.")

