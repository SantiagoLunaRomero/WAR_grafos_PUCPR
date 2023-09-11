from Jugadores.jugadorDNQ.utils.codex import estado_a_vector
import numpy as np

class Mover_Remember_Train:

    @staticmethod
    def remember(jugador, tablero, recompensa, estado_actual, lista_nombres_paises, pais_origen, pais_destino):
        # Guardar experiencia en memoria
        pais_origen_idx = lista_nombres_paises.index(pais_origen.nombre)
        pais_destino_idx = lista_nombres_paises.index(pais_destino.nombre)
        next_estado = estado_a_vector(jugador, tablero)
        
        # Aquí asumo que la función remember_mover_tropas tiene una estructura similar a remember_ataque o remember_reforzar
        jugador.remember_mover(estado_actual, (pais_origen_idx, pais_destino_idx), recompensa, next_estado)

        # Entrenar la red neuronal cada ciertos pasos (por ejemplo, cada 10 pasos)
        #if jugador.freq_moverTropas % 10 == 0:
        #    jugador.train(accion="mover")
        
        # Disminuir epsilon
        jugador.epsilon_m = max(jugador.epsilon_min, jugador.epsilon_decay * jugador.epsilon_m)

    @staticmethod
    def train(jugador, batch_size):
        # Paso 1: Muestra un lote de experiencias de la memoria.
        batch = jugador.get_batch(batch_size, jugador.memory_mover)
        
        # Preparar arrays para los datos de entrenamiento
        states = np.array([experience[0] for experience in batch])
        q_values = jugador.mover_tropas_network.predict(states)

        for i, (state, action, reward, next_state) in enumerate(batch):
            pais_origen_idx, pais_destino_idx = action
            
            # Si el next_state es None, es el final del episodio
            if next_state is None:
                q_values[i, pais_origen_idx] = reward
                q_values[i, pais_destino_idx+42] = reward  # +42 porque la segunda parte del vector de salida representa el país destino
            else:
                # Calcula el valor Q máximo para el siguiente estado
                next_q_values = jugador.mover_tropas_network.predict(next_state.reshape(1, -1))
                max_next_q_value_origen = np.max(next_q_values[0, :42])
                max_next_q_value_destino = np.max(next_q_values[0, 42:])
                
                # Actualiza el valor Q para la acción tomada
                q_values[i, pais_origen_idx] = reward + jugador.gamma * max_next_q_value_origen
                q_values[i, pais_destino_idx+42] = reward + jugador.gamma * max_next_q_value_destino

        # Entrena la red neuronal
        jugador.mover_tropas_network.train(states, q_values)
        #jugador.freq_moverTropas=1

        # De manera periódica (por ejemplo, cada 100 pasos), actualiza el target model
        #if jugador.freq_moverTropas_target % 3 == 0:
        #    print("........Entro en la fase de Guardar......")
        #    jugador.sync_networks("mover")
        #    jugador.save("mover")
        #    jugador.freq_moverTropas_target = 1
        #else:
        #    jugador.freq_moverTropas_target = jugador.freq_moverTropas_target + 1