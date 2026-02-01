
'''
Created on Feb 01, 2026

Module to analyze simulations results 
or compute mathematical expressions for analitical estimations

@author: mcvalenti
'''

import numpy as np
import pandas as pd

def get_density(altitude):
    """
    Compute atmospheric density from table
    and a logarithmic interpolation

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
    mu = 398600.4415
    period_sec = 2 * np.pi * np.sqrt(params['a']**3 / mu)
    
    return (lifetime_revs * period_sec) / 86400





