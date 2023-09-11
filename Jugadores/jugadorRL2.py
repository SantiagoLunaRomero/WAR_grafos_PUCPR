from Jugadores.jugador import Jugador
import numpy as np
import random
import pickle
class AgenteRL2(Jugador):
    def __init__(self, nombre, color, mision, alpha=0.1, gamma=0.9, epsilon=0.2, epsilon_decay=0.995, epsilon_min=0.01):
        super().__init__(nombre, color, mision)
        self.alpha = alpha  # Tasa de aprendizaje
        self.gamma = gamma  # Factor de descuento
        self.epsilon = epsilon  # Probabilidad de exploración
        self.epsilon_decay = epsilon_decay  # Factor de decaimiento de epsilon
        self.epsilon_min = epsilon_min  # Valor mínimo para epsilon
        self.q_table = {}  # Tabla Q para almacenar los valores Q
        self.cargar_q_table()
        self.action_index_mapping = {} # Diccionario para mapear vectores de acción a índices
        self.nombres_paises = []

    def informar_victoria(self,tablero):
        recompensa = 100  # Recompensa por ganar

        estado_actual = tablero.matriz_historial[-1] # Tomar el último estado conocido
        accion = [0] * 46  # Puedes definir una acción neutra, como "pass", para la actualización
        self.aprender((estado_actual, accion, recompensa, estado_actual))

    def informar_perdida(self,tablero,recompensa = -100):
        #recompensa = -100  # Penalización por perder
        estado_actual = tablero.matriz_historial[-1]# Tomar el último estado conocido
        accion = [0] * 46  # Puedes definir una acción neutra, como "pass", para la actualización
        self.aprender((estado_actual, accion, recompensa, estado_actual))

    def guardar_q_table(self, filename="q_table.pkl"):
        with open(filename, "wb") as file:
            pickle.dump(self.q_table, file)
    def cargar_q_table(self, filename="q_table.pkl"):
        try:
            with open(filename, "rb") as file:
                self.q_table = pickle.load(file)
        except FileNotFoundError:
            print(f"No se encontró el archivo {filename}. Se usará una tabla Q vacía.")


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
        action_str = ','.join(map(str, action_vector))
        if action_str not in self.action_index_mapping:
            index = len(self.action_index_mapping)
            self.action_index_mapping[action_str] = index

            sample_state = list(self.q_table.keys())[0] if self.q_table else None
            if sample_state and index >= len(self.q_table[sample_state]):
                for key in self.q_table:
                    self.q_table[key] = np.append(self.q_table[key], 0)
        else:
            index = self.action_index_mapping[action_str]
            
        return index


    def vector_to_action(self, action_vector):
        print("Converting action vector:", action_vector) # Print for debugging
        action = {}
        if action_vector[0] == 255:
            action['type'] = 'atacar'
            sub_vector = action_vector[4:]
            if 255 not in sub_vector:
                print("Error: 255 not found for 'atacar' action.") # Error message
                action['type'] = 'pass' # Default action
                return action
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
                action['type'] = 'pass' # Default action
                return action
            action['territorio_origen'] = self.nombres_paises[sub_vector.index(255)]
            action['territorio_destino'] = self.nombres_paises[sub_vector.index(255, sub_vector.index(255) + 1)]
            action['tropas'] = action_vector[sub_vector.index(255, sub_vector.index(255) + 1) + 4]
        elif action_vector[3] == 255:
            action['type'] = 'pass'
        else:
            print("Error: No valid action type found.") # Error message
            action['type'] = 'pass' # Default action

        return action

    def state_to_key(self, state):
        # Aplanar la matriz en un vector
        state_vector = state.flatten()
        # Convertir el vector en una cadena, utilizando un delimitador para separar los elementos
        state_key = ','.join(map(str, state_vector))
        return state_key
    
    def puede_atacar(self, pais,tablero):
        # Un país puede atacar si tiene más de 2 tropas y tiene al menos un vecino controlado por otro jugador
        return pais.tropas > 2 and any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)


    def accion_aleatoria_reforzar(self, tablero):
        # Seleccionar un territorio al azar para reforzar
        territorios_controlados = [nombre_pais for nombre_pais, p in tablero.paises.items() if p.jugador == self]
        
        # Si no hay territorios controlados, retornar una acción de 'pass'
        if not territorios_controlados:
            accion_vector = [0] * 46
            accion_vector[3] = 255  # Acción de 'pass'
            return accion_vector

        territorio_seleccionado = random.choice(territorios_controlados)
        accion_vector = [0] * 46
        accion_vector[1] = 255  # Indicar que la acción es 'fortificar'
        accion_vector[self.nombres_paises.index(territorio_seleccionado) + 4] = self.tropas_por_turno
        return accion_vector


    ##ACCIONES ALEATORIAS PARA ATACAR, REFORZAR, MOVER TROPAS

    def accion_aleatoria_atacar(self, tablero):
        territorios_atacables = [nombre_pais for nombre_pais, p in tablero.paises.items() if p.jugador == self and self.puede_atacar(p,tablero)]
        if not territorios_atacables:
            accion_vector = [0] * 46
            accion_vector[3] = 255
            return accion_vector

        territorio_origen = random.choice(territorios_atacables)
        territorio_destino = random.choice([v for v in tablero.paises[territorio_origen].vecinos if tablero.paises[v].jugador != self])

        accion_vector = [0] * 46
        accion_vector[0] = 255
        accion_vector[self.nombres_paises.index(territorio_origen) + 4] = 255
        accion_vector[self.nombres_paises.index(territorio_destino) + 4] = 255

        return accion_vector

    def accion_aleatoria_mover_tropas(self, tablero):
        nombres_paises_origen = [nombre_pais for nombre_pais, p in tablero.paises.items() if p.jugador == self and p.tropas > 1]
        if not nombres_paises_origen:
            accion_vector = [0] * 46
            accion_vector[3] = 255
            return accion_vector

        pais_origen = random.choice(nombres_paises_origen)
        
        vecinos_posibles = [v for v in tablero.paises[pais_origen].vecinos if tablero.paises[v].jugador == self]
        if not vecinos_posibles:
            # No hay vecinos disponibles para mover tropas, puedes decidir qué hacer en este caso
            # Por ejemplo, simplemente pasar el turno:
            accion_vector = [0] * 46
            accion_vector[3] = 255
            return accion_vector
        pais_destino = random.choice(vecinos_posibles)

        accion_vector = [0] * 46
        accion_vector[2] = 255
        accion_vector[self.nombres_paises.index(pais_origen) + 4] = 255
        accion_vector[self.nombres_paises.index(pais_destino) + 4] = 255

        return accion_vector

    def mask_for_phase(self, fase):
        # Retorna un array booleano donde True indica una acción válida y False una acción inválida
        if fase == 'reforzar':
            return [False, True, False, False] + [True] * 42
        elif fase == 'atacar':
            return [True, False, False, True] + [False] * 42
        elif fase == 'mover_tropas':
            return [False, False, True, True] + [False] * 42
        else:
            return [False, False, False, True] + [False] * 42
        
    def index_to_action_vector(self, action_index):
        # Crear un vector de acción con todos los elementos en cero
        action_vector = [0] * 46
        
        # Asumiendo que el índice de acción se corresponde directamente con una posición en el vector
        action_vector[action_index] = 255
        return action_vector


    def elegir_accion(self, estado, fase, tablero):
        estado_key = self.state_to_key(estado)
        if estado_key not in self.q_table:
            self.q_table[estado_key] = np.random.uniform(low=-0.01, high=0.01, size=46)

        # Comprobar y corregir si la longitud de self.q_table[estado_key] es menor que 46
        if len(self.q_table[estado_key]) < 46:
            self.q_table[estado_key] = np.append(self.q_table[estado_key], [0] * (46 - len(self.q_table[estado_key])))

        # ε-greedy policy
        if np.random.rand() < self.epsilon:
            if fase == 'reforzar':
                return self.accion_aleatoria_reforzar(tablero)
            elif fase == 'atacar':
                return self.accion_aleatoria_atacar(tablero)
            elif fase == 'mover_tropas':
                return self.accion_aleatoria_mover_tropas(tablero)
            else:
                accion_vector = [0] * 46
                accion_vector[3] = 255
                return accion_vector
        else:
            mask = self.mask_for_phase(fase)
            if len(self.q_table[estado_key]) > 46:
                self.q_table[estado_key] = self.q_table[estado_key][:46]

            valid_q_values = np.where(mask, self.q_table[estado_key], float('-inf'))
            action_index = np.argmax(valid_q_values)
            # Convertir el índice de acción a un vector de acción
            return self.index_to_action_vector(action_index)


    def aprender(self, transicion):
        estado_actual, accion_vector, recompensa, estado_siguiente = transicion

        # Convertir los estados y acciones a sus representaciones de clave
        estado_key = self.state_to_key(estado_actual)
        estado_siguiente_key = self.state_to_key(estado_siguiente)
        accion_index = self.action_vector_to_index(accion_vector)

        # Inicializar el estado en la tabla Q si aún no existe
        if estado_key not in self.q_table:
            self.q_table[estado_key] = [0] * len(self.action_index_mapping)
        if estado_siguiente_key not in self.q_table:
            self.q_table[estado_siguiente_key] = [0] * len(self.action_index_mapping)

        # Extender la tabla Q para el estado actual si es necesario
        if accion_index >= len(self.q_table[estado_key]):
            self.q_table[estado_key] = np.append(self.q_table[estado_key], [0] * (accion_index - len(self.q_table[estado_key]) + 1))

        # Imprimir información de diagnóstico
        print("Estado actual:", estado_key)
        print("Acción:", accion_index)
        print("Tamaño de self.q_table[estado_key]:", len(self.q_table[estado_key]))

        # Actualizar la tabla Q con la fórmula Q-learning
        q_value_next = np.max(self.q_table[estado_siguiente_key])
        self.q_table[estado_key][accion_index] += self.alpha * (recompensa + self.gamma * q_value_next - self.q_table[estado_key][accion_index])

        # Decrementar epsilon si es necesario
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


    def aplicar_accion_reforzar(self, accion_vector, tablero):
        print("Accion vector:", accion_vector)
        accion = self.vector_to_action(accion_vector)
        print("Acción resultante:", accion)

        recompensa = 0

        if accion['type'] == 'fortificar':
            for territorio, tropas in accion['territorios'].items():
                pais = tablero.paises[territorio]
                pais.tropas += tropas

                # Recompensa si reforzamos territorios fronterizos o con vecinos controlados por otros jugadores
                if any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos):
                    recompensa += 5 * tropas
                else:
                    recompensa -= 2 * tropas  # Penalización por reforzar territorios ya bien defendidos

        tablero.actualizar_grafo()
        tablero.crear_matriz_estado(tablero.vector_fase("reforzar"), self)
        estado_siguiente = tablero.matriz_historial[-1]

        return recompensa, estado_siguiente


    def reforzar(self, tablero):
        self.nombres_paises = list(tablero.paises.keys())
        # Obtener el estado actual
        estado_actual = tablero.matriz_historial[-1]

        # Elegir la acción de reforzar usando la política del agente
        accion_vector = self.elegir_accion(estado_actual, fase='reforzar', tablero=tablero)
        accion = self.vector_to_action(accion_vector)  # Convertir el vector de acción a un diccionario de acción

        # Aplicar la acción y obtener la recompensa y el estado siguiente
        recompensa, estado_siguiente = self.aplicar_accion_reforzar(accion_vector, tablero)

        if accion['type'] == 'fortificar' and not accion['territorios']:
            recompensa = -10  # Penalización por no reforzar

        # Aprender de la transición
        self.aprender((estado_actual, accion_vector, recompensa, estado_siguiente))


    def aplicar_accion_atacar(self, accion_vector, tablero):
        print("Vector de acción atacar: ", accion_vector)
        accion = self.vector_to_action(accion_vector)
        print("Acción resultante:", accion)

        if accion['type'] == 'pass':
            recompensa = 0
            tablero.actualizar_grafo()
            tablero.crear_matriz_estado(tablero.vector_fase("atacar"), self)
            estado_siguiente = tablero.matriz_historial[-1]
            return recompensa, estado_siguiente

        pais_origen = tablero.paises[accion['territorio_origen']]
        pais_destino = tablero.paises[accion['territorio_destino']]
        jugador_destino_anterior = pais_destino.jugador

        tablero.batalla(pais_origen, pais_destino)

        recompensa = 0
        # Recompensa por conquistar un territorio
        if pais_destino.jugador == self and jugador_destino_anterior != self:
            recompensa += 10

            # Recompensa adicional si se conquista un continente completo
            if self.conquisto_continente(pais_destino, tablero):
                recompensa += 20

        # Penalización por tropas perdidas
        if pais_destino.jugador == self:
            recompensa -= (pais_origen.tropas * 2)  # El atacante perdió la batalla
        else:
            recompensa -= pais_destino.tropas  # El defensor perdió la batalla

        tablero.actualizar_grafo()
        tablero.crear_matriz_estado(tablero.vector_fase("reforzar"), self)
        estado_siguiente = tablero.matriz_historial[-1]

        return recompensa, estado_siguiente
    
    def conquisto_continente(self, pais, tablero):
        # Crear un mapeo de continentes a la lista de países
        continentes = {}
        for p in tablero.paises.values():
            if p.continente not in continentes:
                continentes[p.continente] = []
            continentes[p.continente].append(p.nombre)

        # Usar el mapeo para verificar si el jugador ha conquistado todo el continente al que pertenece el país.
        nombre_continente = pais.continente
        for nombre_pais in continentes[nombre_continente]:
            if tablero.paises[nombre_pais].jugador != self:
                return False
        return True

    def atacar(self, tablero):
        # Obtener el estado actual
        estado_actual = tablero.matriz_historial[-1]

        # Elegir la acción de atacar usando la política del agente
        accion_vector = self.elegir_accion(estado_actual, fase='atacar',tablero=tablero)
        accion = self.vector_to_action(accion_vector)  # Convertir el vector de acción a un diccionario de acción

        # Aplicar la acción y obtener la recompensa y el estado siguiente
        recompensa, estado_siguiente = self.aplicar_accion_atacar(accion_vector, tablero)

        if accion['type'] == 'pass' and any(self.puede_atacar(p,tablero) for p in tablero.paises.values() if p.jugador == self):
            recompensa = -15  # Penalización por no atacar cuando es posible

        # Aprender de la transición
        self.aprender((estado_actual, accion_vector, recompensa, estado_siguiente))


    def aplicar_accion_mover_tropas(self, accion_vector, tablero):
        print("Vector de acción mover_tropas: ", accion_vector)  # Agregar esta línea
        # Convertir el vector de acción a una acción concreta
        accion = self.vector_to_action(accion_vector)
        print("Acción resultante:", accion) 
        if accion['type'] == 'pass':
            recompensa = 0
            tablero.actualizar_grafo()
            tablero.crear_matriz_estado(tablero.vector_fase("mover"), self)
            estado_siguiente = tablero.matriz_historial[-1] # Puedes definir esto como sea apropiado
            return recompensa, estado_siguiente

        # Asume que la acción es un diccionario con 'type': 'deslocar', 'territorio_origen': origen, 'territorio_destino': destino, 'tropas': cantidad
        # Obtener la cantidad de tropas en el territorio origen
        tropas_en_origen = tablero.paises[accion['territorio_origen']].tropas

        # Calcular las tropas a mover, asegurándose de dejar al menos una tropa en el origen
        tropas_a_mover = min(accion['tropas'], tropas_en_origen - 1)

        # Mover las tropas
        tablero.mover_tropas(accion['territorio_origen'], accion['territorio_destino'], tropas_a_mover)

        # Base recompensa
        recompensa = tropas_a_mover

        pais_destino = tablero.paises[accion['territorio_destino']]
        pais_origen = tablero.paises[accion['territorio_origen']]

        # Recompensa por mover tropas a territorios fronterizos o vulnerables
        if self.es_territorio_vulnerable(pais_destino, tablero):
            recompensa += 5

        # Penalización por movimiento innecesario de tropas
        if not self.es_territorio_vulnerable(pais_origen, tablero) and not self.es_territorio_vulnerable(pais_destino, tablero):
            recompensa -= 3

        # Obtener el estado siguiente
        tablero.actualizar_grafo()
        tablero.crear_matriz_estado(tablero.vector_fase("reforzar"), self)
        estado_siguiente = tablero.matriz_historial[-1]

        return recompensa, estado_siguiente

    def es_territorio_vulnerable(self, pais, tablero):
        # Consideramos un territorio como vulnerable si tiene vecinos controlados por otros jugadores
        return any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)


    def mover_tropas(self, tablero):
        # Obtener el estado actual
        estado_actual = tablero.matriz_historial[-1]

        # Elegir la acción de mover tropas usando la política del agente
        accion_vector = self.elegir_accion(estado_actual, fase='mover_tropas', tablero=tablero)
        accion = self.vector_to_action(accion_vector)  # Convertir el vector de acción a un diccionario de acción

        # Aplicar la acción y obtener la recompensa y el estado siguiente
        recompensa, estado_siguiente = self.aplicar_accion_mover_tropas(accion_vector, tablero)

        if accion['type'] == 'pass':
            recompensa = -5  # Penalización por no mover tropas

        # Aprender de la transición
        self.aprender((estado_actual, accion_vector, recompensa, estado_siguiente))

