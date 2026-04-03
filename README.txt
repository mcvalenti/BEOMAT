Integrar GMAT (General Mission Analysis Tool) con Python para trabajar en un entorno como JupyterLab.
[Ref] ../yourdir/GMAT/docs/GMAT_API_UsersGuide.pdf

1. La Interfaz GMAT-Python (API)
GMAT no es una librería de Python que se instale con pip, sino un software independiente que expone una API de Python. Para usarla en Jupyter:

Configuración de Rutas: Debes indicarle a Python dónde reside el motor de GMAT dentro de tu computadora.

Carga del Motor: Se utiliza un módulo llamado gmatpy que viene dentro de la carpeta /bin de tu instalación de GMAT.

Tipo en GMAT				Método Python			Ejemplo
String (Nombres, Modos)			SetField(str, str)		SetField("BodyName", "Earth")
Real (SMA, Altura, Masas)		SetReal(str, float)		SetReal("SMA", 7100.0)
Integer (Grado, Orden, Iteraciones)	SetInteger(str, int)		SetInteger("Degree", 4)

Otras dependencias
plotly 
astropy (para la transformacion de ECI a Geodesicas)
-----------------------------------------------------------------------------------------
Versión de Astropy: 5.2.2
Versión de Python: 3.8.18 (default, Sep 11 2023, 13:39:12) [MSC v.1916 64 bit (AMD64)]
Versión de Requests: 2.32.4 (Python HTTP for Humans.)
Versión de Pandas: 2.0.3
-----------------------------------------------------------------------------------------

Configuracion del Entorno.
Vamos a dejarlo configurado de forma blindada siguiendo estos pasos:

1. Forzar la instalación en el ejecutable correcto
Para evitar cualquier confusión entre terminales, ejecuta esto dentro de una celda de tu Notebook.
Esto garantiza que la instalación ocurra exactamente donde vive tu .venv:
la clave está en que la Terminal de VSCode y el Kernel del Notebook hablen el mismo idioma.


Bloqueo de scripts de Venv
Ese error es un clásico de Windows. Por seguridad, PowerShell viene configurado de fábrica para bloquear
la ejecución de scripts (como el archivo Activate.ps1 de tu entorno virtual).

Para solucionarlo y poder "entrar" a tu entorno virtual, tienes que cambiar la Política de Ejecución.

🚀 General Use
Follow these steps to set up and run your mission analysis in BEOMAT:
- Define the ORBIT 🛰️
- - Set up the initial state vectors or Keplerian elements.
- - Select the appropriate Reference Frame (ECI, ITRF, etc.).
- Configure the FORCE MODELS 🌍
- - Select Earth's gravity field (J2, complex geopotential models).
- - Enable atmospheric drag, solar radiation pressure, and third-body perturbations (Sun/Moon).
- Set the SIMULATION SCENARIO ⏱️
- - Define start and stop times (Epoch).
- - Configure the numerical integrator and step size for propagation.
- Make an Analysis (Optional) 📊
- - Custom modules for specific mission requirements:
- - - Coverage & Revisit: Calculate ground track access and gaps. (On construction)
- - - End of Life (EoL): Estimate orbital decay and re-entry timelines. (For LEO)
- - - Orbit Maintenance: Station-keeping maneuvers and fuel budget. (Not yet)
- - - Launch Windows: Identify optimal departure dates and $\Delta V$. (Not yet)
- - - Propulsion Requirements: Sizing for chemical or electric thrusters. (Not yet)
- VISUALIZATION 🎨
- - Generate 2D ground tracks and 3D orbital plots.
- - Export data for comparison and evaluation.

=========
MODULES 
=========

**access_manager.py**
Calculates visibility between a pre-computed trajectory and a Ground Site.
From a precomputed trajectory (GMAT), uses astropy library to compute Az and El (and formate timestamp),
and check for the visibility from a particular site on earth.  Returns a List of Pass objects (from ground_segment)
- class AccessManager

**analitics.py**
(Do not use GMAT environment)
Module to analyze simulations results or compute mathematical expressions for raw analitical estimations.
Analitics allows to compute general metrics without making precise propagations. Particularly useful for 
LEO orbits, to compute decay because of atmospheric drag. 
- get_density - drag_decay_per_rev - estimate_lifetime

**constants.py**
List astrodynamics more used constants values

**constellation_env.py**
TODO: TO describe in more details foward. 

**envConfiguration.py**
Prints python and GMAT environment configuration

**gmat_env.py**
Fundamentals to instatiate GMAT environment 
gmatpy executable PATH must be set here

**ground_segment.py**
Contains all objects regarding Ground Station, as: Site, station, ROI, pass

**satCatalog.py**
Manage request to CELESTRACK. 

**space_env.py**
Fundamental for the creation of spacecraft object, throughout GMAT environment (spacecraft)
or as TLE (spg4). It also contains the Propagator object (GMAT)

**visualizer.py**
Contains functions to plot trajectories 3D and 2D (ground track)


