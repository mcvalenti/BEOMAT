from gmat_env import init_gmat
init_gmat()   # Se ejecuta automaticamente al importar

import gmatpy as gmat
import numpy as np

class Satellite:
    def __init__(
        self,
        name="Sat1",
        sma=7000.0,      # km
        ecc=0.001,
        inc=98.0,        # deg
        raan=0.0,
        aop=0.0,
        ta=0.0,
        epoch="01 Jan 2024 00:00:00.000"
    ):
        self.name = name
        self.orbital_elements = {
            "SMA": sma,
            "ECC": ecc,
            "INC": inc,
            "RAAN": raan,
            "AOP": aop,
            "TA": ta,
            "Epoch": epoch,
        }

        self.sc = None
        self.propagator = None

        self._build_spacecraft()
        self._build_propagator()

    # ------------o--------------
    # Construccion del spacecraft
    # ---------------------------
    def _build_spacecraft(self):
        self.sc = gmat.Construct("Spacecraft", self.name)

        self.sc.SetField("DateFormat", "UTCGregorian")
        self.sc.SetField("Epoch", self.orbital_elements["Epoch"])
        self.sc.SetField("CoordinateSystem", "EarthMJ2000Eq")
        self.sc.SetField("DisplayStateType", "Keplerian")

        for key, value in self.orbital_elements.items():
            if key != "Epoch":
                self.sc.SetField(key, value)

    # ---------------------------
    # Propagador
    # ---------------------------
    def _build_propagator(self):
        self.propagator = gmat.Construct("Propagator", "Prop")
        self.propagator.SetField("Type", "RungeKutta89")
        self.propagator.SetField("InitialStepSize", 60.0)

        fm = gmat.Construct("ForceModel", "FM")
        fm.SetField("CentralBody", "Earth")

        earth_grav = gmat.Construct("GravityField", "EarthGrav")
        earth_grav.SetField("Degree", 2)
        earth_grav.SetField("Order", 2)

        fm.AddForce(earth_grav)
        self.propagator.SetReference(fm)

    # ---------------------------
    # Propagacion
    # ---------------------------
    def propagate(self, duration_sec=86400, step_sec=60):
        # Asociar spacecraft al propagador
        self.propagator.SetReference(self.sc)
    
        # Comando Propagate
        prop_cmd = gmat.Construct("Propagate", "PropCmd")
        prop_cmd.SetReference(self.propagator)
        prop_cmd.SetReference(self.sc)
    
        states = []
        t = 0.0
    
        while t < duration_sec:
            prop_cmd.TakeAction("Step")
            state = self.sc.GetState().GetState()
            states.append(state)
            t += step_sec

        return states