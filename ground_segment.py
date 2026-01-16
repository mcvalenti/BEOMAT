from dataclasses import dataclass
from datetime import datetime
from astropy import units as u
from astropy.coordinates import EarthLocation

@dataclass
class Pass:
    """Data structure for a calculated visibility window."""
    aos: datetime
    los: datetime
    max_elevation: float
    duration_sec: float

class Site:
    """Base class for any geographical location."""
    def __init__(self, name, lat, lon, alt_m=0):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.alt_m = alt_m
        self.location = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=alt_m*u.m)

class Station(Site):
    """Ground station with a specific visibility mask."""
    def __init__(self, name, lat, lon, alt_m=0, min_elevation=10.0):
        super().__init__(name, lat, lon, alt_m)
        self.min_elevation = min_elevation

class ROI(Site):
    """Target region for imaging or analysis."""
    def __init__(self, name, lat, lon, radius_km=5.0):
        super().__init__(name, lat, lon, alt_m=0)
        self.radius_km = radius_km