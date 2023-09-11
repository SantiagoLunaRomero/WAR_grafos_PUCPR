from Jugadores.jugador import Jugador
import numpy as np

class AgenteRL(Jugador):
    def __init__(self, nombre, color, mision, alpha=0.1, gamma=0.9, epsilon=0.1):
        super().__init__(nombre, color, mision)
        self.alpha = alpha  # Tasa de aprendizaje
        self.gamma = gamma  # Factor de descuento
        self.epsilon = epsilon  # Probabilidad de exploración
        self.q_table = {}  # Tabla Q para almacenar los valores Q
        self.action_index_mapping = {} # Diccionario para mapear vectores de acción a índices
        self.nombres_paises = []

    def action_to_vector(self, action):
        # Inicializa un vector de acción con ceros
        action_vector = [0] * 46 # 4 acciones + 42 territorios

        # Traduce la acción en el vector de acción correspondiente
        if action['type'] == 'atacar':
            action_vector[0] = 255
            action_vector[action['territorio_origen'] + 4] = 255
            action_vector[action['territorio_destino'] + 4] = 255
        elif action['type'] == 'fortificar':
            action_vector[1] = 255
            action_vector[action['territorio'] + 4] = action['tropas']
        elif action['type'] == 'deslocar':
            action_vector[2] = 255
            action_vector[action['territorio_origen'] + 4] = 255
            action_vector[action['territorio_destino'] + 4] = action['tropas']
        elif action['type'] == 'pass':
            action_vector[3] = 255

        return action_vector
    
    def action_vector_to_index(self, action_vector):
        # Aquí puedes definir la lógica para convertir el vector de acción en un índice
        # Por ejemplo, puedes convertir el vector en una cadena y usar un diccionario para mapear las cadenas a índices
        action_str = ','.join(map(str, action_vector))
        if action_str not in self.action_index_mapping:
            self.action_index_mapping[action_str] = len(self.action_index_mapping)
        return self.action_index_mapping[action_str]


    def vector_to_action(self, action_vector):
        print("Converting action vector:", action_vector) # Print for debugging
        action = {}
        if action_vector[0] == 255:
            action['type'] = 'atacar'
            sub_vector = action_vector[4:]
            if 255 not in sub_vector:
                print("Error: 255 not found for 'atacar' action.") # Error message
                return None
            action['territorio_origen'] = self.nombres_paises[sub_vector.index(255)]
            action['territorio_destino'] = self.nombres_paises[sub_vector.index(255, sub_vector.index(255) + 1)]
        elif action_vector[1] == 255:
            action['type'] = 'fortificar'
            action['territorios'] = {self.nombres_paises[i]: tropas for i, tropas in enumerate(action_vector[4:]) if tropas > 0}
        elif action_vector[2] == 255:
            action['type'] = 'deslocar'
            sub_vector = action_vector[4:]
            if 255 not in sub_vector:
                print("Error: 255 not found for 'deslocar' action.") # Error message
                return None
            action['territorio_origen'] = self.nombres_paises[sub_vector.index(255)]
            action['territorio_destino'] = self.nombres_paises[sub_vector.index(255, sub_vector.index(255) + 1)]
            action['tropas'] = action_vector[sub_vector.index(255, sub_vector.index(255) + 1) + 4]
        elif action_vector[3] == 255:
            action['type'] = 'pass'
        else:
            print("Error: No valid action type found.") # Error message
            return None

        return action

    def state_to_key(self, state):
        # Aplanar la matriz en un vector
        state_vector = state.flatten()
        # Convertir el vector en una cadena, utilizando un delimitador para separar los elementos
        state_key = ','.join(map(str, state_vector))
        return state_key
    
    def puede_atacar(self, pais):
        # Un país puede atacar si tiene más de 2 tropas y tiene al menos un vecino controlado por otro jugador
        return pais.tropas > 2 and any(vecino.jugador != self for vecino in pais.vecinos)

    def elegir_accion(self, estado, fase,tablero):
        estado_key = self.state_to_key(estado)
        if estado_key not in self.q_table:
                self.q_table[estado_key] = np.zeros(46)
        else:
            # Redimensionar la tabla Q si es necesario
            if len(self.q_table[estado_key]) < len(self.action_index_mapping):
                self.q_table[estado_key] = np.resize(self.q_table[estado_key], len(self.action_index_mapping))

        if fase == 'reforzar':
            # Obtener los nombres de los territorios que el agente controla desde el tablero
            nombres_territorios_controlados = [nombre_pais for nombre_pais, p in tablero.paises.items() if p.jugador == self]

            # Obtener las tropas disponibles para distribuir
            tropas_disponibles = self.tropas_por_turno

            # Calcular los valores Q para cada territorio controlado
            q_values = [self.q_table[estado_key][self.nombres_paises.index(nombre_pais) + 4] for nombre_pais in nombres_territorios_controlados]

            # Distribuir las tropas en proporción a los valores Q
            total_q_value = sum(q_values)
            accion_vector = [0] * 46
            accion_vector[1] = 255  # Indicar que la acción es 'fortificar'
            if total_q_value > 0: # Asegúrate de que total_q_value no sea cero
                for nombre_pais, q_value in zip(nombres_territorios_controlados, q_values):
                    tropas_a_colocar = tropas_disponibles * (q_value / total_q_value)
                    accion_vector[self.nombres_paises.index(nombre_pais) + 4] = tropas_a_colocar
            else:
                # Aquí puedes manejar el caso en que total_q_value es cero.
                # Por ejemplo, podrías distribuir las tropas uniformemente entre los territorios controlados.
                tropas_por_territorio = tropas_disponibles // len(nombres_territorios_controlados)
                for nombre_pais in nombres_territorios_controlados:
                    accion_vector[self.nombres_paises.index(nombre_pais) + 4] = tropas_por_territorio

            return accion_vector


        elif fase == 'atacar':
            # Obtener los nombres de los territorios atacables (controlados por el jugador, con más de 2 tropas, y con al menos un vecino controlado por otro jugador)
            territorios_atacables = [nombre_pais for nombre_pais, p in tablero.paises.items() if p.jugador == self and p.tropas > 2 and any(tablero.paises[v].jugador != self for v in p.vecinos)]
            if not territorios_atacables:
                accion_vector = [0] * 46
                accion_vector[3] = 255
                return accion_vector

            max_q_value = float('-inf')
            mejor_territorio_origen = None
            mejor_territorio_destino = None
            for nombre_territorio_origen in territorios_atacables:
                territorio_origen = tablero.paises[nombre_territorio_origen]
                territorio_destino = next((v for v in territorio_origen.vecinos if tablero.paises[v].jugador != self), None)
                if territorio_destino is not None:
                    i = self.nombres_paises.index(nombre_territorio_origen)
                    j = self.nombres_paises.index(territorio_destino)
                    if self.q_table[estado_key][i + 4] > max_q_value:
                        max_q_value = self.q_table[estado_key][i + 4]
                        mejor_territorio_origen = i
                        mejor_territorio_destino = j

            accion_vector = [0] * 46
            accion_vector[0] = 255
            if mejor_territorio_origen is not None and mejor_territorio_destino is not None:
                accion_vector[mejor_territorio_origen + 4] = 255
                accion_vector[mejor_territorio_destino + 4] = 255

            return accion_vector

        elif fase == 'mover_tropas':
            # Obtener los nombres de los paises que el agente controla y desde los cuales puede mover tropas
            nombres_paises_origen = [nombre_pais for nombre_pais, p in tablero.paises.items() if p.jugador == self and p.tropas > 1]
            if not nombres_paises_origen:
                accion_vector = [0] * 46
                accion_vector[3] = 255
                return accion_vector

            max_q_value = float('-inf')
            mejor_pais_origen = None
            mejor_pais_destino = None
            for nombre_pais_origen in nombres_paises_origen:
                pais_origen = tablero.paises[nombre_pais_origen]
                # Obtener los territorios adyacentes que también son controlados por el agente
                nombres_paises_destino = [v for v in pais_origen.vecinos if tablero.paises[v].jugador == self]
                
                # Si no hay países destino viables para este país origen, continuar con la siguiente iteración
                if not nombres_paises_destino:
                    continue

                for nombre_pais_destino in nombres_paises_destino:
                    i = self.nombres_paises.index(nombre_pais_origen)
                    j = self.nombres_paises.index(nombre_pais_destino)
                    if self.q_table[estado_key][j + 4] > max_q_value:
                        max_q_value = self.q_table[estado_key][j + 4]
                        mejor_pais_origen = i
                        mejor_pais_destino = j

            # Si no encontramos ningún país destino viable, devolver acción de "pasar"
            if mejor_pais_origen is None and mejor_pais_destino is None:
                accion_vector = [0] * 46
                accion_vector[3] = 255
                return accion_vector

            accion_vector = [0] * 46
            accion_vector[2] = 255  # Indicar que la acción es 'deslocar'
            accion_vector[mejor_pais_origen + 4] = 255
            accion_vector[mejor_pais_destino + 4] = 255
            return accion_vector

        elif fase == 'pass':
            # Si la única acción permitida es 'pass', simplemente devolvemos esa acción
            accion_vector = [0] * 46
            accion_vector[3] = 255
            return accion_vector

    def aprender(self, transicion):
        estado, accion_vector, recompensa, estado_siguiente = transicion
        estado_key = self.state_to_key(estado)
        estado_siguiente_key = self.state_to_key(estado_siguiente)
        
        # Convertir el vector de acción en un índice de acción
        accion_index = self.action_vector_to_index(accion_vector)

        # Asegúrate de que las tablas Q estén inicializadas para ambos estados con el tamaño correcto
        if estado_key not in self.q_table:
            self.q_table[estado_key] = np.zeros(46)
        if estado_siguiente_key not in self.q_table:
            self.q_table[estado_siguiente_key] = np.zeros(46)

        q_value_next = np.max(self.q_table[estado_siguiente_key])
        self.q_table[estado_key][accion_index] += self.alpha * (recompensa + self.gamma * q_value_next - self.q_table[estado_key][accion_index])

    def aplicar_accion_reforzar(self, accion_vector, tablero):
        print("Accion vector:", accion_vector)
        accion = self.vector_to_action(accion_vector)
        print("Acción resultante:", accion)  # Agregar esta línea
        # Asume que la acción es un diccionario con 'type': 'fortificar' y 'territorios': un diccionario con índices y cantidades de tropas
        recompensa = 0
        for territorio, tropas in accion['territorios'].items():
            pais = tablero.paises[territorio]
            pais.tropas += tropas
            recompensa += tropas # La recompensa puede ser igual a la cantidad total de tropas reforzadas

        # Obtener el estado siguiente
        tablero.actualizar_grafo()
        tablero.crear_matriz_estado(tablero.vector_fase("reforzar"),self)
        estado_siguiente = tablero.matriz_historial[-1]

        return recompensa, estado_siguiente


    def reforzar(self, tablero):
        self.nombres_paises = list(tablero.paises.keys())
        # Obtener el estado actual
        estado_actual = tablero.matriz_historial[-1]

        # Elegir la acción de reforzar usando la política del agente (esto puede ser ε-greedy, por ejemplo)
        accion = self.elegir_accion(estado_actual, fase='reforzar', tablero=tablero)

        # Aplicar la acción y obtener la recompensa y el estado siguiente
        recompensa, estado_siguiente = self.aplicar_accion_reforzar(accion, tablero)

        # Aprender de la transición (esto puede ser Q-learning, por ejemplo)
        self.aprender((estado_actual, accion, recompensa, estado_siguiente))


    def aplicar_accion_atacar(self,  accion_vector, tablero):
        print("Vector de acción atacar: ", accion_vector)  # Agregar esta línea
        # Convertir el vector de acción a una acción concreta
        accion = self.vector_to_action(accion_vector)
        print("Acción resultante:", accion)  # Agregar esta línea
        if accion['type'] == 'pass':
            recompensa = 0
            tablero.actualizar_grafo()
            tablero.crear_matriz_estado(tablero.vector_fase("atacar"),self)
            estado_siguiente = tablero.matriz_historial[-1] # Puedes definir esto como sea apropiado
            return recompensa, estado_siguiente

        # Asume que la acción es un diccionario con 'type': 'atacar', 'territorio_origen': origen, 'territorio_destino': destino
        pais_origen = tablero.paises[accion['territorio_origen']]
        pais_destino = tablero.paises[accion['territorio_destino']]

        # Realizar la batalla
        tablero.batalla(pais_origen, pais_destino)

        # Calcular la recompensa (puede ser personalizada según la lógica del juego)
        recompensa = pais_destino.tropas if pais_destino.jugador == pais_origen.jugador else -pais_origen.tropas

        # Obtener el estado siguiente
        tablero.actualizar_grafo()
        tablero.crear_matriz_estado(tablero.vector_fase("reforzar"),self)
        estado_siguiente = tablero.matriz_historial[-1]

        return recompensa, estado_siguiente

    def atacar(self, tablero):
        # Obtener el estado actual
        estado_actual = tablero.matriz_historial[-1]

        # Elegir la acción de atacar usando la política del agente
        accion = self.elegir_accion(estado_actual, fase='atacar',tablero=tablero)

        # Aplicar la acción y obtener la recompensa y el estado siguiente
        recompensa, estado_siguiente = self.aplicar_accion_atacar(accion, tablero)

        # Aprender de la transición
        self.aprender((estado_actual, accion, recompensa, estado_siguiente))


    def aplicar_accion_mover_tropas(self, accion_vector, tablero):
        print("Vector de acción mover_tropas: ", accion_vector)  # Agregar esta línea
        # Convertir el vector de acción a una acción concreta
        accion = self.vector_to_action(accion_vector)
        print("Acción resultante:", accion) 
        if accion['type'] == 'pass':
            recompensa = 0
            tablero.actualizar_grafo()
            tablero.crear_matriz_estado(tablero.vector_fase("mover"),self)
            estado_siguiente = tablero.matriz_historial[-1] # Puedes definir esto como sea apropiado
            return recompensa, estado_siguiente

        # Asume que la acción es un diccionario con 'type': 'deslocar', 'territorio_origen': origen, 'territorio_destino': destino, 'tropas': cantidad
        # Obtener la cantidad de tropas en el territorio origen
        tropas_en_origen = tablero.paises[accion['territorio_origen']].tropas

        # Calcular las tropas a mover, asegurándose de dejar al menos una tropa en el origen
        tropas_a_mover = min(accion['tropas'], tropas_en_origen - 1)

        # Mover las tropas
        tablero.mover_tropas(accion['territorio_origen'], accion['territorio_destino'], tropas_a_mover)

        # Actualizar la recompensa
        recompensa = tropas_a_mover

        # Calcular la recompensa (puede ser personalizada según la lógica del juego)
        recompensa = accion['tropas'] # Por ejemplo, la recompensa es igual a la cantidad de tropas movidas

        # Obtener el estado siguiente
        tablero.actualizar_grafo()
        tablero.crear_matriz_estado(tablero.vector_fase("reforzar"),self)
        estado_siguiente = tablero.matriz_historial[-1]

        return recompensa, estado_siguiente

    def mover_tropas(self, tablero):
        # Obtener el estado actual
        estado_actual = tablero.matriz_historial[-1]

        # Elegir la acción de mover tropas usando la política del agente
        accion = self.elegir_accion(estado_actual, fase='mover_tropas', tablero=tablero)

        # Aplicar la acción y obtener la recompensa y el estado siguiente
        recompensa, estado_siguiente = self.aplicar_accion_mover_tropas(accion, tablero)

        # Aprender de la transición
        self.aprender((estado_actual, accion, recompensa, estado_siguiente))
