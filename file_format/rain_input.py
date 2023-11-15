""" create grid rain input """
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

# constant rain tif #####################
# as geotiff
new_file = rasterio.open('rain_input_constant.tif',
                         'w',
                         driver='GTiff',
                         width=ori_dem.width,
                         height=ori_dem.height,
                         count=1,
                         crs=ori_dem.crs,
                         transform=ori_dem.transform,
                         dtype=np.float64,
                         nodata=-9999)
rain_rate = np.full((ori_dem.width,ori_dem.height), 59.2)   # mm/hr
new_file.write(rain_rate, 1)
new_file.close()

# spatial variable rain tif #####################
# as geotiff
# rain_input_small loc = 40
# rain_input_large loc = 57

new_file = rasterio.open('rain_input_large.tif',
                         'w',
                         driver='GTiff',
                         width=ori_dem.width,
                         height=ori_dem.height,
                         count=1,
                         crs=ori_dem.crs,
                         transform=ori_dem.transform,
                         dtype=np.float64,
                         nodata=-9999)

np.random.seed(123)
rain_rate = np.random.normal(loc=57, scale=0.5, size=(ori_dem.width, ori_dem.height))   # mm/hr
new_file.write(rain_rate, 1)
new_file.close()