
'''
Created on Feb 01, 2026

Module to analyze simulations results 
or compute mathematical expressions for raw analitical estimations

@author: mcvalenti
'''

import numpy as np
import pandas as pd
import constants as cts

def get_density(altitude):
    """
    Compute atmospheric density from table and a logarithmic interpolation

    Args:
        altitude (float): Satellite altitude in km.

    atmospheric.csv: (pd.DataFrame): DataFrame containing columns ['h', 'rho', 'H']
                                   h: Altitude [km]
                                   rho: Reference Density [kg/m^3]
                                   H: Scale Height [km]

    Returns:
        float: Interpolated density at target_altitude kg/m3.
    """
    path_atm_table='Tables/atmospheric.csv'

    df_atm=pd.read_csv(path_atm_table, 
                       skiprows=1, 
                    names=['h', 'rho', 'H', 'T', 'P', 'M'])
    
    # 1. Find the base level (the row where h is just below our target altitude)
    lower_bound = df_atm[df_atm['h'] <= altitude].iloc[-1]
    
    h0 = lower_bound['h']
    rho0 = lower_bound['rho']
    scale_height = lower_bound['H']
    
    # 2. Apply Exponential Decay Formula: rho = rho0 * exp(-(h - h0) / H)
    delta_h = altitude - h0
    rho = rho0 * np.exp(-delta_h / scale_height)
    
    return rho

def drag_decay_per_rev(atmparams=None):
    """
    Raw Estimation of decay because of atmospheric friction.
    Change in semi-major axis per revolution (Eq. 6-22 SMAD).
        Units: km / rev
    :param params: dict containing:
        'cd': drag coefficient [-]
        'area': cross-sectional area [m^2]
        'mass': spacecraft mass [kg]
        'a': semi-major axis [km]
        'h': altitude [km]

    rho: atmospheric density
    H: atmospheric dnesity scale height

    """
    # 1. Extract parameters for readability
    cd = atmparams['cd']
    area = atmparams['area']
    mass = atmparams['mass']
    a = atmparams['a']
    h = atmparams['h']

    # 2. Get density at current altitude using our interpolation function
    rho = get_density(h)
    
    # 3. Units Conversion: rho from [kg/m^3] to [kg/km^3]
    # Crucial for consistency with semi-major axis in [km]
    rho_km3 = rho * 1e9

    # 4. Ballistic term (Cd * A / m)
    # Note: area must be in km^2 to match rho_km3 if mass is kg
    # Or more simply: keep area in m^2, rho in kg/m^3 and convert a to meters
    # Let's use the standard SMAD consistency (all in km):
    area_km2 = area * 1e-6

    # 5. Eq. 6-22 SMAD: delta_a_rev = -2 * pi * (Cd * A / m) * a^2 * rho
    delta_a_rev = -2 * np.pi * (cd * area_km2 / mass) * (a**2) * rho_km3
    
    return delta_a_rev

def estimate_lifetime(params):
    """
    Estimates total lifetime based on Scale Height (Eq. 6-24 SMAD).
    Units: Days
    """
    # Get delta_a per revolution
    delta_a_rev = drag_decay_per_rev(params)

    # SMAD table 
    path_atm_table='Tables/atmospheric.csv'
    df_atm=pd.read_csv(path_atm_table, 
                       skiprows=1, 
                    names=['h', 'rho', 'H', 'T', 'P', 'M'])
    
    # Extract Scale Height (H) from table for current altitude
    lower_bound = df_atm[df_atm['h'] <= params['h']].iloc[-1]
    scale_height = lower_bound['H']
    
    # Eq. 6-24: L_revs = -H / delta_a_rev
    lifetime_revs = -scale_height / delta_a_rev
    
    # Convert revs to days: L_days = L_revs * (Period / 86400)
    period_sec = 2 * np.pi * np.sqrt(params['a']**3 / cts.mu_e)
    
    return (lifetime_revs * period_sec) / cts.secinday

# GEOMETRIC COVERAGE

def compute_Lmax(altitude, elevation_min):
    """ 
    Spheric Earth Geometry - Maximum Ground Coverage Angle (Lmax) 
    for a given satellite altitude and minimum elevation angle.
    ---------------------------------------------------------------------
    altitude (float): Satellite altitude in [km].
    elevation_min (float): Minimum elevation angle [deg].  
    rho: Angular radius of the Earth as seen from the satellite [rad].    
    eta_max: Nadir angle from the satellite to the target horizon with elevation_min [rad].
    Returns:
        Lmax_deg (float): Maximum ground coverage angle in [deg].

    """ 
    elevation_min_rad = np.radians(elevation_min)
    rho = np.arcsin(cts.Re / (cts.Re + altitude))
    eta_max = np.arcsin(np.sin(rho)*np.cos(elevation_min_rad))
    Lmax_rad = np.pi/2 - eta_max - elevation_min_rad
    Lmax_deg = np.degrees(Lmax_rad)
    
    return Lmax_deg

def compute_Swath(altitude, elevation_min):
    """
    Computes the swath width (ground coverage) for a satellite at a given altitude
    and minimum elevation angle. (Spheric Earth Geometry)
    ---------------------------------------------------------------------
    altitude (float): Satellite altitude in [km].
    elevation_min (float): Minimum elevation angle [deg].
    
    Returns:
        swath_width_km (float): Swath width in [km].
    """
    Lmax_deg = compute_Lmax(altitude, elevation_min)
    
    # Convert Lmax from degrees to radians for the sine function
    Lmax_rad = np.radians(Lmax_deg)
    
    # Swath width calculation using the formula: Swath = 2 * R * sin(Lmax)
    swath_width_km = 2 * cts.Re * np.sin(Lmax_rad)
    
    return swath_width_km

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






