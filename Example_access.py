'''
Created on Apr 03, 2026

Module to compute access to Ground Stations
! note: Requires conextion to downlaod Leap_Second.dat from IERS. 

@author: mcvalenti
'''

import numpy as np
import matplotlib.pyplot as plt
from space_env import Satellite, Propagator
from visualizer import plot_ground_track, graficar_2d_plotly, plot_ground_track_with_access
import constants as cts
from datetime import time
from astropy.time import Time
import ground_segment as gs
import access_manager as am

#====================
# ORBIT
#====================
# LEO orbit circular
h = 550 # km
LTAN = time(9,0,0)
Lon_RAAN= LTAN.hour*15 # [deg/hs]
# GMAT Spacecraft creation
sat = Satellite("Salta")
sat.set_keplerian(
    sma=cts.Re + h, 
    ecc=0.0001, 
    inc=98.2, 
    raan=Lon_RAAN, 
    aop=0, 
    ta=0
)
print(f"Satellite '{sat.name}' configured.")

#====================
# FORCE MODELS
#====================
config_leo = {
    'gravity': 'Earth',
    'degree': 2,    # Activa J2
    'order': 0,
    'drag': True    # Atmospheric Drag
}

#====================
# SIMULATION
#====================
# GMAT Propagator creation
prop = Propagator("MyPropagator", config=config_leo)
# 5 hours 
duracion_sim = 5 * 3600  # [sec]
print("Propagating ...")
# Esto devuelve un array de numpy: [tiempo, x, y, z]
trajectory = prop.run(sat, duration_sec=duracion_sim, step_size=60)
print(f" Ready -  {trajectory.shape[0]} data points available")

#====================
# ANALYSIS & REPORTS
#====================
# Acces Analysis 
# Sites
salta_site = gs.Site("Salta",-24.7851,-65.39939, 1200)
# bsas = gs.Site("BuenosAires", -34.6, -58.48, 25)
# matera = gs.Site("Matera", 40.66, 16.6, 100)
# Access objects
acc1 = am.AccessManager()
astropy_time_start = Time("2026-02-10T12:00:00", format='isot', scale='utc')
access_salta= acc1.calculate_access(trajectory, astropy_time_start, salta_site)


#====================
# VISUALIZATION
#====================
# 3D
figura = plot_ground_track(trajectory, epoch="2026-02-10T12:00:00")
figura.show()
# Ground Track
fig_2d = graficar_2d_plotly(trajectory, epoch="2026-02-10T12:00:00")
fig_2d.show()
# Access visualization
visual_data = [{'site': salta_site, 'passes': access_salta}]
fig = plot_ground_track_with_access(trajectory, astropy_time_start, visual_data)
fig.show()

