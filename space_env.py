import numpy as np
from gmat_env import get_gmat

# Get GMAT's motor instance
gmat = get_gmat()

class Satellite:
    def __init__(self, name="MySat"):
        self.name = name
        self.gmat_obj = gmat.Construct("Spacecraft", name)
        
    def set_keplerian(self, **elements):
        """Configure kepelerian elements"""
        self.gmat_obj.SetField("CoordinateSystem", "EarthMJ2000Eq")
        self.gmat_obj.SetField("DisplayStateType", "Keplerian")
        
        mappings = {
            'sma': 'SMA', 
            'ecc': 'ECC', 
            'inc': 'INC', 
            'raan': 'RAAN', 
            'aop': 'AOP', 
            'ta': 'TA'
        }
        
        for key, value in elements.items():
            gmat_key = mappings.get(key.lower())
            if gmat_key:
                # GMAT espera un 'double' de C++, que en Python es float.
                try:
                    self.gmat_obj.SetReal(gmat_key, float(value))
                except AttributeError:
                    # En algunas versiones muy específicas, si SetReal falla, 
                    # intentamos SetField pero sin convertir a string
                    self.gmat_obj.SetField(gmat_key, float(value))
        
        gmat.Initialize()

class Propagator:
    def __init__(self, name="MainProp", config=None):
        gmat = get_gmat()
        self.name = name
        
        # ==============
        #  ForceModel
        # ==============
        self.force_model = gmat.Construct("ForceModel", f"FM_{name}")
        self.earthgrav = gmat.Construct("GravityField")
        self.earthgrav.SetField("PotentialFile","JGM2.cof")
        self.earthgrav.SetField("BodyName","Earth")
        self.earthgrav.Help()
        self.force_model.AddForce(self.earthgrav)
        # ==============
        #  Propagator
        # ==============
        self.gmat_prop = gmat.Construct("PropSetup", f"Prop_{name}")
        # ==============
        #  Integrator
        # ==============
        self.integrator = gmat.Construct("PrinceDormand78", f"Int_{name}")
        
        # Assign the integrator and force model
        self.gmat_prop.SetReference(self.integrator)
        self.gmat_prop.SetReference(self.force_model)
        
    #     # Configuracion por defecto si no se provee una
    #     if config is None:
    #         config = {'gravity': 'Earth', 'degree': 0, 'order': 0}
        
    #     self.config = config
    #     self._setup_forces(config)

    # def _setup_forces(self, config):
    #     """Configura el modelo de fuerzas usando enteros nativos para Degree/Order."""
    #     gmat = get_gmat()

    #     if 'gravity' in config:
    #         body = config['gravity']
    #         if config.get('degree', 0) > 0:
    #             grav = gmat.Construct("GravityField", f"Grav_{body}")
                
    #             grav.SetField("BodyName", body)
    #             # El Test 1 demostró que esto debe ser int
    #             grav.SetField("Degree", int(config['degree']))
    #             grav.SetField("Order", int(config['order']))
    #         else:
    #             grav = gmat.Construct("PointMassForce", f"PM_{body}")
    #             grav.SetField("BodyName", body)
            
    #         self.force_model.AddForce(grav)

    def run(self, satellite, duration_sec, step_size=60):
        gmat = get_gmat()
        # Top level initialization
        gmat.Initialize()
        sat_obj = satellite.gmat_obj       
        # Spacecraft that is propagated
        self.gmat_prop.AddPropObject(sat_obj)
        self.gmat_prop.PrepareInternals()
        
        # Refresh the integrator reference
        internal_prop = self.gmat_prop.GetPropagator()
       
        data = []
        current_time = 0.0
        
        for _ in range(0, int(duration_sec), step_size):
            # Propagar
            internal_prop.Step(float(step_size)) # take a step
            
            # Get Iterator state
            state = internal_prop.GetState() # To force sat_obj Update
            
            # Force step iteration
            sat_obj.SetField("X", state[0])
            sat_obj.SetField("Y", state[1])
            sat_obj.SetField("Z", state[2])
            sat_obj.SetField("VX", state[3])
            sat_obj.SetField("VY", state[4])
            sat_obj.SetField("VZ", state[5])
            
            pos = [state[0], state[1], state[2]]
            data.append([current_time] + pos)
            
            current_time += step_size
            
        return np.array(data)

  