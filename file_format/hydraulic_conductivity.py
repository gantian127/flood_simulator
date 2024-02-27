""" prepare hydraulic conductivity input"""

import rasterio
import numpy as np
import os

# change working dir
os.chdir('/Users/tiga7385/Desktop/flood_simulator/file_format')

# read dem data #####################
# read ori dem
ori_dem = rasterio.open('ori_DEM.tif')
ori_dem_1d = ori_dem.read(1).flatten()

# constant rain tif #####################
new_file = rasterio.open('hydr_cond_constant.tif',
                         'w',
                         driver='GTiff',
                         width=ori_dem.width,
                         height=ori_dem.height,
                         count=1,
                         crs=ori_dem.crs,
                         transform=ori_dem.transform,
                         dtype=np.float64,
                         nodata=-9999)
cond_rate = np.full((ori_dem.width, ori_dem.height), 1.0e-7)   # mm/hr
new_file.write(cond_rate, 1)
new_file.close()


# wildfire impacted tif #####################
new_file = rasterio.open('hydr_cond_wildfire.tif',
                         'w',
                         driver='GTiff',
                         width=ori_dem.width,
                         height=ori_dem.height,
                         count=1,
                         crs=ori_dem.crs,
                         transform=ori_dem.transform,
                         dtype=np.float64,
                         nodata=-9999)

cond_rate = np.full((ori_dem.width, ori_dem.height), 1.0e-7)   # mm/hr

# get x, y index values
x = np.arange(0, ori_dem.height)
y = np.arange(0, ori_dem.width)

# mask 1
cx = int(ori_dem.height/2)
cy = int(ori_dem.width/2)
r = 30
mask1 = (x[np.newaxis, :]-cx)**2 + (y[:, np.newaxis]-cy)**2 < r**2
cond_rate[mask1] = 1.0e-8

# mask2
cx = int(ori_dem.height/2.5)
cy = int(ori_dem.width/1.5)
r = 15
mask2 = (x[np.newaxis, :]-cx)**2 + (y[:,np.newaxis]-cy)**2 < r**2

cond_rate[mask2] = 1.0e-8

new_file.write(cond_rate, 1)
new_file.close()