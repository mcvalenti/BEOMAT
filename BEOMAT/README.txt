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
-----------------------------------------------------------------------------------------