from satCatalog import request_celestrak_data
from space_env import Satellite, Propagator, TLEHandler
import ground_segment as gs
import access_manager as am
from visualizer import graficar_2d_plotly, plot_ground_track_with_access

# Request Satellites to Celestrak
nusat_list = request_celestrak_data("NUSAT", "NAME")
nusat45=nusat_list[-1]
handler = TLEHandler.from_json(nusat45) # To propagate with SGP4

handler.name.split()[0]

# New Satellite
sat_name = handler.name.split()[0]
# 3. Get the state at the TLE's specific Epoch 
state = handler.get_state_at() 

# Initialize GMAT Satellite and set the state
sat_nusat = Satellite(sat_name)
sat_nusat.set_cartesian(
    epoch_astropy=state['epoch'],
    pos=state['pos'],
    vel=state['vel']
)

# 1. Interval of propagation (eg: 1 orbit ~ 90 min = 5400 sec)
duration = 16*5400 
step = 60 # dates every 60 sec

# 2. Instantiate propagator
prop = Propagator(name="HighPrecisionProp")

# 3. Execute propagation
# Esto devolverá un array de numpy con [tiempo, x, y, z]
trajectory_data = prop.run(sat_nusat, duration, step_size=step)

print(f"Propagación completada. Puntos calculados: {len(trajectory_data)}")
print(f"Última posición (km): {trajectory_data[-1, 1:]}")

# Ground Track 2D
fig_2d = graficar_2d_plotly(trajectory_data)
fig_2d.show()

"""
Analysis
"""
# Sites
bsas = gs.Site("BuenosAires", -34.6, -58.48, 25)
matera = gs.Site("Matera", 40.66, 16.6, 100)

# Access computation
acc1 = am.AccessManager()
acc2 = am.AccessManager()
access_bsas = acc1.calculate_access(trajectory_data, state['epoch'], bsas)
access_matera = acc1.calculate_access(trajectory_data, state['epoch'], matera)

# Visualizer
visual_data = [{'site': bsas, 'passes': access_bsas}, {'site': matera, 'passes': access_matera}]
fig = plot_ground_track_with_access(trajectory_data, state['epoch'], visual_data)
fig.show()

