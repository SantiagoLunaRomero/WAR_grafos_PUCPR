from Jugadores.jugador import Jugador
import networkx as nx
import random
import math
from collections import defaultdict

class JugadorGrafoOptimizado(Jugador):
    def __init__(self, nombre, color, mision):
        super().__init__(nombre, color, mision)
        self.interpretar_mision(mision)
        self.turnos_jugados = 0  # Para decidir la etapa del juego

    def interpretar_mision(self, mision):
        self.objetivos = {
            'continentes': [],
            'territorios': 0,
            'tropas_minimas': 0,
            'destruir_color': None
        }

        descripcion = mision.descripcion

        # Interpretar las misiones de conquistar continentes
        if "Conquistar na totalidade" in descripcion:
            continentes = ['América del Norte', 'América del Sur', 'Europa', 'África', 'Asia', 'Oceanía']
            for continente in continentes:
                if continente in descripcion:
                    self.objetivos['continentes'].append(continente)
            print("_____ se ha establecido la mision de conquistar continentonces : ",self.objetivos['continentes'])
        
        if 'Europa' in self.objetivos['continentes'] and 'Oceanía' in self.objetivos['continentes']:
            self.objetivos['tercero'] = True
            print("Es neceseario tambien un continente extra : ")

        # Interpretar la misión de conquistar 18 territorios con al menos dos ejércitos
        if "Conquistar 18 TERRITÓRIOS" in descripcion:
            self.objetivos['territorios'] = 18
            self.objetivos['tropas_minimas'] = 2

        # Interpretar la misión de conquistar 24 territorios a elección
        if "Conquistar 24 TERRITÓRIOS" in descripcion:
            self.objetivos['territorios'] = 24

        # Interpretar las misiones de destruir ejércitos de un color específico
        colores = ['red', 'blue', 'green', 'yellow', 'black', 'purple'] #['Azul', 'Amarillo', 'Vermelho', 'Preto', 'Branco', 'Verde']
        for color in colores:
          if f"Destruir totalmente OS EXÉRCITOS {color}" in descripcion:
              self.objetivos['destruir_color'] = color
    

    def identificar_tercer_continente(self):
        continentes = ['América del Norte', 'América del Sur', 'África', 'Asia']
        pais_count_por_continente = {continente: sum(1 for pais in self.paises if pais.continente == continente) for continente in continentes}
        return max(pais_count_por_continente, key=pais_count_por_continente.get)

            
    def reforzar(self, tablero):
        self.turnos_jugados += 1
        refuerzos = defaultdict(int)  # Registrar cada refuerzo
        for _ in range(self.tropas_por_turno):
            recompensa_actual = self.calcular_recompensa_mision(tablero, self.mision.descripcion) * (1 + self.turnos_jugados * 0.05)  # La recompensa aumenta con los turnos
            paises_evaluados = self.evaluar_paises(tablero, recompensa_actual)
            # Ordenamos los países por sus puntuaciones de evaluación
            paises_ordenados = sorted(paises_evaluados, key=paises_evaluados.get, reverse=True)
            
            while paises_ordenados:
                pais_a_reforzar = paises_ordenados.pop(0)
                vecinos_enemigos = [tablero.paises[vecino] for vecino in pais_a_reforzar.vecinos if tablero.paises[vecino].jugador != self]
                
                # Si el país ya tiene una ventaja significativa sobre todos sus vecinos enemigos, considera el siguiente país
                if all(pais_a_reforzar.tropas > vecino.tropas * 10 for vecino in vecinos_enemigos):
                    continue
                else:
                    #print("reforzando pais :",pais_a_reforzar.get_nombre())
                    result = tablero.reforzar_pais(pais_a_reforzar.nombre, 1, self)
                    print(result)
                    if result[0]:
                        refuerzos[pais_a_reforzar.nombre] += 1
                        print("Dueno del pais:",pais_a_reforzar.jugador)
                        break
                    else :
                        continue
            else:
                # Si todos los países ya tienen una ventaja significativa, simplemente reforzamos el país originalmente elegido
                pais_a_reforzar = max(paises_evaluados, key=paises_evaluados.get)
                #print("reforzando pais :",pais_a_reforzar.get_nombre())
                result =tablero.reforzar_pais(pais_a_reforzar.nombre, 1, self)
                if result[0]:
                    refuerzos[pais_a_reforzar.nombre] += 1
                    print("Dueno del pais:",pais_a_reforzar.jugador)

        vector=[0] * 47
        nombres = list(tablero.paises.keys())
        vector[0:5]=[0,255,0,0,0]
        # Imprimir un resumen de los refuerzos al final
        for pais, cantidad in refuerzos.items():
            print(f"Reforzado el país {pais} con {cantidad} tropas.")
            indice = nombres.index(pais)
            vector[indice + 5] = cantidad
        print(vector)
        return vector
    def factor_priorizacion_mision(self):
        # Ajustamos según la necesidad: estos valores determinan cuándo comienza a priorizar la misión
        escala = 0.3
        desplazamiento = 5  # Comienza a priorizar la misión después de 5 turnos
    
        return 1 / (1 + math.exp(-escala * (self.turnos_jugados - desplazamiento)))
    

    def evaluar_paises(self, tablero, recompensa_actual):
        puntuaciones = {}
        factor_mision = self.factor_priorizacion_mision()
        # Establecer puntuaciones base basadas en la misión

        paises_cercano_objetivo = self.identificar_paises_cercanos_a_objetivos(tablero)

        for pais in self.paises:
            puntuaciones[pais] = 10 * factor_mision if pais in paises_cercano_objetivo else 0

        # Ajustar puntuaciones por conectividad y potencial estratégico
        for pais in self.paises:
            puntuaciones[pais] += len(pais.vecinos)  # Aumenta la puntuación por cada vecino que tenga

        # Si la misión es conquistar 18 territorios con al menos dos ejércitos
        if self.objetivos['territorios']:
            for pais in self.paises:
                if pais.tropas < 2:
                    puntuaciones[pais] += 10000  # Dar una alta prioridad a estos países

        # Ajustar puntuaciones por posición relativa de las tropas enemigas
        for pais in self.paises:
            tropas_enemigas_cercanas = sum(tablero.paises[vecino].tropas for vecino in pais.vecinos if tablero.paises[vecino].jugador != self)
            if tropas_enemigas_cercanas > pais.tropas:
                puntuaciones[pais] += 5  # Ajuste arbitrario, puedes cambiarlo según la necesidad

        # Ajustar puntuaciones por oportunidades de ataque
        paises_candidatos_ataque = self.identificar_paises_candidatos_ataque(tablero)
        for pais in paises_candidatos_ataque:
            vecino = [vec for vec in pais.vecinos if tablero.paises[vec].jugador != self and tablero.paises[vec].tropas < pais.tropas * 0.75]
            if vecino:
                # Usa el método get() para obtener el valor actual o un valor predeterminado si la clave no existe
                puntuaciones[pais] = puntuaciones.get(pais, 0) + 5

        # Ajustar puntuaciones por defensa en las etapas posteriores del juego
        if self.turnos_jugados > 5:  # Esto es solo un ejemplo; puedes ajustar el número de turnos según lo que consideres una "etapa posterior"
            paises_frontera = [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)]
            for pais in paises_frontera:
                puntuaciones[pais] += 3
        
        # Ajustar por recompensa actual
        for pais in puntuaciones:
            puntuaciones[pais] += recompensa_actual / 100
        
        return puntuaciones
    
    def identificar_paises_cercanos_a_objetivos(self, tablero):
        G = tablero.construir_grafo_con_peso()
        
        # Usamos la función existente para obtener todos los países objetivo
        paises_objetivo = self.identificar_paises_objetivo(tablero)

        paises_cercanos = {}
        for objetivo in paises_objetivo:
            min_distancia = float('inf')
            pais_cercano_actual = None
            for pais in self.paises:
                try:
                    distancia = nx.dijkstra_path_length(G, source=pais.nombre, target=objetivo.nombre, weight='weight')
                    if distancia < min_distancia:
                        min_distancia = distancia
                        pais_cercano_actual = pais
                except nx.NetworkXNoPath:
                    # No hay camino entre 'pais' y 'objetivo'
                    continue
            
            paises_cercanos[objetivo] = pais_cercano_actual

        return paises_cercanos

    def identificar_paises_objetivo(self, tablero):
        # Objetivo: Conquistar continentes específicos
        if self.objetivos['continentes']:
            # Primero, determinamos qué continentes ya hemos conquistado por completo
            continentes_conquistados = [cont for cont in self.objetivos['continentes'] 
                                        if all(pais.jugador == self for pais in tablero.paises.values() if pais.continente == cont)]
            # A continuación, identificamos los países en continentes objetivo que no hemos conquistado y que no nos pertenecen
            paises_objetivo = [pais for pais in tablero.paises.values() 
                            if pais.continente in self.objetivos['continentes'] 
                            and pais.jugador != self 
                            and pais.continente not in continentes_conquistados]
            
            if hasattr(self.objetivos, 'tercero') and self.objetivos['tercero']:
                continentes = ['América del Norte', 'América del Sur', 'África', 'Asia']
                pais_count_por_continente = {continente: sum(1 for pais in self.paises if pais.continente == continente) for continente in continentes}
                tercer_continente = max(pais_count_por_continente, key=pais_count_por_continente.get)
                paises_tercer_continente = [pais for pais in tablero.paises.values() if pais.continente == tercer_continente and pais.jugador != self]
                paises_objetivo.extend(paises_tercer_continente)  # Añadir países del tercer continente a los objetivos

        # Objetivo: Conquistar un cierto número de territorios
        elif self.objetivos['territorios']:
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.jugador != self]
        # Objetivo: Destruir un color específico
        elif self.objetivos['destruir_color']:
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.jugador.color == self.objetivos['destruir_color']]
        # Si no hay un objetivo claro (o algo salió mal), simplemente considera todos los países que no nos pertenecen
        else:
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.jugador != self]
        return paises_objetivo
    
    def a_identificar_paises_objetivo(self, tablero):
        # Objetivo: Conquistar continentes específicos
        if self.objetivos['continentes']:
            return [pais for pais in tablero.paises.values() if pais.continente in self.objetivos['continentes'] and pais.jugador != self]

        # Objetivo: Conquistar un cierto número de territorios
        elif self.objetivos['territorios']:
            return [pais for pais in tablero.paises.values() if pais.jugador != self]

        # Objetivo: Destruir un color específico
        elif self.objetivos['destruir_color']:
            return [pais for pais in tablero.paises.values() if pais.jugador.color == self.objetivos['destruir_color']]

        # Si no hay un objetivo claro (o algo salió mal), simplemente considera todos los países que no nos pertenecen
        return [pais for pais in tablero.paises.values() if pais.jugador != self]

    def identificar_paises_candidatos_ataque(self, tablero):
        """
        Identifica países vecinos débiles que son buenos candidatos para ser atacados.
        """
        candidatos_ataque = []

        for pais in self.paises:
            for vecino_nombre in pais.vecinos:
                vecino = tablero.paises[vecino_nombre]
                if vecino.jugador != self and vecino.tropas < pais.tropas * 0.75:
                    candidatos_ataque.append(vecino)

        return candidatos_ataque
        
    def identificar_pais_a_reforzar_por_objetivo(self, tablero, paises_objetivo):
        G = tablero.construir_grafo_con_peso()
        distancias_objetivo = self.calcular_distancias_objetivo(G, paises_objetivo)
        
        # Ordenar países por proximidad y luego por número de tropas (menos tropas primero)
        paises_ordenados = sorted(self.paises, key=lambda pais: (distancias_objetivo[pais], -pais.tropas))
        
        return paises_ordenados[0] if paises_ordenados else None

    def identificar_pais_a_reforzar_por_frontera(self, tablero):
        paises_frontera = [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)]
        if not paises_frontera:
            return None
        
        # Ordenar los países de la frontera por el número de tropas (menos tropas primero)
        return sorted(paises_frontera, key=lambda pais: pais.tropas)[0]

    def calcular_distancias_objetivo(self, G, paises_objetivo):
        distancias_objetivo = {}
        for pais in self.paises:
            distancias = nx.single_source_dijkstra_path_length(G, pais.nombre, weight='weight')
            distancias_objetivo[pais] = min(distancias[objetivo.nombre] for objetivo in paises_objetivo)
        return distancias_objetivo
    
    def recompensa_por_conquista_continente(self, tablero, continente):
        paises_en_continente = [pais for pais in tablero.paises.values() if pais.continente == continente]
        paises_conquistados = [pais for pais in paises_en_continente if pais.jugador == self]
        return 100 * len(paises_conquistados) / len(paises_en_continente)

    def recompensa_por_conquista_territorios(self, tablero, objetivo):
        territorios_conquistados = len([pais for pais in tablero.paises.values() if pais.jugador == self])
        return max(100 * territorios_conquistados / objetivo, 100)

    def recompensa_por_destruir_color(self, tablero, color):
        territorios_iniciales = len(tablero.paises)
        territorios_actuales = len([pais for pais in tablero.paises.values() if pais.jugador.color == color])
        return 100 * (territorios_iniciales - territorios_actuales) / territorios_iniciales

    def recompensa_por_mision_europa_oceania_tercero(self, tablero):
        recompensa_europa = self.recompensa_por_conquista_continente(tablero, 'Europa')
        recompensa_oceania = self.recompensa_por_conquista_continente(tablero, 'Oceanía')
        # Lista de todos los continentes excepto Europa y Oceanía
        otros_continentes = ['Asia', 'América del Sur', 'África', 'América del Norte']
        recompensas_otros = [self.recompensa_por_conquista_continente(tablero, continente) for continente in otros_continentes]
        # Tomamos la recompensa máxima de los demás continentes
        max_recompensa_otro_continente = max(recompensas_otros)
        return (recompensa_europa + recompensa_oceania + max_recompensa_otro_continente) / 3

    def calcular_recompensa_mision(self, tablero, descripcion):
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
        return 0  #

    def atacar(self, tablero):
        print("Fase de ataque optimizada")

        #while True:
        # Evaluar las mejores opciones de ataque
        paises_ataque_evaluados = self.evaluar_paises_para_ataque(tablero)
        ataques_ordenados = sorted(paises_ataque_evaluados, key=paises_ataque_evaluados.get, reverse=True)
        pass_atack = False
        # Verificar si hay opciones de ataque viables
        if not ataques_ordenados:
            pass_atack = True

        # Seleccionar el mejor ataque viable de la lista ordenada
        mejor_ataque = None
        for ataque in ataques_ordenados:
            origen, destino = ataque
            if origen.tropas > destino.tropas*2:
                mejor_ataque = ataque
                break

        # Si no se encontró un ataque viable, detiene la fase de ataque
        if not mejor_ataque:
            pass_atack = True

        vector=[0] * 47
        if(pass_atack):
            vector[3] = 255
            print(vector)
            return vector
    
        nombres = list(tablero.paises.keys())
        vector[0:5]=[255,0,0,0,0]
        print("Intentando atacar de :", origen.get_nombre(), " a ", destino.get_nombre())
        indice = nombres.index(origen.get_nombre())
        vector[indice + 5] = 255
        indice = nombres.index(destino.get_nombre())
        vector[indice + 5] = 255
        print(vector)
        #tablero.batalla(origen, destino, self)
        return(vector)


    def es_conquista_continente(self, tablero, pais):
        """Verifica si al conquistar el país dado, el jugador conquista todo el continente."""
        continente = pais.continente
        paises_en_continente = [p for p in tablero.paises.values() if p.continente == continente]
        paises_no_conquistados = [p for p in paises_en_continente if p.jugador != self or p == pais]
        
        return len(paises_no_conquistados) == 1

    def bloquea_ruta(self, tablero, pais):
        """Verifica si el país bloquea una ruta entre dos de los países del jugador."""
        # Para simplificar, verificaremos si el país está entre dos de nuestros países
        vecinos_jugador = [vecino for vecino in pais.vecinos if tablero.paises[vecino].jugador == self]
        return len(vecinos_jugador) >= 2

    def evaluar_paises_para_ataque(self, tablero):
        puntuaciones_ataque = {}
        paises_objetivo = self.interpretar_objetivo_ataque(tablero)

        for pais in self.paises:
            for vecino_nombre in pais.vecinos:
                vecino = tablero.paises[vecino_nombre]
                if vecino.jugador != self:
                    # Base: diferencia de tropas
                    puntuacion = pais.tropas - vecino.tropas
                    # Durante los primeros turnos, se prioriza la expansión rápida
                    if self.turnos_jugados < 3:
                        puntuacion += 50 if vecino.tropas < pais.tropas else 0
                    else:
                        # Bonificación por conquistar un continente
                        if self.es_conquista_continente(tablero, vecino):
                            puntuacion += 20

                        # Bonificación por ataque a países vulnerables
                        if vecino.tropas < pais.tropas * 0.5:
                            puntuacion += 30
                        
                        # Penalización por ataque a países fuertemente defendidos
                        elif vecino.tropas > pais.tropas:
                            puntuacion -= 20

                        # Bonificación si el vecino bloquea una ruta de suministro/movimiento
                        if self.bloquea_ruta(tablero, vecino):
                            puntuacion += 20

                        # Bonificación si el vecino es un objetivo según la misión
                        if vecino in paises_objetivo:
                            puntuacion += 50

                    puntuaciones_ataque[(pais, vecino)] = puntuacion

        return puntuaciones_ataque


    def interpretar_objetivo_ataque(self, tablero):
        # Construir el grafo ponderado
        G = tablero.construir_grafo_con_peso()
        
        # Determinar los países objetivo en función de la misión
        paises_objetivo = self.identificar_paises_objetivo(tablero)

        # Considerar el objetivo especial de un tercer continente
        if hasattr(self.objetivos, 'tercero') and self.objetivos['tercero']:
            tercer_continente = self.identificar_tercer_continente()
            paises_objetivo += [pais for pais in tablero.paises.values() if pais.continente == tercer_continente and pais.jugador != self]

        # Para cada país objetivo, determinar el camino más corto y menos costoso hacia él y
        # elegir el país en ese camino que sea más débil o estratégicamente valioso.

        paises_objetivo_inmediato = []
        for objetivo in paises_objetivo:
            for pais in self.paises:
                try:
                    camino = nx.shortest_path(G, source=pais.nombre, target=objetivo.nombre, weight='weight')
                    # Elegimos el país enemigo más débil en el camino
                    pais_debil = min(camino[1:], key=lambda nombre_pais: tablero.paises[nombre_pais].tropas)
                    paises_objetivo_inmediato.append(tablero.paises[pais_debil])
                except nx.NetworkXNoPath:
                    continue

        return paises_objetivo_inmediato

    def a_interpretar_objetivo_ataque(self, tablero):
        # Construir el grafo ponderado
        G = tablero.construir_grafo_con_peso()
        
        # Determinar los países objetivo en función de la misión
        paises_objetivo = []
        if self.objetivos['continentes']:
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.continente in self.objetivos['continentes'] and pais.jugador != self]
        elif self.objetivos['territorios']:
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.jugador != self]
        elif self.objetivos['destruir_color']:
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.jugador.color == self.objetivos['destruir_color']]
        else:
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.jugador != self]

        # Considerar el objetivo especial de un tercer continente
        if hasattr(self.objetivos, 'tercero') and self.objetivos['tercero']:
            tercer_continente = self.identificar_tercer_continente()
            paises_objetivo += [pais for pais in tablero.paises.values() if pais.continente == tercer_continente and pais.jugador != self]

        # Para cada país objetivo, determinar el camino más corto y menos costoso hacia él y
        # elegir el primer país en ese camino como el objetivo inmediato.

        paises_objetivo_inmediato = []
        for objetivo in paises_objetivo:
            for pais in self.paises:
                try:
                    camino = nx.shortest_path(G, source=pais.nombre, target=objetivo.nombre, weight='weight')
                    if len(camino) > 1:
                        pais_inmediato = tablero.paises[camino[1]]
                        paises_objetivo_inmediato.append(pais_inmediato)
                except nx.NetworkXNoPath:
                    continue

        return paises_objetivo_inmediato



    def paises_cercanos_ordenados(self, paises_objetivo, tablero):
        G = tablero.construir_grafo_con_peso()
        paises_cercanos = []

        for pais in self.paises:
            for objetivo in paises_objetivo:
                if nx.has_path(G, pais.nombre, objetivo.nombre):
                    distancia = nx.shortest_path_length(G, source=pais.nombre, target=objetivo.nombre, weight='weight')
                    paises_cercanos.append((pais, distancia))

        # Ordenamos por distancia y retornamos solo los países
        paises_cercanos.sort(key=lambda x: x[1])
        return [pais for pais, _ in paises_cercanos]

    def mover_tropas(self, tablero):
        paises_objetivo = self.identificar_paises_objetivo(tablero)
        """
        # Si el jugador tiene el objetivo de un tercer continente
        if hasattr(self.objetivos, 'tercero') and self.objetivos['tercero']:
            continentes = ['América del Norte', 'América del Sur', 'África', 'Asia']
            pais_count_por_continente = {continente: sum(1 for pais in self.paises if pais.continente == continente) for continente in continentes}
            tercer_continente = max(pais_count_por_continente, key=pais_count_por_continente.get)
            paises_tercer_continente = [pais for pais in tablero.paises.values() if pais.continente == tercer_continente and pais.jugador != self]
            paises_objetivo.extend(paises_tercer_continente)  # Añadir países del tercer continente a los objetivos
        """

        movimientos = defaultdict(int)
        paises_cercanos = self.paises_cercanos_ordenados(paises_objetivo, tablero)
        paises_donados = set()

        for pais in paises_cercanos:
            vecinos_donantes = [tablero.paises[vecino] for vecino in pais.vecinos 
                                if tablero.paises[vecino].jugador == self and tablero.paises[vecino].tropas > 1 and vecino not in paises_donados]

            for vecino in vecinos_donantes:
                tropas_a_mover = vecino.tropas_disponibles_para_mover()
                if "territorios" in self.objetivos:  # Si el objetivo es conquistar territorios
                    tropas_a_mover = max(0, tropas_a_mover - 2)  # Nunca mover más de lo que dejaría al país con menos de dos tropas
                
                while tropas_a_mover > 0:
                    try:
                        tablero.mover_tropas(vecino.nombre, pais.nombre, 1)  # Movemos solo una tropa
                        vecino.mover_tropas(1)
                        #print(f"Se movió 1 tropa de {vecino.nombre} a {pais.nombre}.")
                        movimientos[(vecino.nombre, pais.nombre)] += 1
                        tropas_a_mover -= 1
                    except ValueError as e:
                        #print(f"Error al mover tropa de {vecino.nombre} a {pais.nombre}: {e}")
                        break  # Si hay un error, detenemos el intento de mover más tropas desde ese vecino
                paises_donados.add(vecino.nombre)

       
        nombres = list(tablero.paises.keys())
        print("Resumen de movimientos:")
        action_vectors = []
        for (origen, destino), tropas in movimientos.items():
            vector=[0] * 47
            vector[0:5]=[0,0,255,0,tropas]
            print(f"Mover {tropas} tropas de {origen} a {destino}.")
            indice = nombres.index(origen)
            vector[indice + 5] = 125
            indice = nombres.index(destino)
            vector[indice + 5] = 255
            action_vectors.append(vector)
            print(vector)
            
        if (len(action_vectors) == 0):
            vector=[0] * 47
            vector[0:5]=[0,0,0,255,0]
            print(f"No se movieron tropas")
            action_vectors.append(vector)
        return action_vectors
    
    def step(self, gamestate_matrix, player_index, tablero):
        
        fase_jogo = gamestate_matrix[player_index][-4:]
        self.tropas_por_turno = gamestate_matrix[player_index][44]
        
        print('step - fase jogo -> ', fase_jogo)
        print('step - tropas por turno -> ', self.tropas_por_turno)

        #Reforzar
        if(fase_jogo[1] == 255):
            print("Mis pasies son : ")
            self.imprimir_paises()
            self.actualizar_tropas_por_turno()
            self.iniciar_turno()
            action_vector = self.reforzar(tablero)
            return action_vector
        #Atacar
        elif(fase_jogo[2] == 255):
            action_vector = self.atacar(tablero)
            return action_vector
        #Mover
        elif(fase_jogo[3] == 255):
            action_vector = self.mover_tropas(tablero)
            tablero.reset_tropas_recibidas()
            return action_vector
        #Fortificar
        elif(fase_jogo[0] == 255):
            print(f"Fase de jogo None")
            None
        None