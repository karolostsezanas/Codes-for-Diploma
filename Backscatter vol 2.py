import numpy as np
import matplotlib.pyplot as plt
from pyhdf.SD import SD, SDC
from pyhdf.HDF import HDF
from pyhdf.VS import VS
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
from scipy.interpolate import griddata
import os

# List of colors and corresponding backscatter values
cmap_colors = [
    ('#002aaa', 1.00E-04), ('#002aaa', 2.00E-04), ('#007fff', 3.00E-04), ('#007fff', 4.00E-04),
    ('#007fff', 5.00E-04), ('#007fff', 6.00E-04), ('#007fff', 7.00E-04), ('#00ffaa', 8.00E-04),
    ('#007f7f', 9.00E-04), ('#00aa55', 1.00E-03), ('#ffff00', 1.50E-03), ('#ffff00', 2.00E-03),
    ('#ffd400', 2.50E-03), ('#ffaa00', 3.00E-03), ('#ff7f00', 3.50E-03), ('#ff5500', 4.00E-03),
    ('#ff0000', 4.50E-03), ('#ff2a55', 5.00E-03), ('#ff557f', 5.50E-03), ('#ff7faa', 6.00E-03),
    ('#464646', 6.50E-03), ('#646464', 7.00E-03), ('#828282', 7.50E-03), ('#9b9b9b', 8.00E-03),
    ('#b4b4b4', 1.00E-02), ('#c8c8c8', 2.00E-02), ('#e1e1e1', 3.00E-02), ('#ebebeb', 4.00E-02),
    ('#f0f0f0', 5.00E-02), ('#f2f2f2', 6.00E-02), ('#f5f5f5', 7.00E-02), ('#f9f9f9', 8.00E-02),
    ('#fdfdfd', 9.00E-02), ('#ffffff', 1.00E-01)
]

# Create a custom colormap
colors_list = [color for color, value in cmap_colors]
values = [value for color, value in cmap_colors]
custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', colors_list, N=len(colors_list))

# Ensure the values are in ascending order for BoundaryNorm
values = sorted(values)
norm = BoundaryNorm(values, custom_cmap.N)

# Load the HDF4 file
FILE_NAME = 'D:/CALIPSO/L1 SMOKE/22_2_L1.hdf'
hdf = HDF(FILE_NAME)
vs = hdf.vstart()

# Retrieve the altitude data
xid = vs.find('metadata')
altid = vs.attach(xid)
altid.setfields('Lidar_Data_Altitudes')
nrecs, _, _, _, _ = altid.inquire()
altitude_data = altid.read(nRec=nrecs)
altid.detach()

# Convert altitude data to a numpy array
altitude = np.array(altitude_data[0][0])

# Load the scientific data set
sd = SD(FILE_NAME, SDC.READ)
total_backscatter_data = sd.select('Total_Attenuated_Backscatter_532')
total_backscatter = total_backscatter_data[:]

# Read geolocation datasets
latitude_data = sd.select('Latitude')
latitude = latitude_data[:]
longitude_data = sd.select('Longitude')
longitude = longitude_data[:]

# Ensure latitude and total_backscatter are aligned
min_length = min(len(latitude), total_backscatter.shape[0])
latitude = latitude[:min_length]
longitude = longitude[:min_length]
total_backscatter = total_backscatter[:min_length, :]

# Reshape latitude and longitude if needed
if latitude.ndim > 1:
    latitude = latitude.squeeze()
if longitude.ndim > 1:
    longitude = longitude.squeeze()

# Filter altitude to be within 0 to 10 km
altitude_filter = altitude <= 10
altitude = altitude[altitude_filter]
total_backscatter = total_backscatter[:, altitude_filter]

# Filter data based on the specified longitude range
lon_filter = (longitude >= -106.0) & (longitude <= -98.0)
latitude = latitude[lon_filter]
longitude = longitude[lon_filter]
total_backscatter = total_backscatter[lon_filter, :]

# Mask the missing data and set the background to dark blue
masked_backscatter = np.ma.masked_where(total_backscatter == 0, total_backscatter)

# Interpolate data on a regular grid
x1, x2 = 0, len(latitude)
nx = x2 - x1
h1, h2 = 0, 10  # km
nz = 500  # Number of pixels in the vertical
x = np.arange(x1, x2)
h = np.linspace(h2, h1, nz)
grid_x, grid_h = np.meshgrid(x, h)
points = np.array([(i, alt) for i in range(total_backscatter.shape[0]) for alt in altitude])
values = total_backscatter.flatten()
data = griddata(points, values, (grid_x, grid_h), method='linear')

# X axis ticks
xvals = []
xstrs = []
for i in range(0, nx, 800):  # Increase step size for less frequent ticks
    xvals.append(i + x1)
    if i == 0:
        xstrs.append('Lat: %.2f\nLon: %.2f' % (latitude[i], longitude[i]))
    else:
        xstrs.append('%.2f\n%.2f' % (latitude[i], longitude[i]))

# Plot
plt.figure(figsize=(15, 8))
layer = plt.imshow(data, aspect='auto', extent=[x1, x2, h1, h2], cmap=custom_cmap, interpolation='bilinear', norm=norm)
cbar = plt.colorbar(layer, extend='both', ticks=[1.00E-01, 1.00E-02, 1.00E-03, 1.00E-04])
cbar.ax.set_yticklabels(['1.00E-01', '1.00E-02', '1.00E-03', '1.00E-04'])
cbar.set_label(r'$\rm{km}^{-1} \rm{sr}^{-1}$')
plt.xticks(xvals, xstrs)
plt.ylabel('Altitude (km)')
basename = os.path.basename(FILE_NAME)
plt.title(f'{basename}\nTotal_Attenuated_Backscatter_532')

plt.show()
