from sgp4.api import Satrec, jday, WGS84
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import TEME, CartesianRepresentation, ITRS
import numpy as np
from gmat_env import get_gmat

# Get GMAT's motor instance
gmat = get_gmat()

class Satellite:
    def __init__(self, name="MySat"):
        self.name = name
        self.gmat_obj = gmat.Construct("Spacecraft", name)
        
    def set_keplerian(self, **elements):
        """Configure kepelerian elements"""
        self.gmat_obj.SetField("CoordinateSystem", "EarthMJ2000Eq")
        self.gmat_obj.SetField("DisplayStateType", "Keplerian")
        
        mappings = {
            'sma': 'SMA', 
            'ecc': 'ECC', 
            'inc': 'INC', 
            'raan': 'RAAN', 
            'aop': 'AOP', 
            'ta': 'TA'
        }
        
        for key, value in elements.items():
            gmat_key = mappings.get(key.lower())
            if gmat_key:
                # GMAT espera un 'double' de C++, que en Python es float.
                try:
                    self.gmat_obj.SetReal(gmat_key, float(value))
                except AttributeError:
                    # En algunas versiones muy específicas, si SetReal falla, 
                    # intentamos SetField pero sin convertir a string
                    self.gmat_obj.SetField(gmat_key, float(value))
        
        gmat.Initialize()

    def format_astropy_to_gmat(self, astropy_time):
        """
        Converts Astropy Time to GMAT UTCGregorian: 'DD Mon YYYY HH:MM:SS.SSS'
        """
        # strftime %b gives abbreviated month name (Jan, Feb, etc.)
        return astropy_time.datetime.strftime('%d %b %Y %H:%M:%S.%f')[:-3]
    
    def set_cartesian(self, epoch_astropy, pos, vel):
        """
        Configure Cartesian state.
        :param epoch_str: UTC ISO format 'YYYY-MM-DD HH:MM:SS.SSS'
        :param pos: List or array [X, Y, Z] in km
        :param vel: List or array [VX, VY, VZ] in km/s
        """
        # Format the date correctly for GMAT
        gmat_epoch = self.format_astropy_to_gmat(epoch_astropy)

        # Set the Coordinate System to Earth Fixed or Inertial (J2000)
        self.gmat_obj.SetField("CoordinateSystem", "EarthMJ2000Eq")
        self.gmat_obj.SetField("DisplayStateType", "Cartesian")
        
        # Set the Epoch (GMAT uses UTCGregorian by default)
        self.gmat_obj.SetField("DateFormat", "UTCGregorian")
        self.gmat_obj.SetField("Epoch", gmat_epoch)
        
        # Set Position
        self.gmat_obj.SetField("X", float(pos[0]))
        self.gmat_obj.SetField("Y", float(pos[1]))
        self.gmat_obj.SetField("Z", float(pos[2]))
        
        # Set Velocity
        self.gmat_obj.SetField("VX", float(vel[0]))
        self.gmat_obj.SetField("VY", float(vel[1]))
        self.gmat_obj.SetField("VZ", float(vel[2]))
        
        gmat.Initialize()

class Propagator:
    def __init__(self, name="MainProp", config=None):
        gmat = get_gmat()
        self.name = name
        
        # ==============
        #  ForceModel
        # ==============
        self.force_model = gmat.Construct("ForceModel", f"FM_{name}")
        self.earthgrav = gmat.Construct("GravityField")
        self.earthgrav.SetField("PotentialFile","JGM2.cof")
        self.earthgrav.SetField("BodyName","Earth")
        self.earthgrav.Help()
        self.force_model.AddForce(self.earthgrav)
        # ==============
        #  Propagator
        # ==============
        self.gmat_prop = gmat.Construct("PropSetup", f"Prop_{name}")
        # ==============
        #  Integrator
        # ==============
        self.integrator = gmat.Construct("PrinceDormand78", f"Int_{name}")
        
        # Assign the integrator and force model
        self.gmat_prop.SetReference(self.integrator)
        self.gmat_prop.SetReference(self.force_model)
        
    #     # Configuracion por defecto si no se provee una
    #     if config is None:
    #         config = {'gravity': 'Earth', 'degree': 0, 'order': 0}
        
    #     self.config = config
    #     self._setup_forces(config)

    # def _setup_forces(self, config):
    #     """Configura el modelo de fuerzas usando enteros nativos para Degree/Order."""
    #     gmat = get_gmat()

    #     if 'gravity' in config:
    #         body = config['gravity']
    #         if config.get('degree', 0) > 0:
    #             grav = gmat.Construct("GravityField", f"Grav_{body}")
                
    #             grav.SetField("BodyName", body)
    #             # El Test 1 demostró que esto debe ser int
    #             grav.SetField("Degree", int(config['degree']))
    #             grav.SetField("Order", int(config['order']))
    #         else:
    #             grav = gmat.Construct("PointMassForce", f"PM_{body}")
    #             grav.SetField("BodyName", body)
            
    #         self.force_model.AddForce(grav)

    def run(self, satellite, duration_sec, step_size=60):
        gmat = get_gmat()
        # Top level initialization
        gmat.Initialize()
        sat_obj = satellite.gmat_obj       
        # Spacecraft that is propagated
        self.gmat_prop.AddPropObject(sat_obj)
        self.gmat_prop.PrepareInternals()
        
        # Refresh the integrator reference
        internal_prop = self.gmat_prop.GetPropagator()
       
        data = []
        current_time = 0.0
        
        for _ in range(0, int(duration_sec), step_size):
            # Propagar
            internal_prop.Step(float(step_size)) # take a step
            
            # Get Iterator state
            state = internal_prop.GetState() # To force sat_obj Update
            
            # Force step iteration
            sat_obj.SetField("X", state[0])
            sat_obj.SetField("Y", state[1])
            sat_obj.SetField("Z", state[2])
            sat_obj.SetField("VX", state[3])
            sat_obj.SetField("VY", state[4])
            sat_obj.SetField("VZ", state[5])
            
            pos = [state[0], state[1], state[2]]
            data.append([current_time] + pos)
            
            current_time += step_size
            
        return np.array(data)

class TLEHandler:
    """
    Handles TLE (Two-Line Element) data using SGP4 for propagation 
    and Astropy for coordinate frame transformations.
    """
    def __init__(self, name, line1=None, line2=None):
        """
        Initialize the TLE handler.
        :param name: String name of the satellite.
        :param line1: First line of the TLE.
        :param line2: Second line of the TLE.
        """
        self.mu = 398600.5 # [km2/s]
        self.Re = 6378.135 # [km]
        self.name = name
        self.line1 = line1
        self.line2 = line2
        # Initialize the SGP4 satellite record object (C++ backend)
        # Only call twoline2rv if lines are actually provided as strings
        if isinstance(line1, str) and isinstance(line2, str):
            self.satrec = Satrec.twoline2rv(line1, line2)
        
    @classmethod
    def from_json(cls, data):
        """
        Alternative constructor to create an instance from CelesTrak GP-JSON format.
        :param data: Dictionary containing OBJECT_NAME, TLE_LINE1, and TLE_LINE2.
        """
        return cls(
            name=data.get('OBJECT_NAME', 'Unknown'),
            line1=data.get('TLE_LINE1'),
            line2=data.get('TLE_LINE2')
        )
    
    @classmethod
    def from_omm(cls, data):
        """
        Use this if the JSON DOES NOT have TLE lines. 
        It initializes SGP4 using raw orbital elements.
        """
        name = data.get('OBJECT_NAME', 'Unknown')
        instance = cls(name)
        
        # Initialize a blank satellite record
        sat = Satrec()
        
        # Prepare the Epoch (Time)
        # SGP4 needs: epoch days since 1949 December 31 00:00 UT
        t = Time(data['EPOCH'])
        epoch_days = t.jd - 2433281.5
        
        # Initialize with orbital elements
        sat.sgp4init(
            WGS84, 
            'i', 
            data['NORAD_CAT_ID'], 
            epoch_days,
            data['BSTAR'],
            data.get('MEAN_MOTION_DOT', 0.0),
            data.get('MEAN_MOTION_DDOT', 0.0),
            data['ECCENTRICITY'],
            np.radians(data['ARG_OF_PERICENTER']),
            np.radians(data['INCLINATION']),
            np.radians(data['MEAN_ANOMALY']),
            data['MEAN_MOTION'] * (2 * np.pi / 1440.0), # rev/day to rad/min
            np.radians(data['RA_OF_ASC_NODE'])
        )
        
        instance.satrec = sat
        return instance
    
    def get_state_at(self, epoch_str=None):
        # 1. Handle time
        t = Time(epoch_str) if epoch_str else Time.now()
        
        # Use the Astropy Julian Date parts directly in the satrec.sgp4 method.
        # jd1 is the day, jd2 is the fraction of the day.
        error, r, v = self.satrec.sgp4(t.jd1, t.jd2)
        
        if error != 0:
            raise RuntimeError(f"SGP4 Propagation Error: Code {error}")
            
        return {
            'epoch': t,
            'pos': np.array(r), 
            'vel': np.array(v)
        }
    
    def get_orbit_elements(self):
        """
        Extracts orbital elements for SGP4 and SMAD.
        """
        # Mean Motion (revs/day)
        n_rev_day = float(self.line2[52:63])
        n_rad_min = (n_rev_day * 2 * np.pi) / 1440.0 # Standard for SGP4 init
        
        # Semi-major axis (a) for SMAD [km]
        n_rad_sec = (n_rev_day * 2 * np.pi) / 86400.0
        a = (self.mu / (n_rad_sec**2))**(1/3)
        
        return {
            'a': a,
            'h': a - self.Re,
            'e': float("0." + self.line2[26:33]),
            'inc': np.radians(float(self.line2[8:16])),
            'raan': np.radians(float(self.line2[17:25])),
            'argp': np.radians(float(self.line2[34:42])),
            'm': np.radians(float(self.line2[43:51])),
            'bstar': float(self.line1[53:59]) * 1e-5, # Simplified
            'n_rad_min': n_rad_min
        }

    def to_geodetic(self, epoch_str=None):
        """
        Transforms TEME Cartesian coordinates to Geodetic coordinates (Lat, Lon, Alt).
        Uses ITRS (International Terrestrial Reference System) for Earth-fixed projection.
        """
        # Obtain the inertial state vector
        state = self.get_state_at(epoch_str)
        
        # Create a TEME coordinate object (the native frame for SGP4/TLE)
        teme_coord = TEME(
            representation_type='cartesian',
            x=state['pos'][0] * u.km,
            y=state['pos'][1] * u.km,
            z=state['pos'][2] * u.km,
            obstime=state['epoch']
        )
        
        # Transform from inertial frame (TEME) to Earth-fixed frame (ITRS)
        # This handles Earth rotation (ERA) and precession/nutation
        itrs_coord = teme_coord.transform_to(ITRS(obstime=state['epoch']))
        
        # Extract geodetic information from the Earth location
        location = itrs_coord.earth_location.geodetic
        
        return {
            'lat': location.lat.deg,
            'lon': location.lon.deg,
            'alt': location.height.to(u.km).value,
            'epoch': state['epoch'].iso
        }
