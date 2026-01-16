import numpy as np
from astropy.time import Time, TimeDelta
from astropy.coordinates import CartesianRepresentation, GCRS, ITRS, AltAz
from astropy import units as u
from ground_segment import Pass

class AccessManager:
    """
    Calculates visibility between a pre-computed trajectory and a Ground Site.
    """
    
    @staticmethod
    def calculate_access(trajectory_data, start_epoch_astropy, site):
        """
        :param trajectory_data: numpy array [time_offset, x, y, z] from GMAT
        :param start_epoch_astropy: The Astropy Time of the first point (t=0)
        :param site: A Station or ROI object
        :return: List of Pass objects
        """
        passes = []
        is_visible = False
        current_pass_start = None
        max_el = 0.0

        # 1. Iterate through the trajectory steps
        for row in trajectory_data:
            t_offset, x, y, z = row
            
            # Calculate actual time for this point
            current_time = start_epoch_astropy + TimeDelta(t_offset, format='sec')
            
            # 2. Define the position in GCRS (Inertial - GMAT's default)
            # GMAT uses km, so we multiply by u.km
            inertial_pos = GCRS(
                CartesianRepresentation(x=x*u.km, y=y*u.km, z=z*u.km),
                obstime=current_time
            )
            
            # 3. Transform to ITRS (Earth-Fixed)
            earth_fixed_pos = inertial_pos.transform_to(ITRS(obstime=current_time))
            
            # 4. Calculate Elevation/Azimuth relative to the Site
            # This is where we see if the satellite is "above the horizon"
            altaz_frame = AltAz(obstime=current_time, location=site.location)
            satellite_altaz = earth_fixed_pos.transform_to(altaz_frame)
            
            elevation = satellite_altaz.alt.deg
            
            # 5. Logical check for AOS/LOS (Acquisition/Loss of Signal)
            min_el = getattr(site, 'min_elevation', 0.0) # Default to 0 if it's an ROI
            
            if elevation >= min_el:
                if not is_visible:
                    # AOS detected
                    is_visible = True
                    current_pass_start = current_time
                    max_el = elevation
                else:
                    # Update max elevation during the pass
                    if elevation > max_el:
                        max_el = elevation
            else:
                if is_visible:
                    # LOS detected
                    is_visible = False
                    duration = (current_time - current_pass_start).sec
                    
                    # Create the Pass object (assuming you imported it)
                    # from entities import Pass
                    new_pass = Pass(
                        aos=current_pass_start.datetime,
                        los=current_time.datetime,
                        max_elevation=max_el,
                        duration_sec=duration
                    )
                    passes.append(new_pass)
                    max_el = 0.0
                    
        return passes