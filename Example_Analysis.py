"""
## Orbit Maintenance 

---------------------------------------------------------
Atmospheric Drag Perturbation computation
[Ref] Larson & Werz - Sec. 6.2.3
Note: Rough estimation for near circular orbits. 

Inputs:
    'cd':  Standard drag coefficient
    'area': Effective cross-section  [m^2]
    'mass': Satellite mass [kg]
    'h': Circular hight [km]
"""

import constants as cts
import numpy as np
import matplotlib.pyplot as plt
from analytics import *
from space_env import Satellite, Propagator
from config import load_beomat_configuration


# #### Auxiliary Functions

def compute_sma(P):
    """
    Compute semimajor-axis from Period
    """
    P_seg = P*60
    return np.cbrt(P_seg*P_seg*cts.mu_e/(4*np.pi*np.pi))

def J2_RAAN_drift(a,e,i):
    """
    J2_RAAN_drift raw estimation of the drift of the Node
    when considering the J2 perturbation
    [Ref]  Larson & Wertz - pag 143
    :param a: semimajor-axis [km]
    :param e: eccentriticty
    :param i: inclination [deg]
    -----------------------------
    return OMEGA_drift [deg/day]
    """
    return -2.06474e14*a**(-7/2)*np.cos(i*cts.deg2rad)*(1-e)**(-2)

# ==========================================================================
#  Scenario
# ==========================================================================
all_satellites = load_beomat_configuration()
print(all_satellites)

SEGUIR ACA !!
#  Satellite Physical Properties (Manual or from Database) (or user Input)
sat_properties = {
    'cd': 2.2,      # Standard drag coefficient
    'area': 12.5,   # m^2 (Effective cross-section)
    'mass': 450.0,   # kg
    'h': 450.0      # km
}

atmparams = {
    'cd': sat_properties['cd'],
    'area': sat_properties['area'],
    'mass': sat_properties['mass'],
    'h': sat_properties['h'],
    'a': cts.Re + sat_properties['h']
}

#  Decay and Lifetime computation

da_rev =drag_decay_per_rev(atmparams)
life_time = estimate_lifetime(atmparams)
print(f'Decay in every revolution: {np.round(da_rev,4)} Km' )
print(f'Life Time: {np.round(life_time,4)} days' )

# ==========================================================================
# Propagation in GMAT
# ==========================================================================
# Once we know the life time in days, we can propagate in GMAT to show decay. 

sat = Satellite("Freefall")
sat.set_keplerian(
    sma=cts.Re + sat_properties['h'], 
    ecc=0.0001, 
    inc=98.2, 
    raan=0, 
    aop=0, 
    ta=0
)
print(f"Satelite '{sat.name}' configurado.")
# Force Models
config_leo = {
    'gravity': 'Earth',
    'degree': 2,    # J2
    'order': 0,
    'drag': True    # Atmpospheric Drag
}
# GMAT Propagator 
prop = Propagator("MyPropagator", config=config_leo)
# Propagation time
duration_sim = life_time+2 # [days]
duration_sim = duration_sim*cts.secinday # [sec]
print("Runnig propagation...")
# trajectory -> numpy: [tiempo, x, y, z]
trajectory = prop.run(sat, duration_sec=duration_sim, step_size=600)
print(f"Finished!")
# Compute semimajor axis to plot
time = trajectory[:, 0]
# r = sqrt(x^2 + y^2 + z^2)
r = np.linalg.norm(trajectory[:, 1:], axis=1)
# Matrix(N, 2)
radius= np.column_stack((time, r))
print(f'First Orbit radius ri: {radius[0][1]}')
print(f'Last Orbit radius rf: {radius[0][1]}')

# ===========================
#  Repeating Ground Track
# ===========================
# Definition from book
# k_rev = 16 # revolutions
# P=cts.min_sidereal_day/k_rev # [min]
# sma = compute_sma(P)
# hp=120.0 # [km]
# i=45  # [deg]
# r_a= 2*compute_sma(P)-(hp+cts.Re)
# b = np.sqrt(r_a*(hp+cts.Re))
# e = np.sqrt(1-(b*b/(sma*sma)))
# # RAAN drift
# Ome_dot = J2_RAAN_drift(sma,e,i)

# # Period computation iteration
# P_ini = P

# sma = compute_sma(P_ini)
# r_a= 2*sma-(hp+cts.Re)
# b = np.sqrt(r_a*(hp+cts.Re))
# e = np.sqrt(1-(b*b/(sma*sma)))
# Ome_dot = J2_RAAN_drift(sma,e,i) # [deg/day]
# Ome_dot_min = Ome_dot/1440 # [deg/min]
# # cuantos minutos le llevo a Tierra recorrer el Delta de RAAN 
# Delta_period = Ome_dot_min*P_ini/cts.earth_angular_velocity
# P_new = P_ini + Delta_period
# P_ini = P_new 

# sma1 = compute_sma(P_ini)
# # New P
# print (f'New Period: {np.round(P_ini,4)} and New sma: {np.round(sma1,4)}')
