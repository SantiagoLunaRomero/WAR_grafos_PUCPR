import numpy as np
import random
from collections import deque
from tensorflow import keras
from tensorflow.keras.layers import Input, Conv2D, Dense, Flatten, Concatenate
from tensorflow.keras.models import Model
from Jugadores.jugador import Jugador
import math
import json
import os
from keras.callbacks import TensorBoard
from keras.layers import Dropout,MaxPooling2D
from keras.regularizers import l2
from keras.layers import  BatchNormalization
from keras.optimizers import Adam
tensorboard = TensorBoard(log_dir='./logs', histogram_freq=0, write_graph=True, write_images=True)
class ReplayMemory:
    def __init__(self, max_size=2000, filename=None):
        self.buffer = deque(maxlen=max_size)
        self.filename = filename
                
        if filename and os.path.exists(filename):
            with open(filename, 'r') as f:
                lines = f.readlines()
                for line in lines[-max_size:]:
                    item = json.loads(line.strip())
                    self.buffer.append((
                        np.array(item['state_history']),  # Cambiado de 'state' a 'state_history'
                        {k: np.array(v) for k, v in item['action'].items()},
                        item['reward'],
                        np.array(item['next_state_history']) if item['next_state_history'] else None  # Cambiado de 'next_state' a 'next_state_history'
                    ))

    def save_to_json(self, transition):
        if self.filename:
            with open(self.filename, 'a') as file:
                file.write(json.dumps(transition) + '\n')
            with open("Transitions_acumulada", 'a') as file:
                file.write(json.dumps(transition) + '\n')


    def truncate_file(self):
        """Verifica y trunca el archivo si supera 2 veces el maxlen."""
        with open(self.filename, 'r') as file:
            lines = file.readlines()
            
        # Si el número de transiciones excede 2*max_size, truncar el archivo
        if len(lines) > 1.1 * self.buffer.maxlen:
            # Conservar solo las últimas transiciones igual a 2*max_size
            with open(self.filename, 'w') as file:
                file.writelines(lines[-(1.1*self.buffer.maxlen):])

    def store(self, state_history, action, reward, next_state_history):
        self.buffer.append((state_history, action, reward, next_state_history))
        
        # Convertir a lista solo si es un objeto numpy
        transition = {
            'state_history': state_history.tolist() if isinstance(state_history, np.ndarray) else state_history,
            'action': {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in action.items()}, 
            'reward': reward,
            'next_state_history': next_state_history.tolist() if (next_state_history is not None and isinstance(next_state_history, np.ndarray)) else next_state_history
        }
        self.save_to_json(transition)


    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)


class FusionAgenteDQN(Jugador):

    def __init__(self, nombre, color, mision, alpha=0.1, gamma=0.6, epsilon=0.7, epsilon_decay=0.995, epsilon_min=0.01):
        super().__init__(nombre, color, mision)
        
        # Parámetros del algoritmo
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.recompensa_acumulada = 0
        
        #REFORZAR ATACAR MOVER TROPAS : 
        self.tropas_disponibles = self.tropas_por_turno 
        # Historial y mapeo de acciones
        self.historial_maxlen = 25
        self.historial_estados = deque(maxlen=self.historial_maxlen)
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

        # Variables para las mejoras
        self.learning_counter = 0
        self.train_frequency = 75  # Entrenar el modelo cada 5 acciones
        self.target_update_frequency = 75*3  # Actualizar el modelo objetivo cada 10 acciones
        self.target_update_counter = 0
        self.memory = ReplayMemory(max_size=3000, filename="transitions.json") # Almacenar transiciones en JSON
        self.batch_size = 256

    def debug_print(self, message):
        if self.debug:
            print(message) 

    # ----------------------- Métodos relacionados con el modelo -----------------------


    def create_multi_output_model(self):
        """Crea y retorna el modelo DQN con múltiples salidas."""
        input_caracteristicas = Input(shape=(6, 61,self.historial_maxlen ), name="input_caracteristicas")
        input_adyacencia = Input(shape=(42, 42), name="input_adyacencia")

        # Capas convolucionales para características
        x_features = Conv2D(32, (7, 7), activation='relu', padding='same', kernel_regularizer=l2(0.01))(input_caracteristicas)
        x_features = Dropout(0.15)(x_features)

        x_features = Conv2D(64, (5, 5), activation='relu', padding='same', kernel_regularizer=l2(0.01))(x_features)
        x_features = MaxPooling2D((2, 2))(x_features)
        x_features = Dropout(0.15)(x_features)

        x_features = Conv2D(128, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(0.01))(x_features)
        x_features = MaxPooling2D((2, 2))(x_features)
        x_features = Dropout(0.15)(x_features)

        x_features = Flatten()(x_features)

        # Añade una dimensión extra a la matriz de adyacencia
        x_adjacency = keras.layers.Reshape((42, 42, 1))(input_adyacencia)

        # Capas convolucionales para matriz de adyacencia
        x_adjacency = Conv2D(32, (3, 3), activation='relu',padding='same', kernel_regularizer=l2(0.01))(x_adjacency)  # Regularización L2
        x_adjacency = Dropout(0.15)(x_adjacency)  # Dropout del 25%

        x_adjacency = Conv2D(64, (3, 3), activation='relu',padding='same', kernel_regularizer=l2(0.01))(x_adjacency)  # Regularización L2
        x_adjacency = Dropout(0.15)(x_adjacency)  # Dropout del 25%
        x_adjacency = Flatten()(x_adjacency)

        combined = Concatenate()([x_features, x_adjacency])
        x = Dense(256, activation='relu')(combined)

        # Bloque de capas densas antes de cada salida
        def dense_block(input_tensor, units):
            x = Dense(units[0], activation='relu', kernel_regularizer=l2(0.01))(input_tensor)  # Regularización L2
            x = Dropout(0.25)(x)  # Dropout del 50%
            x = Dense(units[1], activation='relu', kernel_regularizer=l2(0.01))(x)  # Regularización L2
            if len(units) == 3:
                x = Dropout(0.25)(x)  # Dropout del 50%
                x = Dense(units[2], activation='relu', kernel_regularizer=l2(0.01))(x)  # Regularización L2
            return x

        # Salidas con bloques densos
        reforzar_territorio = Dense(42, activation='softmax', name='reforzar_territorio')(dense_block(x, [128,128]))
        num_tropas_reforzar = Dense(1, activation='relu', name='num_tropas_reforzar')(dense_block(x, [128,64,32]))
        territorio_origen_atacar = Dense(42, activation='softmax', name='territorio_origen_atacar')(dense_block(x, [128,128]))
        territorio_destino_atacar = Dense(42, activation='softmax', name='territorio_destino_atacar')(dense_block(x, [128,128]))
        territorio_origen_mover = Dense(42, activation='softmax', name='territorio_origen_mover')(dense_block(x, [128,128]))
        territorio_destino_mover = Dense(42, activation='softmax', name='territorio_destino_mover')(dense_block(x, [128,128]))
        num_tropas_mover = Dense(1, activation='relu', name='num_tropas_mover')(dense_block(x, [128,64,32]))

        model = Model(inputs=[input_caracteristicas, input_adyacencia], 
                    outputs=[reforzar_territorio, num_tropas_reforzar, territorio_origen_atacar, territorio_destino_atacar, territorio_origen_mover, territorio_destino_mover, num_tropas_mover])
        
        optimizer = Adam(lr=(1e-6))
        model.compile(optimizer=optimizer, 
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
        print("Modelo cargado___as")
        self.update_target_model()

    # ----------------------- Métodos relacionados con acciones -----------------------

    # ... [Métodos como obtener_estado_completo, mask_for_phase, etc.]
    def obtener_estado_completo(self):
        if len(self.historial_estados) == 0:
            return np.array([np.zeros((6, 61))] * self.historial_maxlen)
        elif len(self.historial_estados) < self.historial_maxlen:
            estado_completo = [self.historial_estados[0]] * (self.historial_maxlen - len(self.historial_estados)) + list(self.historial_estados)
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
    def escalar_recompensa(self,recompensa):
        recompensa = recompensa/100
        return recompensa

    def aprender(self, transicion, tablero):
        estado_actual, action_vectors, recompensa, estado_siguiente = transicion

        # Actualiza el historial de estados
        self.historial_estados.append(estado_actual)

        # Obtiene el historial completo de estados
        state_history_current = self.obtener_estado_completo()

        # Almacena la transición (con historial) en la memoria replay
        self.memory.store(state_history_current, action_vectors, recompensa, estado_siguiente)

        # Reducir la frecuencia de entrenamiento
        self.learning_counter += 1
        if self.learning_counter % self.train_frequency != 0:
            return

        # Entrenar el modelo principal usando un lote aleatorio
        if len(self.memory) >= self.batch_size:
            batch = self.memory.sample(self.batch_size)
            
            estado_batch = []
            matriz_batch = []
            q_values_batch = {
                'reforzar_territorio': [],
                'num_tropas_reforzar': [],
                'territorio_origen_atacar': [],
                'territorio_destino_atacar': [],
                'territorio_origen_mover': [],
                'territorio_destino_mover': [],
                'num_tropas_mover': []
            }

            for estado, accion, recomp, estado_next in batch:
                recomp = self.escalar_recompensa(recomp)
                estado_original = np.transpose(estado, (1, 2, 0))
                estado_batch.append(estado_original)

                matriz_adyacencia = tablero.matriz_de_adyacencia()
                matriz_batch.append(matriz_adyacencia)

                output_names = [
                    'reforzar_territorio', 'num_tropas_reforzar', 'territorio_origen_atacar', 
                    'territorio_destino_atacar', 'territorio_origen_mover', 
                    'territorio_destino_mover', 'num_tropas_mover'
                ]

                current_q_values = dict(zip(output_names, self.model.predict([estado_original[np.newaxis, ...], matriz_adyacencia[np.newaxis, ...]])))
                #print("Current Q-values:", current_q_values)
                if estado_next is not None:
                    estado_next_expandido = np.transpose(estado_next, (1, 2, 0))
                    next_q_values = dict(zip(output_names, self.target_model.predict([estado_next_expandido[np.newaxis, ...], matriz_adyacencia[np.newaxis, ...]])))
                    #print("Next Q-values (from target model)::", current_q_values)
                    for key in accion:
                        if accion[key][0] == 1:
                            current_q_values[key][0][np.argmax(accion[key])] = recomp + self.gamma * np.max(next_q_values[key][0])
                        else:
                            current_q_values[key][0] = recomp + self.gamma * next_q_values[key][0]
                else:
                    for key in accion:
                        if accion[key][0] == 1:
                            current_q_values[key][0][np.argmax(accion[key])] = recomp
                        else:
                            current_q_values[key][0] = recomp
                #print("Updated Q-values:", current_q_values)
                for key in current_q_values:
                    q_values_batch[key].append(current_q_values[key][0])

            # Convertir cada lista del diccionario en un numpy array.
            for key in q_values_batch:
                q_values_batch[key] = np.array(q_values_batch[key])
            
            estado_batch = np.array(estado_batch)
            matriz_batch = np.array(matriz_batch)

            self.model.fit([estado_batch, matriz_batch], q_values_batch, epochs=1, verbose=0,callbacks=[tensorboard])

        # Actualizar el modelo objetivo
        self.target_update_counter += 1
        if self.target_update_counter % self.target_update_frequency == 0:
            self.update_target_model()
            self.target_update_counter = 0

        # Decrecer epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay



    def a_aprender(self, transicion, tablero):
        estado_actual, action_vectors, recompensa, estado_siguiente = transicion

        # Actualiza el historial de estados
        self.historial_estados.append(estado_actual)
        
        # Obtiene el historial completo de estados
        state_history_current = self.obtener_estado_completo()
        

        # Almacena la transición (con historial) en la memoria replay

        self.memory.store(state_history_current, action_vectors, recompensa, estado_siguiente)

        # Reducir la frecuencia de entrenamiento
        self.learning_counter += 1
        if self.learning_counter % self.train_frequency != 0:
            return

        # Entrenar el modelo principal usando un lote aleatorio
        if len(self.memory) >= self.batch_size:
            batch = self.memory.sample(self.batch_size)
            for estado, accion, recomp, estado_next in batch:
                recomp = self.escalar_recompensa(recomp)
                estado_original = np.expand_dims(estado, axis=0)
                print(estado_original.shape)
                estado_original = np.transpose(estado_original, (0, 2, 3, 1))

                matriz_adyacencia = np.expand_dims(tablero.matriz_de_adyacencia(), axis=0)
                output_names = ['reforzar_territorio', 'num_tropas_reforzar', 'territorio_origen_atacar', 
                        'territorio_destino_atacar', 'territorio_origen_mover', 'territorio_destino_mover', 
                        'num_tropas_mover']

                current_q_values = dict(zip(output_names, self.model.predict([estado_original, matriz_adyacencia])))
                #print("Current Q-values:", current_q_values)

                if estado_next is not None:
                    estado_next_expandido = np.expand_dims(estado_next, axis=0)
                    estado_next_expandido = np.transpose(estado_next_expandido, (0, 2, 3, 1))
                    next_q_values = dict(zip(output_names, self.target_model.predict([estado_next_expandido, matriz_adyacencia])))
                    #print("Next Q-values (from target model)::", current_q_values)

                    for key in accion:
                        if accion[key][0] == 1:
                            current_q_values[key][0][np.argmax(accion[key])] = recomp + self.gamma * np.max(next_q_values[key][0])
                        else:
                            current_q_values[key][0] = recomp + self.gamma * next_q_values[key][0]
                else:
                    for key in accion:
                        if accion[key][0] == 1:
                            current_q_values[key][0][np.argmax(accion[key])] = recomp
                        else:
                            current_q_values[key][0] = recomp
                #print("Updated Q-values:", current_q_values)
                self.model.fit([estado_original, matriz_adyacencia], current_q_values, epochs=1, verbose=0, callbacks=[tensorboard])

        # Actualizar el modelo objetivo
        self.target_update_counter += 1
        if self.target_update_counter % self.target_update_frequency == 0:
            self.update_target_model()
            self.target_update_counter = 0

        # Decrecer epsilon
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
        #self.memory.truncate_file()
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
            if accion['territorio'] not in tablero.paises or tablero.paises[accion['territorio']].jugador != self:
                return False
            
            # Si se intenta reforzar con más tropas de las disponibles, la acción es inválida.
            if accion['tropas'] > self.tropas_disponibles:
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

            # Descontar las tropas usadas de las tropas disponibles
            self.tropas_disponibles -= accion['tropas']
            # Recompensa basada en la ubicación del refuerzo
            recompensa += 10 * accion['tropas'] if self.es_territorio_vulnerable(pais, tablero) else -2 * accion['tropas']
        
        recompensa += self.calcular_recompensa_mision(tablero)
        estado_siguiente = self.obtener_estado_siguiente("reforzar", tablero)
        return recompensa, estado_siguiente

    def reforzar(self, tablero):
        self.nombres_paises = list(tablero.paises.keys())
        tropas_disponibles = self.tropas_disponibles   # Suponiendo que tienes una variable para las tropas disponibles

        while tropas_disponibles > 0:
            estado_actual = self.obtener_estado_actual()
            accion_vector = self.elegir_accion(estado_actual, fase='reforzar', tablero=tablero)
            accion = self.vector_to_action(accion_vector, fase='reforzar')

            recompensa, estado_siguiente = self.aplicar_accion_reforzar(accion_vector, tablero)

            if accion['type'] == 'fortificar' and not accion['territorio']:
                recompensa -= 10

            self.recompensa_acumulada += recompensa
            self.aprender((estado_actual, accion_vector, recompensa, estado_siguiente), tablero)
            tropas_disponibles -= accion.get('tropas', 0)  # Reduce las tropas disponibles basado en la acción

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
        puede_atacar = True  # Inicialmente asumimos que el jugador puede atacar
        ataques_consecutivos = 0  # Contador para ataques consecutivos sin "pass"
        max_ataques_consecutivos = 5  # Establecer un límite para ataques consecutivos sin "pass"

        while puede_atacar and ataques_consecutivos < max_ataques_consecutivos:
            estado_actual = self.obtener_estado_actual()
            accion_vector = self.elegir_accion(estado_actual, fase='atacar', tablero=tablero)
            accion = self.vector_to_action(accion_vector, fase='atacar')

            territorio_origen_jugador_anterior = tablero.paises[accion['territorio_origen']].jugador if accion['type'] != 'pass' else None
            recompensa, estado_siguiente = self.aplicar_accion_atacar(accion_vector, tablero)
            territorio_origen_jugador_actual = tablero.paises[accion['territorio_origen']].jugador if accion['type'] != 'pass' else None

            if accion['type'] == 'pass':
                recompensa -= 15
                ataques_consecutivos = 0  # Restablecer el contador de ataques consecutivos
            elif territorio_origen_jugador_anterior != territorio_origen_jugador_actual:
                ataques_consecutivos += 1  # Incrementar el contador de ataques consecutivos

            self.aprender((estado_actual, accion_vector, recompensa, estado_siguiente), tablero)
            self.recompensa_acumulada += recompensa

            # Verifica si aún puede atacar
            puede_atacar = any(self.puede_atacar(p, tablero) for p in tablero.paises.values() if p.jugador == self)

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

    def aplicar_accion_mover_tropas(self, accion_vector, tablero,paises_que_recibieron):
        accion = self.debug_action(accion_vector, "mover_tropas")
        recompensa = 0

        # Si el territorio origen ya recibió tropas, la acción no es válida
        if accion['territorio_origen'] in paises_que_recibieron:
            self.debug_print("No valida : Pais ya recibio")
            return -50, self.obtener_estado_siguiente("mover_tropas", tablero)

        if not self.es_accion_mover_tropas_valida(accion, tablero):
            # Si la acción de mover tropas no es válida, penaliza al agente y devuelve el estado actual.
            self.debug_print("No valida")
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
        paises_que_recibieron = set()
        movimientos_repetidos = {}  # Llevar registro de movimientos repetidos entre países
        MAX_REPETICIONES = 3  # Límite de repeticiones para movimientos entre dos países
        MAX_INTENTOS = 10  # Límite de intentos para mover tropas
        intentos = 0
        puede_mover = True
        pasadas_consecutivas = 0

        while puede_mover and pasadas_consecutivas < 3 and intentos < MAX_INTENTOS:
            estado_actual = self.obtener_estado_actual()
            accion_vector = self.elegir_accion(estado_actual, fase='mover_tropas', tablero=tablero)
            accion = self.vector_to_action(accion_vector, fase='mover_tropas')

            # Verificar si el país origen ya donó tropas
            while accion['type'] != 'pass' and accion['territorio_origen'] in paises_que_recibieron and intentos < MAX_INTENTOS:
                accion_vector = self.elegir_accion(estado_actual, fase='mover_tropas', tablero=tablero)
                accion = self.vector_to_action(accion_vector, fase='mover_tropas')
                intentos += 1

            if accion['type'] == 'pass':
                recompensa = -10
                pasadas_consecutivas += 1
            else:
                # Verificar movimientos repetidos
                pareja_paises = (accion['territorio_origen'], accion['territorio_destino'])
                movimientos_repetidos[pareja_paises] = movimientos_repetidos.get(pareja_paises, 0) + 1
                if movimientos_repetidos[pareja_paises] > MAX_REPETICIONES:
                    recompensa = -20  # Penalización por movimientos repetidos
                else:
                    recompensa, _ = self.aplicar_accion_mover_tropas(accion_vector, tablero, paises_que_recibieron)
                    if recompensa != -50:  # Evitar agregar países en caso de una acción inválida
                        paises_que_recibieron.add(accion['territorio_destino'])
                        pasadas_consecutivas = 0

            estado_siguiente = self.obtener_estado_siguiente("mover_tropas", tablero)
            self.aprender((estado_actual, accion_vector, recompensa, estado_siguiente), tablero)
            self.recompensa_acumulada += recompensa

            puede_mover = any(p for p in tablero.paises.values() if p.jugador == self and p.tropas > 1 and p.nombre not in paises_que_recibieron)


    def a_mover_tropas(self, tablero):
        paises_que_recibieron = set()  # Almacenar los territorios que ya han recibido tropas
        puede_mover = True  # Inicialmente asumimos que el jugador puede mover tropas
        pasadas_consecutivas = 0  # Contador para las acciones "pass" consecutivas

        while puede_mover and pasadas_consecutivas < 3:  # Establecemos un límite de 3 pasadas consecutivas
            estado_actual = self.obtener_estado_actual()
            accion_vector = self.elegir_accion(estado_actual, fase='mover_tropas', tablero=tablero)
            accion = self.vector_to_action(accion_vector, fase='mover_tropas')

            if accion['type'] == 'pass':
                recompensa = -10
                pasadas_consecutivas += 1  # Incrementamos el contador de pasadas consecutivas
            else:
                recompensa, _ = self.aplicar_accion_mover_tropas(accion_vector, tablero)
                paises_que_recibieron.add(accion['territorio_destino'])
                pasadas_consecutivas = 0  # Restablecemos el contador de pasadas consecutivas

            estado_siguiente = self.obtener_estado_siguiente("mover_tropas", tablero)
            self.aprender((estado_actual, accion_vector, recompensa, estado_siguiente), tablero)
            self.recompensa_acumulada += recompensa

            # Verifica si aún puede mover tropas y si el territorio origen no ha recibido tropas
            puede_mover = any(p for p in tablero.paises.values() if p.jugador == self and p.tropas > 1 and p.nombre not in paises_que_recibieron)

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
            #print(territorio_seleccionado)
            tropas_a_reforzar = random.randint(1, min(self.tropas_disponibles, self.tropas_por_turno))
            action_vectors = self.actualizar_vector_accion(action_vectors, 'reforzar_territorio', territorio_seleccionado, tropas_a_reforzar)

            #print("aleatorios:",action_vectors)

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
