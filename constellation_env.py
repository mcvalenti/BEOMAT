import json
from dataclasses import dataclass, field
from typing import List, Union, Optional
from space_env import Satellite

@dataclass
class SatelliteConstellation:
    # Required parameters for a basic identification
    name: str
    approx_satellites: int
    
    # Optional parameters with default values (English)
    classification: str = "Broadband"
    company: str = "Unknown"
    country_of_origin: str = "International"
    altitude_km: int = 550
    inclination_deg: Union[str, float] = 53.0
    configuration: str = "Standard LEO"
    primary_launcher: str = "TBD"
    primary_purpose: str = "Communication"
    satellites: List[Satellite] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict):
        """
        Factory method to create an instance from a full dictionary (JSON style).
        """
        return cls(**data)

    @classmethod
    def create_walker(cls, name: str, t_total: int, p_planes: int, f_phasing: int, inc: float, alt: int):
        """
        Simplified constructor for a Walker Delta Constellation (T/P/F).
        Calculates configuration string automatically.
        """
        return cls(
            name=name,
            approx_satellites=t_total,
            altitude_km=alt,
            inclination_deg=inc,
            configuration=f"Walker Delta {t_total}/{p_planes}/{f_phasing}",
            primary_purpose="Research/Navigation"
        )
    
    def deploy_in_gmat_from_list(self, sat_list):
        # Instantiate our Satellite class
        for sat in sat_list:
            new_sat = Satellite(name=sat[0])
            # Set GMAT parameters
            new_sat.set_keplerian(
                sma=sma,
                ecc=0.0, # Circular orbit
                inc=self.inclination_deg,
                raan=current_raan,
                aop=0.0,
                ta=current_ta
            )
            # Store in the constellation list
            self.satellites.append(new_sat)
        
        print(f"Successfully deployed {len(self.satellites)} satellites in GMAT.")
    
    def deploy_in_gmat_from_Walker(self, planes: int, phasing: int):
        """
        Logic to automatically create Satellite objects and configure 
        their orbits in GMAT according to Walker Delta logic.
        """
        earth_radius = 6371.0
        sma = earth_radius + self.altitude_km
        
        sats_per_plane = self.approx_satellites // planes
        raan_spacing = 360 / planes
        ta_spacing = 360 / sats_per_plane
        phase_offset = (360 * phasing) / self.approx_satellites

        for p in range(planes):
            current_raan = p * raan_spacing
            for s in range(sats_per_plane):
                # 1. Create unique name
                sat_name = f"{self.name}_{p}_{s}"
                
                # 2. Instantiate our Satellite class
                new_sat = Satellite(name=sat_name)
                
                # 3. Calculate True Anomaly (TA) with phasing
                current_ta = (s * ta_spacing) + (p * phase_offset)
                
                # 4. Set GMAT parameters
                new_sat.set_keplerian(
                    sma=sma,
                    ecc=0.0, # Circular orbit
                    inc=self.inclination_deg,
                    raan=current_raan,
                    aop=0.0,
                    ta=current_ta
                )
                
                # 5. Store in the constellation list
                self.satellites.append(new_sat)
        
        print(f"Successfully deployed {len(self.satellites)} satellites in GMAT.")


class ConstellationManager:
    def __init__(self, constellations: Optional[List[SatelliteConstellation]] = None):
        self.constellations = constellations if constellations else []

    def add_constellation(self, constellation: SatelliteConstellation):
        self.constellations.append(constellation)

    def filter_by_country(self, country: str) -> List[SatelliteConstellation]:
        """Returns a list of constellations matching the country name."""
        return [c for c in self.constellations if country.lower() in c.country_of_origin.lower()]

    def get_total_satellite_count(self) -> int:
        """Returns the sum of all satellites in the managed constellations."""
        return sum(c.approx_satellites for c in self.constellations)

    def summary(self):
        """Prints a quick summary of all managed assets."""
        print(f"{'Name':<20} | {'Sats':<6} | {'Altitude':<10} | {'Purpose'}")
        print("-" * 60)
        for c in self.constellations:
            print(f"{c.name:<20} | {c.approx_satellites:<6} | {c.altitude_km:<10} | {c.primary_purpose}")

# --- Practical Usage Example ---

if __name__ == "__main__":
    # 1. Create using the Walker shortcut
    my_mesh = SatelliteConstellation.create_walker("AlphaNet", 24, 3, 1, 53.0, 600)

    # 2. Create from a JSON-like dictionary
    starlink_data = {
        "name": "Starlink V3",
        "approx_satellites": 6800,
        "company": "SpaceX",
        "country_of_origin": "USA",
        "altitude_km": 550,
        "inclination_deg": 53.0,
        "primary_purpose": "Global Internet"
    }
    starlink = SatelliteConstellation.from_json(starlink_data)

    # 3. Manage them
    manager = ConstellationManager([my_mesh, starlink])
    
    # 4. Results
    print(f"Total satellites in orbit: {manager.get_total_satellite_count()}\n")
    manager.summary()