import numpy as np
import matplotlib.pyplot as plt
from space_env import Satellite, Propagator
from visualizer import plot_ground_track, graficar_2d_plotly, plot_ground_track_with_access

print("Entorno cargado correctamente.")

# Instanciamos el satelite (esto crea el objeto Spacecraft en GMAT)
sat = Satellite("Saocom")

# Configuramos una orbita circular a 700 km de altura (LEO)
# SMA = 6371 (Radio Tierra) + 700 = 7071 km
sat.set_keplerian(
    sma=7071, 
    ecc=0.0001, 
    inc=98.2, 
    raan=0, 
    aop=0, 
    ta=0
)
print(f"Satelite '{sat.name}' configurado.")

# 1. Definir la fidelidad de la física
config_leo = {
    'gravity': 'Earth',
    'degree': 2,    # Activa J2
    'order': 0,
    'drag': True    # Resistencia atmosférica (importante en LEO)
}

# 2. Instanciar el propagador (esto crea el ForceModel y el Propagator en GMAT)
prop = Propagator("MyPropagator", config=config_leo)

# 5 horas en segundos
duracion_sim = 5 * 3600 

print("Propagando...")
# Esto devuelve un array de numpy: [tiempo, x, y, z]
trayectoria = prop.run(sat, duration_sec=duracion_sim, step_size=60)

print(f"¡Listo! Se generaron {trayectoria.shape[0]} puntos de datos.")

# Ground Track 3D
figura = plot_ground_track(trayectoria, epoch="2026-01-16T12:00:00")
figura.show()

# Ground Track 2D
fig_2d = graficar_2d_plotly(trayectoria)
fig_2d.show()

