
from satCatalog import request_celestrak_data
from space_env import TLEHandler
# Request Satellites to Celestrak
nusat_list = request_celestrak_data("NUSAT", "NAME")
print(nusat_list)
# Choose the last satellite of the list
nusat45=nusat_list[-1]
handler = TLEHandler.from_json(nusat45) # To propagate with SGP4
state= handler.get_state_at()
orbital_elements = handler.get_orbit_elements()
print(orbital_elements)