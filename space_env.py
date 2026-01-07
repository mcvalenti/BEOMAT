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
        
        # 1. Crear ForceModel
        self.force_model = gmat.Construct("ForceModel", f"FM_{name}")
        # 2. Crear el integrador (ej: PrinceDormand78 o RungeKutta89)
        self.integrator = gmat.Construct("PrinceDormand78", f"Int_{name}")
        # 3. Crear el PropSetup 
        self.gmat_prop = gmat.Construct("PropSetup", f"Prop_{name}")
        # 4. Vincular todo
        self.gmat_prop.SetReference(self.integrator)
        self.gmat_prop.SetReference(self.force_model)
        
        # Configuracion por defecto si no se provee una
        if config is None:
            config = {'gravity': 'Earth', 'degree': 0, 'order': 0}
        
        self.config = config
        self._setup_forces(config)

    def _setup_forces(self, config):
        """Configura el modelo de fuerzas usando enteros nativos para Degree/Order."""
        gmat = get_gmat()

        if 'gravity' in config:
            body = config['gravity']
            if config.get('degree', 0) > 0:
                grav = gmat.Construct("GravityField", f"Grav_{body}")
                
                grav.SetField("BodyName", body)
                # El Test 1 demostró que esto debe ser int
                grav.SetField("Degree", int(config['degree']))
                grav.SetField("Order", int(config['order']))
            else:
                grav = gmat.Construct("PointMassForce", f"PM_{body}")
                grav.SetField("BodyName", body)
            
            self.force_model.AddForce(grav)

        # if config.get('drag', False):
        #     atmos = gmat.Construct("ExponentialAtmosphere")
        #     drag = gmat.Construct("DragForce", f"Drag_{self.name}")
        #     drag.SetReference(atmos)
        #     self.force_model.AddForce(drag)

    def run(self, satellite, duration_sec, step_size=60):
        gmat = get_gmat()
        
        # 1. En lugar de AddPropObject, usamos SetField en el ForceModel
        # Esto le dice al modelo de fuerzas que el satélite es el cuerpo a mover
        self.force_model.SetField("PointMasses", f"{{{satellite.name}}}") 
        
        # 2. Vincular al PropSetup
        self.gmat_prop.AddPropObject(satellite.gmat_obj)
        
        # 3. Inicializar
        gmat.Initialize()
        
        internal_prop = self.gmat_prop.GetPropagator()
        data = []
        
        # Extraer estado inicial
        pos_0 = [float(satellite.gmat_obj.GetField("X")), 
                float(satellite.gmat_obj.GetField("Y")), 
                float(satellite.gmat_obj.GetField("Z"))]
        data.append([0.0] + pos_0)

        # 4. Bucle de propagación
        for i in range(1, int(duration_sec / step_size) + 1):
            internal_prop.Step(float(step_size))
            
            # Sincronización manual: Leemos directamente del integrador
            # Esto extrae el vector de estado (X, Y, Z, Vx, Vy, Vz)
            state = internal_prop.GetState() 
            
            # Extraemos X, Y, Z (índices 0, 1, 2)
            pos = [state[0], state[1], state[2]]
            data.append([float(i * step_size)] + pos)
            
        return np.array(data)

    # def run(self, satellite, duration_sec, step_size=60):
    #     gmat = get_gmat()
               
    #     # 2. Vincular al PropSetup e Inicializar
    #     self.gmat_prop.AddPropObject(satellite.gmat_obj)
    #     gmat.Initialize()
        
    #     # 3. Obtener el integrador y el satélite
    #     internal_prop = self.gmat_prop.GetPropagator()
    #     sat_obj = satellite.gmat_obj
        
    #     data = []
    #     current_time = 0.0
        
    #     for _ in range(0, int(duration_sec), step_size):
    #         # Propagar
    #         internal_prop.Step(float(step_size))
            
    #         current_time += step_size
    #         # SINCRONIZACIÓN MANUAL
    #         # Si no hay UpdateObjects, forzamos a GMAT a refrescar el estado
    #         # moviendo el puntero de tiempo del satélite
    #         gmat.Update(sat_obj) 
            
    #         # Extraer posición
    #         pos = [
    #             float(sat_obj.GetField("X")),
    #             float(sat_obj.GetField("Y")),
    #             float(sat_obj.GetField("Z"))
    #         ]
    #         data.append([current_time] + pos)
            
    #     return np.array(data)

  