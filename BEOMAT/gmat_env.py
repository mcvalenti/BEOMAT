# import os
# import sys

# # Flag para evitar inicialización múltiple
# _GMAT_INITIALIZED = False

# def init_gmat():
#     """
#     Inicializa el entorno GMAT para Python.
#     Debe llamarse antes de usar la API GMAT.
#     """

#     global _GMAT_INITIALIZED

#     gmat_bin_path = r'C:\Users\mvalenti\Desktop\gmat-win-R2022a\GMAT\bin'
#     sys.path.append(gmat_bin_path)
#     # Ruta a la carpeta gmatpy (los archivos _py3#)
#     gmat_api_path = os.path.join(gmat_bin_path, 'gmatpy')
#     # Verificar si el archivo existe fisicamente antes de cargarlo
#     startup_file = gmat_bin_path+'\gmat_startup_file.txt'
#     if os.path.exists(startup_file):
#         print(f"--- Archivo de configuración encontrado en: {startup_file}")
#     else:
#         print("--- ERROR: No se encuentra gmat_startup_file.txt en esta carpeta.")
#     try:
#         import gmatpy as gmat
        
#         # Inicializacion global
#         gmat.Setup(startup_file) 
        
#         # Para acceder a la interfaz y crear objetos:
#         # Nota:GmatInterface or usas gmat.Construct 
#         print("Motor de GMAT cargado correctamente.")
        

        
#     except Exception as e:
#         print(f"Error detallado: {e}")

#     _GMAT_INITIALIZED = True

import os
import sys

_GMAT_INSTANCE = None

def get_gmat():
    """Carga el motor GMAT con manejo de excepciones."""
    global _GMAT_INSTANCE
    
    if _GMAT_INSTANCE is not None:
        return _GMAT_INSTANCE

    # --- CONFIGURACIÓN DE PATHS ---
    # Asegúrate de que esta ruta sea exacta en tu sistema
    #gmat_bin_path = r'C:\Users\mvalenti\Desktop\gmat-win-R2022a\GMAT\bin' 
    gmat_bin_path = r'C:\Users\macec\Downloads\gmat-win-R2022a\GMAT\bin'
    
    if not os.path.exists(gmat_bin_path):
        raise FileNotFoundError(f"La ruta de GMAT no existe: {gmat_bin_path}")

    try:
        # 1. Configurar variables de entorno
        if gmat_bin_path not in sys.path:
            sys.path.append(gmat_bin_path)
        
        if gmat_bin_path not in os.environ['PATH']:
            os.environ['PATH'] = gmat_bin_path + os.pathsep + os.environ['PATH']

        # 2. Intento de importación
        import gmatpy as gmat
        
        # 3. Setup del motor
        setup_file = os.path.join(gmat_bin_path, "gmat_startup_file.txt")
        gmat.Setup(setup_file)
        
        _GMAT_INSTANCE = gmat
        print(">>> [SUCCESS] Motor GMAT cargado y configurado.")
        return _GMAT_INSTANCE

    except ImportError as e:
        print(f">>> [ERROR] No se pudo importar gmatpy. Revisa que las DLLs estén en el PATH.")
        print(f"Detalle técnico: {e}")
        raise
    except Exception as e:
        print(f">>> [ERROR] Error inesperado al inicializar GMAT: {e}")
        raise