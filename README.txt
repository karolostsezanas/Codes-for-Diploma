Backscatter vol 2: Creates the contour plot of the backscatter with the y axis being the altitude and the x axis being the longitude/latitude.
You have to manually change the ranges you want the plot to be in. The colours are the same that nasa uses for their graphs.

Aerosol subtype vfm longitude: Creates the contour plot of the aerosol subtype with the y axis being tha altitude and the x axis being longitude/latitude.
It automatically reads the hdf files in the desired folder to create the plot. It also uses the same colours as nasa.

Layer 2: Finds the latitude/longitude for each grid point where there are aerosols detected, distinguishes the type of aerosol, and stores them into an excel file.
Unfortunately, due to errors in the data you may have to then check the plots of aerosol subtype since there can be noise or tiny particles which are counted but are not part
of the smoke layers.

Backscatter/Depolarization/Angstorm plot grid: Creates the plots each point in the grid were aerosols are detected (these are taken from the excel file that is created from
code Layer 2). The y axies is the altitude and the x axis is the corresponding backscatter/depolarization/angstrom. These can be used to easily create the statistics of each.
I haven't uploaded the code cause it is simple enough, but you can always contact me!

Fire maps: Different fire maps i created for Canada using modis data. Firemap is for a specific week. Fire map may-june is obviously all the fires from may-june.
fire map with trajectories takes the trajectories from the hdf files of calipso and plots them on top of the map.