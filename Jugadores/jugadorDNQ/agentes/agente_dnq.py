from Jugadores.jugador import Jugador
from Jugadores.jugadorDNQ.utils.recompensas import recompensa_total_reforzar,  recompensa_total_atacar,recompensa_total_mover_tropas
from Jugadores.jugadorDNQ.utils.EstrategiasExploracion import EstrategiasExploracion
from Jugadores.jugadorDNQ.utils.EstrategiasExplotacion import EstrategiasExplotacion

from Jugadores.jugadorDNQ.utils.reforzar_remember_train import Reforzar_Remember_Train
from Jugadores.jugadorDNQ.utils.atacar_remember_train import Atacar_Remember_Train
from Jugadores.jugadorDNQ.utils.mover_remember_train import Mover_Remember_Train



from Jugadores.jugadorDNQ.utils.codex import estado_a_vector
import random
from Jugadores.jugadorDNQ.modelos.reforzar_nn import ReforzarNN
from Jugadores.jugadorDNQ.modelos.atacar_nn import AtacarNN
from Jugadores.jugadorDNQ.modelos.moverTropas_nn import MoverTropasNN
from collections import deque
import numpy as np
import os
import pickle
import json
from datetime import datetime

class JugadorDQN(Jugador):
    def __init__(self, nombre, color, mision, gamma=0.99, learning_rate=0.001, epsilon=1, epsilon_decay=1, epsilon_min=0.01):
        super().__init__(nombre, color, mision)

        #Variables de control
        self.debug = True
        #frecuencia para entrenar red neuronal
        self.freq_refuerzo = 1
        self.freq_refuerzo_target = 1
        

        self.freq_ataque = 1
        self.freq_ataque_target = 1

        self.freq_moverTropas = 1
        self.freq_moverTropas_target = 1
        
        # Memoria de repetición de experiencia
        self.memory_refuerzo = []#deque(maxlen=2000)  # por ejemplo, un tamaño máximo de 2000
        self.memory_ataque = []#deque(maxlen=2000)
        self.memory_mover = []#deque(maxlen=3000) 

        # Hiperparámetros
        self.gamma = gamma
        self.learning_rate = learning_rate

        self.epsilon_r = epsilon
        self.epsilon_a = epsilon
        self.epsilon_m = epsilon

        self.gamma_refuerzo = 0.5  # refuerzo 0.988 Ataque0.995 #Mover0996
        self.gamma_ataque = 0.5    # 
        self.gamma_mover = 0.5

        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.reforzamiento_network = ReforzarNN()
        self.reforzamiento_target_network = ReforzarNN()
        # Inicializar las redes neuronales para cada fase

        if os.path.exists('reforzamiento_model.h5'):
            self.load("reforzar")
        self.sync_networks("reforzar")  # Inicialmente sincronizamos los pesos


        self.ataque_network = AtacarNN()
        self.ataque_target_network = AtacarNN()
        if os.path.exists('ataque_model.h5'):
            self.load("atacar")
        self.sync_networks("atacar")

        self.mover_tropas_network = MoverTropasNN()
        self.mover_tropas_target_network = MoverTropasNN()
        if os.path.exists('mover_model.h5'):
            self.load("mover")
        self.sync_networks("mover")

    def debug_print(self, message):
        if self.debug:
            print(message) 

    def remember_refuerzo(self, state, action, reward, next_state):
        self.memory_refuerzo.append((state, action, reward, next_state))

    def remember_ataque(self, state, action, reward, next_state):
        self.memory_ataque.append((state, action, reward, next_state))

    def remember_mover(self, state, action, reward, next_state):
        self.memory_mover.append((state, action, reward, next_state))
    
    def get_batch(self, batch_size,memory):
        if len(memory) < batch_size:
            return random.sample(memory, len(memory))
        else:
            return random.sample(memory, batch_size)

    def save(self):
        # Obtener la fecha actual para agregarla al nombre del archivo
        fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Verificar y crear las carpetas necesarias
        if not os.path.exists('partidas'):
            os.mkdir('partidas')
        
        if not os.path.exists('partidas/reforzar'):
            os.mkdir('partidas/reforzar')

        if not os.path.exists('partidas/atacar'):
            os.mkdir('partidas/atacar')

        if not os.path.exists('partidas/mover'):
            os.mkdir('partidas/mover')

        # Guardar los modelos y memorias con el nuevo formato
        path_refuerzo_memory = f'partidas/reforzar/memory_{fecha_actual}.pkl'

        path_ataque_memory = f'partidas/atacar/memory_ataque_{fecha_actual}.pkl'

        path_mover_memory = f'partidas/mover/memory_mover_{fecha_actual}.pkl'

        self.reforzamiento_network.save_model('reforzamiento_model.h5')
        with open(path_refuerzo_memory, 'wb') as f:
            pickle.dump(self.memory_refuerzo, f)

        self.ataque_network.save_model('ataque_model.h5')
        with open(path_ataque_memory, 'wb') as f:
            pickle.dump(self.memory_ataque, f)

        self.mover_tropas_network.save_model('mover_model.h5')
        with open(path_mover_memory, 'wb') as f:
            pickle.dump(self.memory_mover, f)

    def a_save(self,accion):
        if accion == "reforzar":
            self.reforzamiento_network.save_model('reforzamiento_model.h5')
            # Aquí también puedes guardar otros modelos si los tienes
            with open('memory.pkl', 'wb') as f:
                pickle.dump(self.memory_refuerzo, f)
        elif accion == "atacar":
            self.ataque_network.save_model('ataque_model.h5')
            with open('memory_ataque.pkl', 'wb') as f:
                pickle.dump(self.memory_ataque, f)
        elif accion == "mover":
            self.mover_tropas_network.save_model('mover_model.h5')
            with open('memory_mover.pkl', 'wb') as f:
                pickle.dump(self.memory_mover, f)
        else :
            raise ValueError(f"Error no existe el comando : {accion}")

    def load(self,accion):
        if accion == "reforzar":
            print("_____- cargando modelo reforzar ____")
            #self.reforzamiento_network.load_model('reforzamiento_model.h5')
            self.reforzamiento_network.load_model('refuerzo_2.h5')
            # Aquí también puedes cargar otros modelos si los tienes
            if os.path.exists('memory.pkl'):
                with open('memory.pkl', 'rb') as f:
                    self.memory_refuerzo = pickle.load(f)

        elif accion == "atacar":
            self.ataque_network.load_model('ataque_model.h5')
            if os.path.exists('memory_ataque.pkl'):
                with open('memory_ataque.pkl', 'rb') as f:
                    self.memory_ataque = pickle.load(f)

        elif accion == "mover":
            self.mover_tropas_network.load_model('mover_model.h5')
            if os.path.exists('memory_mover.pkl'):
                with open('memory_mover.pkl', 'rb') as f:
                    self.memory_mover = pickle.load(f)
        else :
            raise ValueError(f"Error no existe el comando : {accion}")

    # Método para sincronizar los pesos entre la red principal y la red objetivo
    def sync_networks(self,accion):
        if accion=="reforzar":
            self.reforzamiento_target_network.set_weights(self.reforzamiento_network.get_weights())
        elif accion=="atacar":
            self.ataque_target_network.set_weights(self.ataque_network.get_weights())
        elif accion=="mover":
            self.mover_tropas_target_network.set_weights(self.mover_tropas_network.get_weights())
        else: 
            raise ValueError(f"Error no existe el comando : {accion}")

    def reforzar(self, tablero):
        paises_reforzados = {}
        print("Tengo estas tropas : ", self.tropas_por_turno)
        fallos_consecutivos = 0  # Agregamos un contador para fallos consecutivos
        while self.tropas_por_turno > 0:
            estado_actual = estado_a_vector(self, tablero)
            lista_nombres_paises = list(tablero.paises.keys())
            # Decidir acción usando estrategia epsilon-greedy
            if random.random() < self.epsilon_r or fallos_consecutivos >= 3:
                self.debug_print("reforzando con **** RANDOM ****")
                pais_reforzado, exito_refuerzo = EstrategiasExploracion.reforzar(self, tablero)
                pais_reforzado_idx = lista_nombres_paises.index(pais_reforzado.nombre)
            else:
                pais_reforzado, pais_reforzado_idx, exito_refuerzo = EstrategiasExplotacion.reforzar(self, tablero, estado_actual, lista_nombres_paises)
            # Si no tuvo éxito incrementamos el contador de fallos
            if not exito_refuerzo[0]:
                fallos_consecutivos += 1
            else:  # Si tuvo éxito reseteamos el contador
                fallos_consecutivos = 0
            
            # Obtener recompensa y próximo estado
            recompensa = recompensa_total_reforzar(tablero, self, pais_reforzado, exito_refuerzo[0])
            self.debug_print(recompensa)
            Reforzar_Remember_Train.remember(self, tablero, recompensa, estado_actual, pais_reforzado_idx)

            if exito_refuerzo[0]:
                if pais_reforzado.get_nombre() in paises_reforzados.keys():
                    paises_reforzados[pais_reforzado.get_nombre()] = paises_reforzados[pais_reforzado.get_nombre()] + 1
                else:
                    paises_reforzados[pais_reforzado.get_nombre()] = 1

        self.freq_refuerzo = self.freq_refuerzo + 1
        self.debug_print(["Paises reforzados : ", paises_reforzados])
        return paises_reforzados

    def atacar(self, tablero):
        lista_nombres_paises = list(tablero.paises.keys())
        ataques_maximos = 15
        ataques_fallidos_consecutivos = 0
        ataques_totales = 0
        ultimo_pais_origen = None
        ultimo_pais_destino = None

        while ataques_totales < ataques_maximos and ataques_fallidos_consecutivos < 3:
            estado_actual = estado_a_vector(self, tablero)

            if random.random() < self.epsilon_a:
                self.debug_print("****** Fase de ataque con random *****")
                pais_origen, pais_destino, exito_ataque = EstrategiasExploracion.atacar(self, tablero)
                if pais_origen is None or pais_destino is None:
                    self.debug_print("No se pudo realizar un ataque. Intentando de nuevo...")
                    ataques_fallidos_consecutivos += 1
                    continue
            else:
                self.debug_print("****** Fase de ataque con NN *****")
                pais_origen, pais_destino, exito_ataque = EstrategiasExplotacion.atacar(self, tablero, estado_actual, lista_nombres_paises)

            ultimo_pais_origen = pais_origen
            ultimo_pais_destino = pais_destino

            # Obtener recompensa
            recompensa = recompensa_total_atacar(tablero, self, pais_origen, pais_destino, exito_ataque)
            self.debug_print([exito_ataque, " recompensa: ", recompensa])
            Atacar_Remember_Train.remember(self, tablero, recompensa, estado_actual, lista_nombres_paises, pais_origen, pais_destino)
            
            ataques_totales += 1

            if not exito_ataque:
                ataques_fallidos_consecutivos += 1
            else:
                ataques_fallidos_consecutivos = 0  # Reset

            # Verificar el tercer criterio
            if all(pais.tropas <= max(tablero.paises[vecino].tropas for vecino in pais.vecinos) for pais in self.paises):
                self.debug_print("Todos los países del jugador tienen menos tropas que sus vecinos. Deteniendo la fase de ataque.")
                break

        self.freq_ataque += 1
        return ultimo_pais_origen, ultimo_pais_destino


    def mover_tropas(self, tablero):
        lista_nombres_paises = list(tablero.paises.keys())
        movimientos_maximos = 15
        movimientos_fallidos_consecutivos = 0
        movimientos_totales = 0
        ultimo_pais_origen = None
        ultimo_pais_destino = None
        movimientos =  {}
        while movimientos_totales < movimientos_maximos and movimientos_fallidos_consecutivos < 3:
            estado_actual = estado_a_vector(self, tablero)

            # Estrategia de Exploración
            if random.random() < self.epsilon_m:
                self.debug_print("****** Fase de mover tropas con random *****")
                pais_origen, pais_destino, exito_mover = EstrategiasExploracion.mover_tropas(self, tablero)
                
                if pais_origen is None or pais_destino is None:
                    self.debug_print("No se pudo mover tropas. Intentando de nuevo...")
                    movimientos_fallidos_consecutivos += 1
                    continue
                    
            # Estrategia de Explotación
            else:
                self.debug_print("****** Fase de mover tropas con NN *****")
                pais_origen, pais_destino, exito_mover = EstrategiasExplotacion.mover_tropas(self, tablero, estado_actual, lista_nombres_paises)

            ultimo_pais_origen = pais_origen
            ultimo_pais_destino = pais_destino

            # Obtener recompensa
            recompensa = recompensa_total_mover_tropas(tablero, self, pais_origen, pais_destino, exito_mover)
            self.debug_print([exito_mover, " recompensa: ", recompensa])
            
            # Aquí asumo que has creado una clase similar a Atacar_Remember_Train y Reforzar_Remember_Train pero para mover tropas
            Mover_Remember_Train.remember(self, tablero, recompensa, estado_actual, lista_nombres_paises, pais_origen, pais_destino)
            
            movimientos_totales += 1

            if not exito_mover:
                movimientos_fallidos_consecutivos += 1
            else:
                movimientos_fallidos_consecutivos = 0  # Reset
                #self.debug_print(["reforzado de : ",ultimo_pais_origen.get_nombre(),ultimo_pais_destino.get_nombre()])
                key = "Mover de "+ultimo_pais_origen.get_nombre()+" a "+ultimo_pais_destino.get_nombre()
                if key in movimientos.keys():
                    movimientos[key] = movimientos[key] + 1
                else:
                    movimientos[key] = 1
        self.debug_print(movimientos)
        self.freq_moverTropas += 1
        return ultimo_pais_origen, ultimo_pais_destino

    def train(self, batch_size=64,accion="None"):
        if accion =="reforzar":
            Reforzar_Remember_Train.train(self,batch_size)
        elif accion == "atacar":
            Atacar_Remember_Train.train(self,batch_size)
        elif accion == "mover":
            Mover_Remember_Train.train(self,batch_size)
        else:
            raise ValueError(f"Error no existe el comando : {accion}")


    def retropropagar_recompensa(self, recompensa_final):
        """Retropropagar la recompensa a través de las memorias del jugador."""

        # Función auxiliar para retropropagar la recompensa en una memoria específica
        def retropropagar_en_memoria(memoria, recompensa_final, gamma):
            retropropagado = []
            for t in reversed(memoria):
                recompensa_final = t[2] + gamma * recompensa_final
                estado, accion, _, proximo_estado = t
                retropropagado.append((estado, accion, recompensa_final, proximo_estado))
            return retropropagado

        # Retropropagar en memoria de refuerzo
        #for t in self.memory_refuerzo:
            #print(t[2])
        #print("*****************************")
        self.memory_refuerzo = retropropagar_en_memoria(self.memory_refuerzo, recompensa_final, self.gamma_refuerzo)
        #for t in self.memory_refuerzo:
            #print(t[2])
        # Retropropagar en memoria de ataque
        self.memory_ataque = retropropagar_en_memoria(self.memory_ataque, recompensa_final, self.gamma_ataque)

        # Retropropagar en memoria de movimiento
        self.memory_mover = retropropagar_en_memoria(self.memory_mover, recompensa_final, self.gamma_mover)
        
        #self.train(accion="reforzar")
        #self.train(accion="atacar")
        #self.train(accion="mover")
        
        #self.save()

    def informar_victoria(self, tablero):
        """Notificar al agente que ha ganado."""
        self.debug_print("¡Victoria notificada!")
        recompensa = 10
        self.retropropagar_recompensa(recompensa)

    def informar_perdida(self, tablero, recompensa = -10):
        """Notificar al agente que ha perdido."""
        self.debug_print(["Derrota notificada.",recompensa])
        self.retropropagar_recompensa(recompensa)

