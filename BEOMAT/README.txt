Integrar GMAT (General Mission Analysis Tool) con Python para trabajar en un entorno como JupyterLab.

1. La Interfaz GMAT-Python (API)
GMAT no es una librería de Python que se instale con pip, sino un software independiente que expone una API de Python. Para usarla en Jupyter:

Configuración de Rutas: Debes indicarle a Python dónde reside el motor de GMAT dentro de tu computadora.

Carga del Motor: Se utiliza un módulo llamado gmatpy que viene dentro de la carpeta /bin de tu instalación de GMAT.