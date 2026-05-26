'''
Created on 20 Apr. 2026

@author: mvalenti
'''

import numpy as np
from astropy.time import Time
import astropy.units as u

deg2rad=np.pi/180.0
omega_earth = 15.041067 # [deg/hour]

def launch_azimuth(orb_inc,  site_lat, launch_dir):
    """
    Compute Site Launch Azimuth (Beta)
    orb_inc: inclination of the desired orbit [deg]
    site_lat: Latitude of the Launch Site [deg]
    """
    beta0 = np.arcsin(np.cos(orb_inc*deg2rad)/np.cos(site_lat*deg2rad))

    if launch_dir == 'ASC':
        beta = beta0 if beta0 > 0 else 2*np.pi+beta0
    elif launch_dir == 'DESC':
        beta = np.pi - beta0
    return beta

def longitude_nearest(site_azimuth, orb_inc):
    """
    Compute the angle in the equatorial plane from the Ascending node 
    to the longitude of the launch site (delta) - [Wertz]
    """
    return np.arccos(np.cos(site_azimuth*deg2rad)/np.sin(orb_inc*deg2rad))

def gmst_launch(RAAN, long_near, site_lon):
    """
    Site sidereal time for the launch windows
    """
    return RAAN+long_near-site_lon


# Space X - Launch Site (Vandenberg)
lat_site = 34.633 # [deg]
lon_site = -120.613 # [deg]
h_site = 0.112 # [m]

# Orbit Configuration
orb_inc = 97.4 # [deg]

# Scenario
launch_direction='DESC' # ['ASC' or 'DESC']
date_str= '2027-01-27 00:00:00'
t0hs=Time(date_str, scale='utc')

Beta=launch_azimuth(orb_inc,lat_site, launch_direction)
delta=longitude_nearest(Beta/deg2rad, orb_inc)
RAAN = 120.0
gmst_launch = gmst_launch(RAAN, delta/deg2rad, lon_site)
gmst0hs = t0hs.sidereal_time('mean', 'greenwich')
gmst0hs_deg = gmst0hs.deg
delta_gmst = (gmst_launch - gmst0hs_deg) % 360
ut_hours = delta_gmst / omega_earth
print('============')
print ('RESULTS')
print('============')
print (f'Launch Azimut Beta: {np.round(Beta/deg2rad,2)}')
print (f'Longitude angle from the nearest node to the site, delta: {delta/deg2rad}')
print(f'GMST Launch: {gmst_launch}')
print(f'GMST 0hs: {gmst0hs_deg}')
print(f'Delta GMST: {delta_gmst}')
print (f'Launch UT: {np.round(ut_hours,2)}')
