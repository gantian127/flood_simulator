"""
Code used to convert the file format for model input/output
"""

import rasterio
import numpy as np
import os
from landlab.io import read_esri_ascii
from landlab import imshow_grid, RasterModelGrid
import pandas as pd

# change working dir
os.chdir('/Users/tiga7385/Desktop/flood_simulator/file_format')

# read data #####################
# read ori dem
ori_dem = rasterio.open('ori_DEM.tif')
ori_dem_1d = ori_dem.read(1).flatten()

# read max depth
max_depth_grid, max_depth_1d = read_esri_ascii('max_water_depth.asc')

# read watershed dem
watershed_dem, watershed_dem_1d = read_esri_ascii('geer_canyon.txt')

# export data watershed_dem #####################
# as geotiff
wateshed_dem_2D = watershed_dem_1d.reshape(158, 223)
wateshed_dem_2D_flip = np.flip(wateshed_dem_2D, axis=0)
new_file = rasterio.open('geer_canyon.tif',
                         'w',
                         driver='GTiff',
                         width=ori_dem.width,
                         height=ori_dem.height,
                         count=1,
                         crs=ori_dem.crs,
                         transform=ori_dem.transform,
                         dtype=wateshed_dem_2D_flip.dtype,
                         nodata=-9999)

new_file.write(wateshed_dem_2D_flip, 1)
new_file.close()

# export data max_depth #########################
# as geotiff
max_depth_2D = max_depth_1d.reshape(158, 223)
max_depth_2D_flip = np.flip(max_depth_2D, axis=0)

new_file = rasterio.open('max_water_depth.tif',
                         'w',
                         driver='GTiff',
                         width=ori_dem.width,
                         height=ori_dem.height,
                         count=1,
                         crs=ori_dem.crs,
                         transform=ori_dem.transform,
                         dtype=max_depth_2D_flip.dtype,
                         nodata=-9999)

new_file.write(max_depth_2D_flip, 1)
new_file.close()

# as csv with Z value
DF = pd.DataFrame(max_depth_1d, columns=['z_value'])
DF.to_csv('max_water_depth.csv')

# show grid data ######################
grid = RasterModelGrid((158, 223))
# value start from upper lat (need flip alone xaxis)
grid.add_field('ori_dem', ori_dem_1d, at='node', clobber=True)
imshow_grid(grid, 'ori_dem')
# value start from lower lat
grid.add_field('max_depth', max_depth_1d, at='node', clobber=True)
imshow_grid(grid, 'max_depth')
# value start from upper
grid.add_field('max_depth_flip', max_depth_2D_flip, at='node', clobber=True)
imshow_grid(grid, 'max_depth_flip')