import numpy as np
import random
from collections import deque
from tensorflow import keras
from tensorflow.keras.layers import Input, Conv2D, Dense, Flatten, Concatenate
from tensorflow.keras.models import Model
from Jugadores.jugador import Jugador
import math



class FusionAgenteDQN(Jugador):

    def __init__(self, nombre, color, mision, alpha=0.1, gamma=0.6, epsilon=0.8, epsilon_decay=0.998, epsilon_min=0.01):
        super().__init__(nombre, color, mision)
        
        # Parámetros del algoritmo
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.recompensa_acumulada = 0
        
        # Historial y mapeo de acciones
        self.historial_estados = deque(maxlen=10)
        self.nombres_paises = []

        self.debug = True
        # Creación de modelos
        self.target_model = self.create_multi_output_model()  # Inicializar siempre target_model primero
        try:
            self.load_model("DQN_V1.h5")
            self.debug_print("Modelo cargado desde archivo.")
        except (OSError, ValueError):
            self.model = self.create_multi_output_model()
            self.update_target_model()
            self.debug_print("Modelo creado desde cero.")


    def debug_print(self, message):
        if self.debug:
            print(message) 

    # ----------------------- Métodos relacionados con el modelo -----------------------

    def create_multi_output_model(self):
        """Crea y retorna el modelo DQN con múltiples salidas."""
        input_caracteristicas = Input(shape=(6, 61, 10), name="input_caracteristicas")
        input_adyacencia = Input(shape=(42, 42), name="input_adyacencia")

        # Capas convolucionales para características
        x_features = Conv2D(32, (3, 3), activation='relu')(input_caracteristicas)
        x_features = Conv2D(64, (3, 3), activation='relu')(x_features)
        x_features = Flatten()(x_features)

        # Añade una dimensión extra a la matriz de adyacencia
        x_adjacency = keras.layers.Reshape((42, 42, 1))(input_adyacencia)

        # Capas convolucionales para matriz de adyacencia
        x_adjacency = Conv2D(32, (3, 3), activation='relu')(x_adjacency)
        x_adjacency = Conv2D(64, (3, 3), activation='relu')(x_adjacency)
        x_adjacency = Flatten()(x_adjacency)

        combined = Concatenate()([x_features, x_adjacency])
        x = Dense(256, activation='relu')(combined)

        # Bloque de capas densas antes de cada salida
        def dense_block(input_tensor, units):
            x = Dense(units[0], activation='relu')(input_tensor)
            x = Dense(units[1], activation='relu')(x)
            if len(units)==3:
                x = Dense(units[2], activation='linear')(x)
            return x

        # Salidas con bloques densos
        reforzar_territorio = Dense(42, activation='softmax', name='reforzar_territorio')(dense_block(x, [128,128]))
        num_tropas_reforzar = Dense(1, activation='linear', name='num_tropas_reforzar')(dense_block(x, [128,64,32]))
        territorio_origen_atacar = Dense(42, activation='softmax', name='territorio_origen_atacar')(dense_block(x, [128,128]))
        territorio_destino_atacar = Dense(42, activation='softmax', name='territorio_destino_atacar')(dense_block(x, [128,128]))
        territorio_origen_mover = Dense(42, activation='softmax', name='territorio_origen_mover')(dense_block(x, [128,128]))
        territorio_destino_mover = Dense(42, activation='softmax', name='territorio_destino_mover')(dense_block(x, [128,128]))
        num_tropas_mover = Dense(1, activation='linear', name='num_tropas_mover')(dense_block(x, [128,64,32]))

        model = Model(inputs=[input_caracteristicas, input_adyacencia], 
                    outputs=[reforzar_territorio, num_tropas_reforzar, territorio_origen_atacar, territorio_destino_atacar, territorio_origen_mover, territorio_destino_mover, num_tropas_mover])
        
        model.compile(optimizer='adam', 
                    loss={'reforzar_territorio': 'categorical_crossentropy', 
                            'num_tropas_reforzar': 'mse', 
                            'territorio_origen_atacar': 'categorical_crossentropy', 
                            'territorio_destino_atacar': 'categorical_crossentropy',
                            'territorio_origen_mover': 'categorical_crossentropy',
                            'territorio_destino_mover': 'categorical_crossentropy',
                            'num_tropas_mover': 'mse'})
        return model

    def update_target_model(self):
        """Actualiza los pesos del modelo objetivo con los pesos del modelo principal."""
        self.target_model.set_weights(self.model.get_weights())

    def save_model(self, filename):
        """Guarda el modelo principal en un archivo."""
        self.model.save(filename)

    def load_model(self, filename):
        """Carga el modelo desde un archivo y sincroniza el modelo objetivo."""
        self.model = keras.models.load_model(filename)
        self.update_target_model()

    # ----------------------- Métodos relacionados con acciones -----------------------

    # ... [Métodos como obtener_estado_completo, mask_for_phase, etc.]
    def obtener_estado_completo(self):
        if len(self.historial_estados) == 0:
            # Retorna una matriz de ceros si el historial está vacío
            return np.array([np.zeros((6, 61))] * 10)
        elif len(self.historial_estados) < 10:
            estado_completo = [self.historial_estados[0]] * (10 - len(self.historial_estados)) + list(self.historial_estados)
        else:
            estado_completo = list(self.historial_estados)
        return np.array(estado_completo)
    
    def obtener_estado_actual(self):
        if len(self.historial_estados) == 0:
            return np.zeros((6, 61))
        else:
            return self.historial_estados[-1]
    
    def mask_for_phase(self, fase):
        # Retorna múltiples arrays booleanos para cada salida del modelo
        mask = {}
        if fase == 'reforzar':
            mask['reforzar_territorio'] = [True] * 42
            mask['num_tropas_reforzar'] = [True]
            mask['territorio_origen_atacar'] = [False] * 42
            mask['territorio_destino_atacar'] = [False] * 42
            mask['territorio_origen_mover'] = [False] * 42
            mask['territorio_destino_mover'] = [False] * 42
            mask['num_tropas_mover'] = [False]
        elif fase == 'atacar':
            mask['reforzar_territorio'] = [False] * 42
            mask['num_tropas_reforzar'] = [False]
            mask['territorio_origen_atacar'] = [True] * 42
            mask['territorio_destino_atacar'] = [True] * 42
            mask['territorio_origen_mover'] = [False] * 42
            mask['territorio_destino_mover'] = [False] * 42
            mask['num_tropas_mover'] = [False]
        elif fase == 'mover_tropas':
            mask['reforzar_territorio'] = [False] * 42
            mask['num_tropas_reforzar'] = [False]
            mask['territorio_origen_atacar'] = [False] * 42
            mask['territorio_destino_atacar'] = [False] * 42
            mask['territorio_origen_mover'] = [True] * 42
            mask['territorio_destino_mover'] = [True] * 42
            mask['num_tropas_mover'] = [True]
        else:
            # Todos los valores serán False si la fase no es reconocida
            mask['reforzar_territorio'] = [False] * 42
            mask['num_tropas_reforzar'] = [False]
            mask['territorio_origen_atacar'] = [False] * 42
            mask['territorio_destino_atacar'] = [False] * 42
            mask['territorio_origen_mover'] = [False] * 42
            mask['territorio_destino_mover'] = [False] * 42
            mask['num_tropas_mover'] = [False]

        return mask

    def action_to_vector(self, action):
        # Inicializa múltiples vectores de acción con ceros
        reforzar_territorio_vector = [0] * 42
        num_tropas_reforzar_vector = [0]
        territorio_origen_atacar_vector = [0] * 42
        territorio_destino_atacar_vector = [0] * 42
        territorio_origen_mover_vector = [0] * 42
        territorio_destino_mover_vector = [0] * 42
        num_tropas_mover_vector = [0]

        # Traduce la acción en los vectores de acción correspondientes
        if action['type'] == 'atacar':
            territorio_origen_atacar_vector[action['territorio_origen']] = 1
            territorio_destino_atacar_vector[action['territorio_destino']] = 1

        elif action['type'] == 'fortificar':
            reforzar_territorio_vector[action['territorio']] = 1
            num_tropas_reforzar_vector[0] = action['tropas']

        elif action['type'] == 'deslocar':
            territorio_origen_mover_vector[action['territorio_origen']] = 1
            territorio_destino_mover_vector[action['territorio_destino']] = 1
            num_tropas_mover_vector[0] = action['tropas']

        # Aquí no hay ninguna acción específica para 'pass', ya que simplemente no se selecciona ninguna acción.

        action_vectors = {
            'reforzar_territorio': reforzar_territorio_vector,
            'num_tropas_reforzar': num_tropas_reforzar_vector,
            'territorio_origen_atacar': territorio_origen_atacar_vector,
            'territorio_destino_atacar': territorio_destino_atacar_vector,
            'territorio_origen_mover': territorio_origen_mover_vector,
            'territorio_destino_mover': territorio_destino_mover_vector,
            'num_tropas_mover': num_tropas_mover_vector
        }

        return action_vectors

    def vector_to_action(self, action_vectors, fase):
        action = {}

        if fase == 'reforzar':
            # Solo verifica el vector de reforzar
            if 1 in action_vectors['reforzar_territorio']:
                action['type'] = 'fortificar'
                indice = np.argmax(action_vectors['reforzar_territorio'])
                action['territorio'] = self.nombres_paises[indice]
                action['tropas'] = math.floor(action_vectors['num_tropas_reforzar'][0])
                return action

        elif fase == 'atacar':
            # Solo verifica el vector de ataque
            if 1 in action_vectors['territorio_origen_atacar']:
                action['type'] = 'atacar'
                indice_origen = np.argmax(action_vectors['territorio_origen_atacar'])
                indice_destino = np.argmax(action_vectors['territorio_destino_atacar'])
                action['territorio_origen'] = self.nombres_paises[indice_origen]
                action['territorio_destino'] = self.nombres_paises[indice_destino]
                return action

        elif fase == 'mover_tropas':
            # Solo verifica el vector de mover tropas
            if 1 in action_vectors['territorio_origen_mover']:
                action['type'] = 'deslocar'
                indice_origen = np.argmax(action_vectors['territorio_origen_mover'])
                indice_destino = np.argmax(action_vectors['territorio_destino_mover'])
                action['territorio_origen'] = self.nombres_paises[indice_origen]
                action['territorio_destino'] = self.nombres_paises[indice_destino]
                action['tropas'] = math.floor(action_vectors['num_tropas_mover'][0])
                return action

        # Si no se detecta ninguna acción válida, se elige la acción 'pass' como predeterminada
        action['type'] = 'pass'
        return action

    

# ----------------------- Métodos relacionados con el aprendizaje -----------------------
    def elegir_accion(self, estado, fase, tablero):
        if np.random.rand() < self.epsilon:
            print("___________________aleatorio____________________________",fase)
            if fase == 'reforzar':
                return self.accion_aleatoria_reforzar(tablero)
            elif fase == 'atacar':
                return self.accion_aleatoria_atacar(tablero)
            elif fase == 'mover_tropas':
                return self.accion_aleatoria_mover_tropas(tablero)
            else:
                return {
                    'reforzar_territorio': [0] * 42,
                    'num_tropas_reforzar': [0],
                    'territorio_origen_atacar': [0] * 42,
                    'territorio_destino_atacar': [0] * 42,
                    'territorio_origen_mover': [0] * 42,
                    'territorio_destino_mover': [0] * 42,
                    'num_tropas_mover': [0]
                }
        else:
            estado_original = np.expand_dims(self.obtener_estado_completo(), axis=0)
            estado_original = np.transpose(estado_original, (0, 2, 3, 1))  # Reordenar las dimensiones
            #print(estado_original.shape)  # Esto te dirá si ya tiene la dimensión extra o no
            matriz_adyacencia = np.expand_dims(tablero.matriz_de_adyacencia(), axis=0)
            #print(matriz_adyacencia.shape)
            predicted_actions = self.model.predict([estado_original, matriz_adyacencia])
            masks = self.mask_for_phase(fase)
            
            # Selecciona la acción con el valor Q más alto para cada salida, considerando las máscaras
            action_vectors = {}
            for idx, key in enumerate(masks):
                valid_values = np.where(masks[key], predicted_actions[idx][0], float('-inf'))
                action_vectors[key] = np.zeros_like(valid_values)
                action_vectors[key][np.argmax(valid_values)] = 1
            #print("###############__________ACCIONES DE LA RED NEURONAL___________###### : ",action_vectors)
            return action_vectors

    def aprender(self, transicion, tablero):
        estado_actual, action_vectors, recompensa, estado_siguiente = transicion

        # Añadir el estado actual y siguiente a los historiales
        self.historial_estados.append(estado_actual)

        estado_original = np.expand_dims(self.obtener_estado_completo(), axis=0)
        estado_original = np.transpose(estado_original, (0, 2, 3, 1))  # Reordenar las dimensiones

        matriz_adyacencia = np.expand_dims(tablero.matriz_de_adyacencia(), axis=0)
        output_names = ['reforzar_territorio', 'num_tropas_reforzar', 'territorio_origen_atacar', 
                'territorio_destino_atacar', 'territorio_origen_mover', 'territorio_destino_mover', 
                'num_tropas_mover']

        current_q_values = dict(zip(output_names, self.model.predict([estado_original, matriz_adyacencia])))

        # Si el juego ha terminado (estado_siguiente es None), usamos solo la recompensa
        if estado_siguiente is not None:
            print(estado_siguiente.shape)
            estado_siguiente_expandido = np.expand_dims(estado_siguiente, axis=0)
            print(estado_siguiente_expandido.shape)
            estado_siguiente_expandido = np.transpose(estado_siguiente_expandido, (0, 2, 3, 1))
            next_q_values = dict(zip(output_names, self.target_model.predict([estado_siguiente_expandido, matriz_adyacencia])))

            # Actualizar los valores Q para las acciones tomadas
            for key in action_vectors:
                if action_vectors[key][0] == 1:  # Si es una acción categórica
                    current_q_values[key][0][np.argmax(action_vectors[key])] = recompensa + self.gamma * np.max(next_q_values[key][0])
                else:  # Si es una acción numérica (como número de tropas)
                    current_q_values[key][0] = recompensa + self.gamma * next_q_values[key][0]
        else:
            # Si el juego ha terminado, el valor Q es simplemente la recompensa
            for key in action_vectors:
                if action_vectors[key][0] == 1:  # Si es una acción categórica
                    current_q_values[key][0][np.argmax(action_vectors[key])] = recompensa
                else:  # Si es una acción numérica (como número de tropas)
                    current_q_values[key][0] = recompensa

        # Entrenar el modelo principal usando el estado completo y los valores Q actualizados
        self.model.fit([estado_original, matriz_adyacencia], current_q_values, epochs=1, verbose=0)

        # Decrecer epsilon para reducir la exploración a lo largo del tiempo
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


    def informar_victoria(self, tablero):
            """Notificar al agente que ha ganado."""
            self.debug_print("¡Victoria notificada!")
            
            # Aprender con una gran recompensa positiva
            estado_actual = self.obtener_estado_actual()
            accion_vector_vacio = self.crear_vector_accion_vacio()
            recompensa = 50
            # No hay acción siguiente porque el juego ha terminado
            self.aprender((estado_actual, accion_vector_vacio, recompensa, None), tablero)
            self.recompensa_acumulada += recompensa
            self.save_model("DQN_V1.h5")
            self.debug_print("Modelo guardado después de una victoria.")

    def informar_perdida(self, tablero,recompensa = -100):
        """Notificar al agente que ha perdido."""
        self.debug_print("Derrota notificada.")
        
        # Aprender con una gran recompensa negativa
        estado_actual = self.obtener_estado_actual()
        accion_vector_vacio = self.crear_vector_accion_vacio()
        recompensa = -75
        # No hay acción siguiente porque el juego ha terminado
        self.aprender((estado_actual, accion_vector_vacio, recompensa, None), tablero)
        self.recompensa_acumulada += recompensa
        self.save_model("DQN_V1.h5")
        self.debug_print("Modelo guardado después de una derrota.")
#------------------------- Recompesnas que guian a cumplir las misiones -------------------------------
    def recompensa_por_conquista_continente(self, tablero, continente):
        paises_en_continente = [pais for pais in tablero.paises.values() if pais.continente == continente]
        paises_conquistados = [pais for pais in paises_en_continente if pais.jugador == self]
        return 10*len(paises_conquistados) / len(paises_en_continente)

    def recompensa_por_conquista_territorios(self, tablero, objetivo):
        territorios_conquistados = len([pais for pais in tablero.paises.values() if pais.jugador == self])
        return 10*territorios_conquistados / objetivo

    def recompensa_por_destruir_color(self, tablero, color):
        territorios_iniciales = len(tablero.paises)
        territorios_actuales = len([pais for pais in tablero.paises.values() if pais.jugador.color == color])
        return 10*(territorios_iniciales - territorios_actuales) / territorios_iniciales
    
    def recompensa_por_mision_europa_oceania_tercero(self, tablero):
        recompensa_europa = self.recompensa_por_conquista_continente(tablero, 'Europa')
        recompensa_oceania = self.recompensa_por_conquista_continente(tablero, 'Oceanía')

        # Lista de todos los continentes excepto Europa y Oceanía
        otros_continentes = ['Asia', 'América del Sur', 'África', 'América del Norte']
        recompensas_otros = [self.recompensa_por_conquista_continente(tablero, continente) for continente in otros_continentes]
        
        # Tomamos la recompensa máxima de los demás continentes
        max_recompensa_otro_continente = max(recompensas_otros)

        return (recompensa_europa + recompensa_oceania + max_recompensa_otro_continente)/3

    def calcular_recompensa_mision(self, tablero):
        descripcion = self.mision.descripcion
        
        # Misiones cuando es "Conquistar na totalidade a Europa, a Oceanía e mais um terceiro"
        if "Conquistar na totalidade a Europa, a Oceanía e mais um terceiro" in descripcion:
            return self.recompensa_por_mision_europa_oceania_tercero(tablero)

        # Misiones de conquista de continentes
        elif any(cont in descripcion for cont in ['Europa', 'Oceanía', 'Asia', 'América del Sur', 'África', 'América del Norte']):
            continentes_mencionados = [cont for cont in ['Europa', 'Oceanía', 'Asia', 'América del Sur', 'África', 'América del Norte'] if cont in descripcion]
            return sum([self.recompensa_por_conquista_continente(tablero, cont) for cont in continentes_mencionados])

        # Misiones de conquista de número específico de territorios
        elif "TERRITÓRIOS" in descripcion:
            objetivo = 18 if "18 TERRITÓRIOS" in descripcion else 24
            return self.recompensa_por_conquista_territorios(tablero, objetivo)
        
        # Misiones de destruir ejércitos de un color específico
        elif "Destruir totalmente OS EXÉRCITOS" in descripcion:
            color = descripcion.split()[-1]
            return self.recompensa_por_destruir_color(tablero, color)

        return 0  # En caso de que no se cumpla ninguna de las condiciones anteriores


 # ----------------------- Otros métodos específicos del juego -----------------------
    def debug_action(self, accion_vector, accion_type):
        """Función auxiliar para imprimir mensajes de depuración."""
        #self.debug_print(f"Vector de acción {accion_type}: {accion_vector}")
        accion = self.vector_to_action(accion_vector,fase=accion_type)
        self.debug_print(f"Acción resultante: {accion}")
        return accion

    def obtener_estado_siguiente(self, fase, tablero):
        """Obtiene el estado siguiente después de una acción."""
        tablero.actualizar_grafo()
        tablero.crear_matriz_estado(tablero.vector_fase(fase), self)
        nuevo_estado = tablero.matriz_historial[-1]
        self.historial_estados.append(nuevo_estado)
        return self.obtener_estado_completo()

    def es_accion_valida(self, accion, tablero):
        """Verifica si una acción es válida."""
        if accion['type'] == 'fortificar':
            # Si el territorio no existe o no pertenece al jugador, la acción es inválida.
            print(tablero.paises[accion['territorio']].jugador)
            if accion['territorio'] not in tablero.paises or tablero.paises[accion['territorio']].jugador != self:
                return False
        return True

    def aplicar_accion_reforzar(self, accion_vector, tablero):
        accion = self.debug_action(accion_vector, "reforzar")
        recompensa = 0
        if not self.es_accion_valida(accion, tablero):
            # Si la acción no es válida, penaliza al agente y devuelve el estado actual.
            print("No validia")
            return -50, self.obtener_estado_siguiente("reforzar", tablero)
        
        
        if accion['type'] == 'fortificar':
            pais = tablero.paises[accion['territorio']]
            pais.tropas += accion['tropas']

            # Recompensa basada en la ubicación del refuerzo
            recompensa += 10 * accion['tropas'] if self.es_territorio_vulnerable(pais, tablero) else -2 * accion['tropas']
        
        recompensa += self.calcular_recompensa_mision(tablero)
        estado_siguiente = self.obtener_estado_siguiente("reforzar", tablero)
        return recompensa, estado_siguiente

    def reforzar(self, tablero):
        self.nombres_paises = list(tablero.paises.keys())
        estado_actual = self.obtener_estado_actual()
        accion_vector = self.elegir_accion(estado_actual, fase='reforzar', tablero=tablero)
        accion = self.vector_to_action(accion_vector, fase='reforzar')

        recompensa, estado_siguiente = self.aplicar_accion_reforzar(accion_vector, tablero)

        if accion['type'] == 'fortificar' and not accion['territorio']:
            recompensa -= 10
        self.recompensa_acumulada += recompensa
        self.aprender((estado_actual, accion_vector, recompensa, estado_siguiente), tablero)
        

    def es_accion_ataque_valida(self, accion, tablero):
        """Verifica si una acción de ataque es válida."""
        if accion['type'] != 'pass':
            if (accion['territorio_origen'] not in tablero.paises or
                accion['territorio_destino'] not in tablero.paises or
                tablero.paises[accion['territorio_origen']].jugador != self or
                tablero.paises[accion['territorio_destino']].jugador == self or
                accion['territorio_destino'] not in tablero.paises[accion['territorio_origen']].vecinos):
                return False
        return True

    def aplicar_accion_atacar(self, accion_vector, tablero):
        accion = self.debug_action(accion_vector, "atacar")
        recompensa = 0

        if not self.es_accion_ataque_valida(accion, tablero):
            # Si la acción de ataque no es válida, penaliza al agente y devuelve el estado actual.
            print("No valido el ataque")
            return -50, self.obtener_estado_siguiente("atacar", tablero)

        if accion['type'] != 'pass':
            pais_origen, pais_destino = tablero.paises[accion['territorio_origen']], tablero.paises[accion['territorio_destino']]
            jugador_destino_anterior = pais_destino.jugador
            print("__________________________________EMPEZO LA BATALLA DEL JUGADOR DQN______________________________________________")
            tablero.batalla(pais_origen, pais_destino)

            # Recompensas y penalizaciones basadas en el resultado de la batalla
            if pais_destino.jugador == self:
                recompensa += 20 if jugador_destino_anterior != self else -2 * pais_origen.tropas
                if self.conquisto_continente(pais_destino, tablero):
                    recompensa += 30
            else:
                recompensa -= pais_destino.tropas
        recompensa += self.calcular_recompensa_mision(tablero)
        estado_siguiente = self.obtener_estado_siguiente("atacar", tablero)
        return recompensa, estado_siguiente

    def atacar(self, tablero):
        estado_actual = self.obtener_estado_actual()
        accion_vector = self.elegir_accion(estado_actual, fase='atacar', tablero=tablero)
        accion = self.vector_to_action(accion_vector,fase='atacar')

        recompensa, estado_siguiente = self.aplicar_accion_atacar(accion_vector, tablero)

        if accion['type'] == 'pass' and any(self.puede_atacar(p, tablero) for p in tablero.paises.values() if p.jugador == self):
            recompensa -= 15
        
        self.aprender((estado_actual, accion_vector, recompensa, estado_siguiente), tablero)
        self.recompensa_acumulada += recompensa
    
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

    def es_territorio_vulnerable(self, pais, tablero):
        # Consideramos un territorio como vulnerable si tiene vecinos controlados por otros jugadores
        return any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)

    def es_accion_mover_tropas_valida(self, accion, tablero):
        """Verifica si una acción de mover tropas es válida."""
        if accion['type'] != 'pass':
            if (accion['territorio_origen'] not in tablero.paises or
                accion['territorio_destino'] not in tablero.paises or
                tablero.paises[accion['territorio_origen']].jugador != self or
                tablero.paises[accion['territorio_destino']].jugador != self or
                accion['territorio_destino'] not in tablero.paises[accion['territorio_origen']].vecinos):
                return False
        return True

    def aplicar_accion_mover_tropas(self, accion_vector, tablero):
        accion = self.debug_action(accion_vector, "mover_tropas")
        recompensa = 0

        if not self.es_accion_mover_tropas_valida(accion, tablero):
            # Si la acción de mover tropas no es válida, penaliza al agente y devuelve el estado actual.
            return -50, self.obtener_estado_siguiente("mover_tropas", tablero)

        if accion['type'] != 'pass':
            tropas_en_origen = tablero.paises[accion['territorio_origen']].tropas
            tropas_a_mover = min(accion['tropas'], tropas_en_origen - 1)
            tablero.mover_tropas(accion['territorio_origen'], accion['territorio_destino'], tropas_a_mover)

            pais_destino, pais_origen = tablero.paises[accion['territorio_destino']], tablero.paises[accion['territorio_origen']]
            recompensa += 20 if self.es_territorio_vulnerable(pais_destino, tablero) else -10
        recompensa += self.calcular_recompensa_mision(tablero)
        estado_siguiente = self.obtener_estado_siguiente("mover_tropas", tablero)
        return recompensa, estado_siguiente

    def mover_tropas(self, tablero):
        estado_actual = self.obtener_estado_actual()
        accion_vector = self.elegir_accion(estado_actual, fase='mover_tropas', tablero=tablero)
        accion = self.vector_to_action(accion_vector,fase='mover_tropas')

        recompensa, estado_siguiente = self.aplicar_accion_mover_tropas(accion_vector, tablero)

        if accion['type'] == 'pass':
            recompensa -= 10

        self.aprender((estado_actual, accion_vector, recompensa, estado_siguiente), tablero)
        self.recompensa_acumulada += recompensa

#_____________________FUNCIONES PARA SELECCION DE ACCIONES ALEATORIOAS PARA MOVER JUGAR__________________
    def puede_atacar(self, pais, tablero):
        """Un país puede atacar si tiene más de 2 tropas y tiene al menos un vecino controlado por otro jugador."""
        return pais.tropas > 2 and any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)

    def obtener_territorios_controlados(self, tablero):
        """Obtener los territorios controlados por el jugador."""
        return [nombre_pais for nombre_pais, p in tablero.paises.items() if p.jugador == self]
    
    def crear_vector_accion_vacio(self):
        return {
            'reforzar_territorio': [0] * 42,
            'num_tropas_reforzar': [0],
            'territorio_origen_atacar': [0] * 42,
            'territorio_destino_atacar': [0] * 42,
            'territorio_origen_mover': [0] * 42,
            'territorio_destino_mover': [0] * 42,
            'num_tropas_mover': [0]
        }

    def actualizar_vector_accion(self, action_vectors, tipo, territorio, tropas=None):
        # Convert the country's name into an index based on its position in the "self.nombres_paises" list.
        indice_territorio = self.nombres_paises.index(territorio)

        # For reinforcement action
        if tipo == 'reforzar_territorio':
            action_vectors['reforzar_territorio'][indice_territorio] = 1
            if tropas is not None:
                action_vectors['num_tropas_reforzar'][0] = tropas

        # For attack action
        elif tipo == 'territorio_origen_atacar':
            action_vectors['territorio_origen_atacar'][indice_territorio] = 1
        elif tipo == 'territorio_destino_atacar':
            action_vectors['territorio_destino_atacar'][indice_territorio] = 1

        # For move troops action
        elif tipo == 'territorio_origen_mover':
            action_vectors['territorio_origen_mover'][indice_territorio] = 1
        elif tipo == 'territorio_destino_mover':
            action_vectors['territorio_destino_mover'][indice_territorio] = 1
            if tropas is not None:
                action_vectors['num_tropas_mover'][0] = tropas

        return action_vectors

    def accion_aleatoria_reforzar(self, tablero):
        action_vectors = self.crear_vector_accion_vacio()
        territorios_controlados = self.obtener_territorios_controlados(tablero)
        if territorios_controlados:
            territorio_seleccionado = random.choice(territorios_controlados)
            print(territorio_seleccionado)
            action_vectors = self.actualizar_vector_accion(action_vectors, 'reforzar_territorio', territorio_seleccionado, self.tropas_por_turno)
            print("aleatorios:",action_vectors)

        return action_vectors

    def accion_aleatoria_atacar(self, tablero):
        action_vectors = self.crear_vector_accion_vacio()
        territorios_atacables = [nombre_pais for nombre_pais in self.obtener_territorios_controlados(tablero) if self.puede_atacar(tablero.paises[nombre_pais], tablero)]
        
        if territorios_atacables:
            territorio_origen = random.choice(territorios_atacables)
            territorio_destino = random.choice([v for v in tablero.paises[territorio_origen].vecinos if tablero.paises[v].jugador != self])
            action_vectors = self.actualizar_vector_accion(action_vectors, 'territorio_origen_atacar', territorio_origen)
            action_vectors = self.actualizar_vector_accion(action_vectors, 'territorio_destino_atacar', territorio_destino)

        return action_vectors

    def accion_aleatoria_mover_tropas(self, tablero):
        action_vectors = self.crear_vector_accion_vacio()
        nombres_paises_origen = [nombre_pais for nombre_pais in self.obtener_territorios_controlados(tablero) if tablero.paises[nombre_pais].tropas > 1]

        if nombres_paises_origen:
            pais_origen = random.choice(nombres_paises_origen)
            vecinos_posibles = [v for v in tablero.paises[pais_origen].vecinos if tablero.paises[v].jugador == self]
            
            if vecinos_posibles:
                pais_destino = random.choice(vecinos_posibles)
                tropas = random.randint(1, tablero.paises[pais_origen].tropas - 1)
                action_vectors = self.actualizar_vector_accion(action_vectors, 'territorio_origen_mover', pais_origen)
                action_vectors = self.actualizar_vector_accion(action_vectors, 'territorio_destino_mover', pais_destino, tropas)

        return action_vectors
