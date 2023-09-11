from Jugadores.jugadorDNQ.utils.codex import estado_a_vector
import numpy as np
class Reforzar_Remember_Train:

    @staticmethod
    def remember(jugador,tablero,recompensa,estado_actual,pais_reforzado_idx):
        #self.debug_print(["Pais reforzado en mis paises : ",pais_reforzado in self.paises,"Exito en refuerzo : ",exito_refuerzo])
        #self.debug_print([pais_reforzado.get_nombre(),pais_reforzado_idx, "Exito : ",exito_refuerzo[0]," Tipo : ",aux])
        # Obtener recompensa y próximo estado
        #recompensa 
        jugador.debug_print(recompensa)
        next_estado = estado_a_vector(jugador, tablero)
        # Guardar experiencia en memoria
        jugador.remember_refuerzo(estado_actual, pais_reforzado_idx, recompensa, next_estado)

        # Entrenar la red neuronal cada ciertos pasos (por ejemplo, cada 10 pasos)
        #if jugador.freq_refuerzo % 10 == 0:
        #    jugador.train(accion="reforzar")
        
        # Disminuir epsilon
        jugador.epsilon_r = max(jugador.epsilon_min, jugador.epsilon_decay * jugador.epsilon_r)

    @staticmethod
    def train(jugador,batch_size):
        # Paso 1: Muestra un lote de experiencias de la memoria.
        batch = jugador.get_batch(batch_size,jugador.memory_refuerzo)
        
        # Preparar arrays para los datos de entrenamiento
        states = np.array([experience[0] for experience in batch])
        q_values = jugador.reforzamiento_network.predict(states)

        for i, (state, action, reward, next_state) in enumerate(batch):
            if next_state is None:
                q_values[i][action] = reward
            else:
                # Usamos el target model para calcular los Q-values del próximo estado
                next_q_values = jugador.reforzamiento_target_network.predict(next_state.reshape(1, -1))
                max_next_q_value = np.max(next_q_values)

                q_values[i][action] = reward + jugador.gamma * max_next_q_value

        # Entrena la red neuronal
        jugador.reforzamiento_network.train(states, q_values)
        #jugador.freq_refuerzo=1
        # De manera periódica (por ejemplo, cada 100 pasos), actualiza el target model
        #if jugador.freq_refuerzo_target % 3 == 0:
        #    jugador.sync_networks("reforzar")
        #    jugador.save("reforzar")
        #    jugador.freq_refuerzo_target = 1
        #else :
        #    jugador.freq_refuerzo_target = jugador.freq_refuerzo_target+1

