import os
import sys

# Flag para evitar inicialización múltiple
_GMAT_INITIALIZED = False

def init_gmat():
    """
    Inicializa el entorno GMAT para Python.
    Debe llamarse antes de usar la API GMAT.
    """

    global _GMAT_INITIALIZED

    gmat_bin_path = r'C:\Users\mvalenti\Desktop\gmat-win-R2022a\GMAT\bin'
    sys.path.append(gmat_bin_path)
    # Ruta a la carpeta gmatpy (los archivos _py3#)
    gmat_api_path = os.path.join(gmat_bin_path, 'gmatpy')
    # Verificar si el archivo existe fisicamente antes de cargarlo
    startup_file = gmat_bin_path+'\gmat_startup_file.txt'
    if os.path.exists(startup_file):
        print(f"--- Archivo de configuración encontrado en: {startup_file}")
    else:
        print("--- ERROR: No se encuentra gmat_startup_file.txt en esta carpeta.")
    try:
        import gmatpy as gmat
        
        # Inicializacion global
        gmat.Setup(startup_file) 
        
        # Para acceder a la interfaz y crear objetos:
        # Nota:GmatInterface or usas gmat.Construct 
        print("Motor de GMAT cargado correctamente.")
        
        # Crear un satelite
        sat = gmat.Construct("Spacecraft", "Cubesat_EO")
        print(f"Objeto creado: {sat.GetName()}")
        
    except Exception as e:
        print(f"Error detallado: {e}")

    _GMAT_INITIALIZED = True