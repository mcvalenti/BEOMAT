import sys
import numpy
import gmatpy

print(f"--- DIAGNÓSTICO ---")
print(f"Python ejecutable: {sys.executable}")
print(f"Numpy versión: {numpy.__version__}")
print(f"Numpy ruta: {numpy.__file__}")
print(f"GMAT cargado: {gmatpy is not None}")