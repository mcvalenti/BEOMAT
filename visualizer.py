import plotly.graph_objects as go
from astropy import units as u
from astropy.coordinates import CartesianRepresentation, GCRS, ITRS, EarthLocation
from astropy.time import Time


"""
 2D - PLOT
"""
def graficar_2d_plotly(trayectoria, epoch="2025-01-01T12:00:00"):
    # 1. Procesamiento de coordenadas con Astropy
    t_ref = Time(epoch, format='isot', scale='utc')
    tiempos = t_ref + trayectoria[:, 0] * u.second
    
    # Convertimos de Inercial (GCRS) a Terrestre (ITRS)
    cartesianas = CartesianRepresentation(trayectoria[:, 1:4].T * u.km)
    gcrs_coords = GCRS(cartesianas, obstime=tiempos)
    itrs_coords = gcrs_coords.transform_to(ITRS(obstime=tiempos))
    
    # Obtenemos Latitud, Longitud y Altura Geodésica
    location = EarthLocation.from_geocentric(itrs_coords.x, itrs_coords.y, itrs_coords.z)
    lats = location.lat.value
    lons = location.lon.value
    alts = location.height.to(u.km).value

    # 2. Creación del gráfico 2D
    fig = go.Figure()

    # Añadir la línea de la trayectoria
    fig.add_trace(go.Scattergeo(
        lat=lats,
        lon=lons,
        mode='lines',
        line=dict(width=2, color='red'),
        name='Trayectoria GMAT',
        hoverinfo='text',
        text=[f"T: {t:.1f}s<br>Alt: {a:.1f} km" for t, a in zip(trayectoria[:, 0], alts)]
    ))

    # Configuración del Layout para Mapa 2D
    fig.update_layout(
        title="Ground Track 2D (Proyección Equirrectangular)",
        geo=dict(
            projection_type='equirectangular', # Esta es la clave para el 2D
            showland=True, landcolor="LightGreen",
            showocean=True, oceancolor="LightBlue",
            showlakes=True, lakecolor="Blue",
            showcountries=True,
            resolution=50, # Calidad de las fronteras
            lonaxis=dict(range=[-180, 180]),
            lataxis=dict(range=[-90, 90])
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
        template="plotly_white"
    )
    
    return fig

# Ejecución
# fig_2d = graficar_2d_plotly(trayectoria)
# fig_2d.show()


"""
 3D - PLOT
"""

def plot_ground_track(trayectoria, epoch="2000-01-01T12:00:00"):
    # 1. Extraer datos del array de GMAT
    tiempos_seg = trayectoria[:, 0]
    pos_km = trayectoria[:, 1:4]
    
    # 2. Configurar tiempos con Astropy
    t_ref = Time(epoch, format='isot', scale='utc')
    tiempos = t_ref + tiempos_seg * u.second
    
    # 3. Transformación de Inercial (GCRS) a Terrestre (ITRS)
    # GMAT usa MJ2000, que en Astropy mapeamos a GCRS con alta precisión
    cartesianas = CartesianRepresentation(pos_km.T * u.km)
    gcrs_coords = GCRS(cartesianas, obstime=tiempos)
    itrs_coords = gcrs_coords.transform_to(ITRS(obstime=tiempos))
    
    # 4. Obtener Latitud y Longitud Geodésica (WGS84)
    location = EarthLocation.from_geocentric(itrs_coords.x, itrs_coords.y, itrs_coords.z)
    lat = location.lat.value
    lon = location.lon.value
    
    # 5. Crear el Globo 3D con Plotly
    fig = go.Figure(data=go.Scattergeo(
        lat=lat,
        lon=lon,
        mode='lines',
        line=dict(width=2, color='magenta')
    ))

    fig.update_layout(
        title="Satellite position (Interactive)",
        geo=dict(
            projection_type='orthographic', # Esto crea el globo 3D
            showland=True, landcolor="DarkGreen",
            showocean=True, oceancolor="LightBlue",
            showlakes=True, lakecolor="Blue",
            showcountries=True
        ),
        template="plotly_dark"
    )
    return fig

# Llamada final:
# figura = plot_ground_track(trayectoria)
# figura.show()


"""
 Access PLOT
"""
def plot_ground_track_with_access(trajectory, epoch, sites_data=None):
    """
    Plots the satellite ground track and adds markers for Sites.
    Circle size represents cumulative pass duration.
    
    :param trajectory: numpy array [time, x, y, z]
    :param epoch: Astropy Time or ISO string
    :param sites_data: List of dicts [{'site': site_obj, 'passes': [pass_list]}]
    """
    # 1. Trajectory Processing (Your existing logic)
    t_ref = Time(epoch)
    tiempos = t_ref + trajectory[:, 0] * u.second
    cartesianas = CartesianRepresentation(trajectory[:, 1:4].T * u.km)
    gcrs_coords = GCRS(cartesianas, obstime=tiempos)
    itrs_coords = gcrs_coords.transform_to(ITRS(obstime=tiempos))
    
    location = EarthLocation.from_geocentric(itrs_coords.x, itrs_coords.y, itrs_coords.z)
    lats = location.lat.value
    lons = location.lon.value

    fig = go.Figure()

    # Add Satellite Path
    fig.add_trace(go.Scattergeo(
        lat=lats, lon=lons,
        mode='lines',
        line=dict(width=1.5, color='red'),
        name='Satellite Path'
    ))

    # 2. Add Sites with variable bubble size
    if sites_data:
        site_lats = []
        site_lons = []
        site_names = []
        bubble_sizes = []
        hover_texts = []

        for item in sites_data:
            site = item['site']
            passes = item['passes']
            
            # Calculate total duration for this site
            total_duration = sum(p.duration_sec for p in passes)
            
            site_lats.append(site.lat)
            site_lons.append(site.lon)
            site_names.append(site.name)
            
            # Scaling logic: Adjust the factor (e.g., 0.1) so the circles 
            # aren't too big or too small on the map.
            bubble_sizes.append(total_duration * 0.05 + 10) 
            
            hover_texts.append(
                f"Site: {site.name}<br>"
                f"Total Passes: {len(passes)}<br>"
                f"Total Time: {total_duration:.1f}s"
            )

        fig.add_trace(go.Scattergeo(
            lat=site_lats,
            lon=site_lons,
            text=hover_texts,
            name='Ground Sites',
            mode='markers',
            marker=dict(
                size=bubble_sizes,
                color='blue',
                opacity=0.7,
                line=dict(width=1, color='white')
            )
        ))

    fig.update_layout(
        title="Satellite Ground Track & Site Access Duration",
        geo=dict(
            projection_type='equirectangular',
            showland=True, landcolor="rgb(240, 240, 240)",
            showcountries=True,
            lonaxis=dict(range=[-180, 180]),
            lataxis=dict(range=[-90, 90])
        ),
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    
    return fig

    # visual_data = [{'site': station_cordoba, 'passes': passes_cordoba}]
    # fig = plot_ground_track_with_access(trajectory_data, start_epoch, visual_data)
    # fig.show()