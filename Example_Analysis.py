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
from visualizer import graficar_2d_plotly


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

""" inputs """
sat_name = "SAOCOM 1-A"
#sat_noradId = 43641

all_satellites = load_beomat_configuration()
if sat_name: 
    search_value = sat_name
elif sat_noradId:
    search_value = sat_noradId  

# Satellite Dictionary
selected_sat = next(
    (sat for sat in all_satellites 
     if str(sat.get('norad_id')) == str(search_value) 
     or sat.get('name', '').lower() == str(search_value).lower()), 
    None
)

if selected_sat:
    print(f"Satellite LOADED: {selected_sat['name']}")
else:
    print(f"Satellite NOT FOUND")

# Instanciamos el satelite (esto crea el objeto Spacecraft en GMAT)
sat = Satellite(selected_sat['name'])

sat.set_keplerian(
    sma=selected_sat['altitude'] + cts.Re, 
    ecc=selected_sat['eccentricity'], 
    inc=selected_sat['inclination'], 
    raan=0, 
    aop=0, 
    ta=0
)

atmparams = {
    'cd': 2.2,
    'area':  selected_sat['Area'],
    'mass': selected_sat['mass'],
    'h': selected_sat['altitude'],
    'a': cts.Re + selected_sat['altitude']
}

#  Analytic DECAY and LIFETIME computation

da_rev =drag_decay_per_rev(atmparams)
life_time = estimate_lifetime(atmparams)
print(f'Decay in every revolution: {np.round(da_rev,4)} Km' )
print(f'Life Time: {np.round(life_time,4)} days' )

# ==========================================================================
# Propagation in GMAT
# ==========================================================================
# Once we know the life time in days, we can propagate in GMAT to show decay. 

# Force Models
config_leo = {
    'gravity': 'Earth',
    'degree': 2,    # J2
    'order': 0,
    'drag': True    # Atmpospheric Drag
}
# GMAT Propagator - Propagate 1 Orbit
prop = Propagator("MyPropagator", config=config_leo)
duration_sim =  sat.get_keplerian_period()# [sec]
print("Runnig propagation...")
# trajectory -> numpy: [tiempo, x, y, z]
trajectory = prop.run(sat, duration_sec=duration_sim, step_size=600)
# Ground Track 2D
fig_2d = graficar_2d_plotly(trajectory)
fig_2d.show()

COVERAGE --> SEGUIR ACA
# ===========================
#  Repeating Ground Track
# ===========================
# Definition from book
P = sat.get_keplerian_period()
k_rev = int(86160/P) # revolutions
r_a= 2*sat.sma-(selected_sat['altitude']+cts.Re)
b = np.sqrt(r_a*(selected_sat['altitude']+cts.Re))
e = selected_sat['eccentricity'] 
# # RAAN drift
Ome_dot = J2_RAAN_drift(sat.sma,e,selected_sat['inclination']) # [deg/day]
P_ini = P
# # cuantos minutos le llevo a Tierra recorrer el Delta de RAAN 
Delta_period = Ome_dot_min*P_ini/cts.earth_angular_velocity
# P_new = P_ini + Delta_period
# P_ini = P_new 

# sma1 = compute_sma(P_ini)
# # New P
# print (f'New Period: {np.round(P_ini,4)} and New sma: {np.round(sma1,4)}')
