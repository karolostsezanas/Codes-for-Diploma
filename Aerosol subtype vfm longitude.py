import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from pyhdf.SD import SD, SDC

FILE_NAME = 'D:/CALIPSO/VFM SMOKE/19_1_VFM.hdf'

# Identify the data field.
DATAFIELD_NAME = 'Feature_Classification_Flags'

# Open the HDF file
hdf = SD(FILE_NAME, SDC.READ)

# Read dataset
data2D = hdf.select(DATAFIELD_NAME)
data = data2D[:, :]

# Read geolocation datasets
latitude = hdf.select('Latitude')
lat = latitude[:, 0]

longitude = hdf.select('Longitude')
lon = longitude[:, 0]

# Function to find index range for longitude range
def find_longitude_indices(longitudes, lon_min, lon_max):
    indices = np.where((longitudes >= lon_min) & (longitudes <= lon_max))[0]
    if len(indices) == 0:
        raise ValueError("No longitudes found in the specified range.")
    return indices[0], indices[-1]

# Set longitude range
lon_min = -120.0  # Set your minimum longitude here
lon_max = -109.0  # Set your maximum longitude here

# Find indices for the longitude range
lidx1, lidx2 = find_longitude_indices(lon, lon_min, lon_max)

# Subset latitude and longitude values for the region of interest
lat = lat[lidx1:lidx2 + 1]
lon = lon[lidx1:lidx2 + 1]
size = lat.shape[0]

N = 290    # 290 is sample number of low height data: -0.5km to 8.2km @ 30m
sidx = data.shape[1] - N * 15
data2d = data[lidx1:lidx2 + 1, sidx:]
data3d = np.reshape(data2d, (size, 15, N))
data_l = data3d[:, 0, :]

N1 = 200   # height data: 8.2 to 20.2 km @ 60m
sidx1 = sidx - N1 * 5
data2d = data[lidx1:lidx2 + 1, sidx1:sidx]
data3d = np.reshape(data2d, (size, 5, N1))
data_m = data3d[:, 0, :]
data_m1 = np.zeros([data_m.shape[0], data_m.shape[1] * 2], dtype='int')
data_m1[:, ::2] = data_m
data_m1[:, 1::2] = data_m

N2 = 55   # height data: 20.2 to 30.1km @ 180m
sidx2 = sidx1 - N2 * 3
data2d = data[lidx1:lidx2 + 1, sidx2:sidx1]
data3d = np.reshape(data2d, (size, 3, N2))
data_m = data3d[:, 0, :]
data_m2 = np.zeros([data_m.shape[0], data_m.shape[1] * 6], dtype='int')
for i in range(6):
    data_m2[:, i::6] = data_m

data = np.concatenate([data_m2, data_m1, data_l], axis=1)
# Rotate data to correct the orientation
data = np.rot90(data, 1)
data = np.flipud(data)

# Feature type
ft = data & 7

# Aerosol type
a = data >> 9
# tropospheric aerosol
atype = a & 7
atype[ft != 3] = 0
# stratospheric aerosol
btype = a & 7
btype[ft != 4] = 0
# combine
btype = btype + 8
btype[btype == 8] = 0
btype[btype > 3 + 8] = 0
atype = atype + btype

# Generate altitude data according to file specification
alt = np.zeros(N + N1 * 2 + N2 * 6)
for i in range(N + N1 * 2 + N2 * 6):
    alt[i] = -0.5 + i * 0.03

# X axis ticks
xvals = []
xstrs = []
nx = atype.shape[1]
for i in range(0, nx, 100):
    xvals.append(i)
    if i == 0:
        xstrs.append('Lat: %.2f\nLon: %.2f' % (lat[i], lon[i]))
    else:
        xstrs.append('%.2f\n%.2f' % (lat[i], lon[i]))

# Convert colors to 0-1 range
def convert_color(color):
    return tuple(c / 255.0 for c in color)

cols = [
    convert_color((204, 204, 204)), convert_color((0, 0, 255)), convert_color((255, 240, 0)), 
    convert_color((255, 153, 0)), convert_color((51, 153, 0)), convert_color((120, 51, 0)), 
    'k', convert_color((0, 153, 204)), 'w', convert_color((150, 150, 150)), convert_color((100, 100, 100))
]

# Plot
fig, ax = plt.subplots()
levs = np.arange(11)
cmap = colors.ListedColormap(cols)
norm = mpl.colors.BoundaryNorm(levs, cmap.N)

im = ax.imshow(atype, aspect='auto', cmap=cmap, norm=norm, extent=[0, nx - 1, alt[0], alt[-1]])

cbar = plt.colorbar(im, ax=ax, shrink=0.8, ticks=levs)
cbar.ax.set_yticklabels(['Not Determined', 'Clean Marine', 'Dust', 'Polluted Cont.', 'Clean Cont.', 
                         'Polluted Dust', 'Smoke', 'Dusty marine', 'PSC aerosol', 'Volcanic ash', 'Sulfate/other'])

ax.set_xticks(xvals)
ax.set_xticklabels(xstrs, fontsize=8)
ax.set_ylabel('Altitude (km)')
ax.set_ylim(-0.5, 10.1)
ax.set_title(f'{os.path.basename(FILE_NAME)}\nAerosol types')

plt.show()
