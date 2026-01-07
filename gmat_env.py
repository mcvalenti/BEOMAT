import os
import sys

_GMAT_INSTANCE = None

def get_gmat():
    """Load GMAT's motor with exceptions management"""
    global _GMAT_INSTANCE
    
    if _GMAT_INSTANCE is not None:
        return _GMAT_INSTANCE

    # --- PATHS CONFIGS ---
    #gmat_bin_path = r'C:\Users\mvalenti\Desktop\gmat-win-R2022a\GMAT\bin' (AR machine)
    gmat_bin_path = r'C:\Users\macec\Downloads\gmat-win-R2022a\GMAT\bin'
    
    if not os.path.exists(gmat_bin_path):
        raise FileNotFoundError(f"GMAT path does not exist: {gmat_bin_path}")

    try:
        # 1. ENVIRONMENTAL VARIABLES CONFIG
        if gmat_bin_path not in sys.path:
            sys.path.append(gmat_bin_path)
        
        if gmat_bin_path not in os.environ['PATH']:
            os.environ['PATH'] = gmat_bin_path + os.pathsep + os.environ['PATH']

        # 2. IMPORT
        import gmatpy as gmat
        
        # 3. Setup motor
        setup_file = os.path.join(gmat_bin_path, "gmat_startup_file.txt")
        gmat.Setup(setup_file)
        
        _GMAT_INSTANCE = gmat
        print(">>> [SUCCESS] GMAT LOADED")
        return _GMAT_INSTANCE

    except ImportError as e:
        print(f">>> [ERROR]  gmatpy not imported.")
        print(f"Detail: {e}")
        raise
    except Exception as e:
        print(f">>> [ERROR] Unexpeted error: {e}")
        raise