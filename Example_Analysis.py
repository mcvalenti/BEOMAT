"""
## Orbit Maintenance 
TO DO REVIEW DESCRIPTION
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

# ==========================================================================
#  Scenario - Load from DB or input a new satellite
# ==========================================================================

""" inputs """
sat_name = "SAOCOM 1-A"
#sat_noradId = 43641

all_satellites = load_beomat_configuration() # from config
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


# Load a GMAT Satellite from input data
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

""" Theoretical Analysis """
#  Analytic DECAY and LIFETIME computation

da_rev =drag_decay_per_rev(atmparams)
life_time = estimate_lifetime(atmparams)
print(f'Decay in every revolution: {np.round(da_rev,4)} Km' )
print(f'Life Time: {np.round(life_time,4)} days' )


""" Propagation """
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
prop = Propagator("PDormand78", config=config_leo)
duration_sim =  16*sat.get_keplerian_period()# [sec]
print("Runnig propagation...")
# trajectory -> numpy: [tiempo, x, y, z]
trajectory = prop.run(sat, duration_sec=duration_sim, step_size=600)
# Ground Track 2D
fig_2d = graficar_2d_plotly(trajectory)
fig_2d.show()


elevation_min = 30 # [deg]

print("---------------------------------------------------------")
print("Mission Summary Report")
print("---------------------------------------------------------")
print("General Information: ")
print(f"Satellite: {sat.name}")
print(f"Altitude: {selected_sat['altitude']} [km]")
print(f"Inclination: {selected_sat['inclination']} [deg]")
print(f"Elevation Mask: {elevation_min} [deg]")
Lmax = compute_Lmax(selected_sat['altitude'], elevation_min)
print(f"Maximum Angle coverage (2Lmax): {np.round(2*Lmax,4)} [deg]")

# Longitude drifting because of Earth rotation and RAAN drift
P = sat.get_keplerian_period() # [sec]
DeltaL = (P/60.0)*(cts.earth_angular_velocity)
DeltaL_j2=J2_RAAN_drift(sat.sma,selected_sat['eccentricity'],selected_sat['inclination'])* P/cts.secinday # [deg/orbit]      
DeltaL_total = DeltaL - DeltaL_j2 # TODO: Confirm signs
print(f"Total Longitude drift per orbit: {np.round(DeltaL_total,4)} [deg/orbit]" )

# REVISIT
review -> continuar
* Revisar las cuentas de revisita
* Identificar bien inputs y outputs del reporte
* Trasladar los inputs y outputs al main -> que tome forma de formulario
* Analizar incorporar más satélites en fase para la cobertura global

k_day = sat.get_revolutions_per_day()
print(f"Revolutions per day: {np.round(k_day,4)} [rev/day]")    
daily_Equator_crossing_ = k_day * (np.radians(Lmax)/(np.pi*np.sin(np.radians(selected_sat['inclination'])))) 
Revisit_time  = 24/daily_Equator_crossing_ # [hs]
print(f"Revisit time: {np.round(Revisit_time,4)} [hs]")


print("COVERAGE ANALYSIS: ")

if DeltaL_total < 2*Lmax:
    k_global = np.ceil(360/DeltaL_total)
    print("Global Coverage is possible in k revolutions: ", k_global)
else:
    k_revisit = Revisit_time*60.0 / P
    print("Revisit time is possible in k revolutions: ", np.round(k_revisit,4))
    coverage_revisit = k_revisit * (DeltaL_total-2*Lmax)
    print("Coverage in k revolutions: ", np.round(coverage_revisit,4), " [deg]")


