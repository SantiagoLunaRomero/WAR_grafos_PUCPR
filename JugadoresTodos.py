from Tablero import Tablero
import networkx as nx
import random

from misiones import misiones
class Jugador:
    def __init__(self, nombre, color, mision):
        self.nombre = nombre
        self.color = color  # Añadimos el atributo color
        self.mision = mision
        self.paises = []
        self.tropas_por_turno = 4

    def reforzar(self, tablero):
        pass

    def atacar(self, tablero):
        pass

    def mover_tropas(self, tablero):
        pass
    def imprimir_paises(self):
      print(f"{self.nombre} posee los siguientes países:")
      for pais in self.paises:
          print(pais.nombre)
    def mostrar_mision(self):
      print(f"La misión de {self.nombre} es: {self.mision.descripcion}")
    def get_mision(self):
      return self.mision.descripcion
    
class JugadorMisionCompleja(Jugador):
    def __init__(self, nombre, color, mision):
        super().__init__(nombre, color, mision)
        self.interpretar_mision(mision)

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

    def reforzar(self, tablero):
        # Objetivo: Conquistar continentes específicos
        if self.objetivos['continentes']:
            # Identificar países en los continentes objetivo que aún no hemos conquistado completamente
            paises_objetivo = [pais for pais in self.paises if pais.continente in self.objetivos['continentes']]
            
            # Reforzar los países más vulnerables en los continentes objetivo
            pais_a_reforzar = min(paises_objetivo, key=lambda pais: pais.tropas, default=None)

        # Objetivo: Conquistar un cierto número de territorios
        elif self.objetivos['territorios']:
            # Reforzar los países con menos tropas para protegerlos
            pais_a_reforzar = min(self.paises, key=lambda pais: pais.tropas)

        # Objetivo: Destruir un color específico
        elif self.objetivos['destruir_color']:
            # Identificar países que son vecinos de ese color
            paises_vecinos_al_color = [pais for pais in self.paises if any(tablero.paises[vecino].jugador.color == self.objetivos['destruir_color'] for vecino in pais.vecinos)]
            
            # Reforzar los países vecinos al color objetivo que tienen menos tropas
            pais_a_reforzar = min(paises_vecinos_al_color, key=lambda pais: pais.tropas, default=None)

        else:
            # Si no hay un objetivo claro (o algo salió mal), simplemente refuerza el país con menos tropas
            pais_a_reforzar = min(self.paises, key=lambda pais: pais.tropas)

        # Aplicar el refuerzo
        if pais_a_reforzar:
            pais_a_reforzar.tropas += self.tropas_por_turno


    def atacar(self, tablero):
        puede_atacar = True
        while puede_atacar:
            # Objetivo: Conquistar continentes específicos
            if self.objetivos['continentes']:
                paises_a_atacar = [pais for pais in tablero.paises.values() if pais.continente in self.objetivos['continentes'] and pais.jugador != self]

            # Objetivo: Conquistar un cierto número de territorios
            elif self.objetivos['territorios']:
                paises_a_atacar = [pais for pais in tablero.paises.values() if pais.jugador != self]

            # Objetivo: Destruir un color específico
            elif self.objetivos['destruir_color']:
                paises_a_atacar = [pais for pais in tablero.paises.values() if pais.jugador.color == self.objetivos['destruir_color']]

            else:
                paises_a_atacar = [pais for pais in tablero.paises.values() if pais.jugador != self]

            # Si no hay países a atacar, termina el turno de ataque
            if not paises_a_atacar:
                return

            # Selecciona el país objetivo para el ataque (el más débil)
            pais_objetivo = min(paises_a_atacar, key=lambda pais: pais.tropas)

            # Selecciona el país de origen para el ataque (el más fuerte entre los vecinos del objetivo)
            paises_origen_posibles = [pais for pais in self.paises if pais.tropas > 1 and pais_objetivo.nombre in pais.vecinos]
            pais_origen = max(paises_origen_posibles, key=lambda pais: pais.tropas, default=None)

            # Ataca el país objetivo si hay un país de origen válido
            if pais_origen:
                tablero.batalla(pais_origen, pais_objetivo)
                puede_atacar = any(pais.tropas > 1 for pais in self.paises)
            else:
                puede_atacar = False


    def mover_tropas(self, tablero):
        # Objetivo: Conquistar continentes específicos
        if self.objetivos['continentes']:
            # Identificar países en las fronteras de los continentes objetivo
            paises_frontera = [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self and tablero.paises[vecino].continente in self.objetivos['continentes'] for vecino in pais.vecinos)]

        # Objetivo: Conquistar un cierto número de territorios
        elif self.objetivos['territorios']:
            # Identificar países en las fronteras con otros jugadores
            paises_frontera = [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)]

        # Objetivo: Destruir un color específico
        elif self.objetivos['destruir_color']:
            # Identificar países en las fronteras con el color objetivo
            paises_frontera = [pais for pais in self.paises if any(tablero.paises[vecino].jugador.color == self.objetivos['destruir_color'] for vecino in pais.vecinos)]

        else:
            # Si no hay un objetivo claro, simplemente identifica países en las fronteras con otros jugadores
            paises_frontera = [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)]

        if paises_frontera:
            # Seleccionar el país de origen (el que tiene más tropas)
            pais_origen = max(paises_frontera, key=lambda pais: pais.tropas)
            
            # Seleccionar el país destino (el vecino con menos tropas)
            pais_destino_nombre = min(pais_origen.vecinos, key=lambda nombre: tablero.paises[nombre].tropas)
            pais_destino = tablero.paises[pais_destino_nombre]

            # Calcular las tropas a mover (dejando al menos una tropa en el país de origen)
            tropas_a_mover = pais_origen.tropas - 1

            if tropas_a_mover > 0:
                pais_origen.tropas -= tropas_a_mover
                pais_destino.tropas += tropas_a_mover

class JugadorGrafo(Jugador):
    def __init__(self, nombre, color, mision):
        super().__init__(nombre, color, mision)
        self.interpretar_mision(mision)

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

    def reforzar_a(self, tablero):
        # Objetivo: Conquistar continentes específicos
        if self.objetivos['continentes']:
            paises_objetivo = [pais for pais in self.paises if pais.continente in self.objetivos['continentes']]
            pesos = tablero.calcular_pesos(self, paises_objetivo)
            pais_a_reforzar = min(paises_objetivo, key=lambda pais: pesos[pais], default=None)

        # Objetivo: Conquistar un cierto número de territorios
        elif self.objetivos['territorios']:
            paises_objetivo = [pais for pais in self.paises if pais.tropas < 2]  # Reforzar países con menos de dos tropas
            pesos = tablero.calcular_pesos(self, paises_objetivo)
            pais_a_reforzar = min(paises_objetivo, key=lambda pais: pesos[pais], default=None)

        # Objetivo: Destruir un color específico
        elif self.objetivos['destruir_color']:
            paises_vecinos_al_color = [pais for pais in self.paises if any(tablero.paises[vecino].jugador.color == self.objetivos['destruir_color'] for vecino in pais.vecinos)]
            pesos = tablero.calcular_pesos(self, paises_vecinos_al_color)
            pais_a_reforzar = min(paises_vecinos_al_color, key=lambda pais: pesos[pais], default=None)

        else:
            # Si no hay un objetivo claro (o algo salió mal), simplemente refuerza el país con menos tropas
            pais_a_reforzar = min(self.paises, key=lambda pais: pais.tropas)

        # Aplicar el refuerzo
        if pais_a_reforzar:
            pais_a_reforzar.tropas += self.tropas_por_turno

    def reforzar(self, tablero):
       # Identificar una lista de países objetivo según la misión
        paises_objetivo = self.identificar_paises_objetivo(tablero)
            # Verificar si hay países objetivo
        if not paises_objetivo:
            print("_________________________________No hay países objetivo para reforzar. Reforzando al azar.")
            pais_a_reforzar = random.choice(self.paises)
            pais_a_reforzar.tropas += self.tropas_por_turno
            return

        G = tablero.construir_grafo_con_peso()

        # Calcular los caminos más cortos a los países objetivo
        distancias_objetivo = {}
        for pais in self.paises:
            distancias = nx.single_source_dijkstra_path_length(G, pais.nombre, weight='weight')
            distancias_objetivo[pais] = min(distancias[objetivo.nombre] for objetivo in paises_objetivo)

        # Ordenar los países actuales del jugador por proximidad a los objetivos
        paises_por_reforzar = sorted(self.paises, key=lambda pais: distancias_objetivo[pais])

        # Distribuir las tropas, teniendo en cuenta la comparación con los vecinos
        tropas_disponibles = self.tropas_por_turno
        for pais in paises_por_reforzar:
            for vecino_nombre in pais.vecinos:
                vecino = tablero.paises[vecino_nombre]
                if vecino.jugador != self and pais.tropas <= vecino.tropas:
                    tropas_necesarias = vecino.tropas - pais.tropas + 1
                    tropas_a_asignar = min(tropas_necesarias, tropas_disponibles)
                    pais.tropas += tropas_a_asignar
                    tropas_disponibles -= tropas_a_asignar

            if tropas_disponibles == 0:
                break

        # Si aún hay tropas disponibles, distribuirlas equitativamente entre los países
        if tropas_disponibles > 0:
            tropas_por_pais = tropas_disponibles // len(self.paises)
            for pais in self.paises:
                pais.tropas += tropas_por_pais

    def identificar_paises_objetivo(self, tablero):
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
        print("////////////////////////////////////////////////////////////////////////")
        return [pais for pais in tablero.paises.values() if pais.jugador != self]

    def atacar(self, tablero):
        # 1. Determinar los países objetivo en función de la misión
        paises_objetivo = self.interpretar_objetivo_ataque(tablero)

        # 2. Construir el grafo con peso
        G = tablero.construir_grafo_con_peso()

        # 3. Encontrar vecinos y países accesibles
        ataques_convenientes = []
        for objetivo in paises_objetivo:
            for vecino in objetivo.vecinos:
                pais_vecino = tablero.paises[vecino]
                if pais_vecino.jugador == self and pais_vecino.tropas > 1:
                    camino = nx.shortest_path(G, source=vecino, target=objetivo.nombre, weight='weight')
                    if camino:
                        pais_origen = tablero.paises[camino[0]]
                        # 4. Seleccionar ataques convenientes
                        if pais_origen.tropas > objetivo.tropas * 1.5:  # Condición de conveniencia
                            ataques_convenientes.append((pais_origen, objetivo))

        # 5. Realizar ataques
        for origen, destino in ataques_convenientes:
            tablero.batalla(origen, destino)

    def interpretar_objetivo_ataque(self, tablero):
        # Determinar los países objetivo en función de la misión
        if self.objetivos['continentes']:
            return [pais for pais in tablero.paises.values() if pais.continente in self.objetivos['continentes'] and pais.jugador != self]
        elif self.objetivos['territorios']:
            return [pais for pais in tablero.paises.values() if pais.jugador != self]
        elif self.objetivos['destruir_color']:
            return [pais for pais in tablero.paises.values() if pais.jugador.color == self.objetivos['destruir_color']]
        else:
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            return [pais for pais in tablero.paises.values() if pais.jugador != self]

    def mover_tropas(self, tablero):
        # Objetivo: Conquistar continentes específicos
        if self.objetivos['continentes']:
            paises_frontera = self.obtener_paises_frontera(tablero)
            paises_objetivo = [pais for pais in paises_frontera if pais.continente in self.objetivos['continentes']]
            self.realizar_movimiento(tablero, paises_objetivo)

        # Objetivo: Conquistar un cierto número de territorios
        elif self.objetivos['territorios']:
            paises_frontera = self.obtener_paises_frontera(tablero)
            paises_objetivo = [pais for pais in paises_frontera if pais.tropas < 2]
            self.realizar_movimiento(tablero, paises_objetivo)

        # Objetivo: Destruir un color específico
        elif self.objetivos['destruir_color']:
            paises_frontera = self.obtener_paises_frontera(tablero)
            paises_objetivo = [pais for pais in paises_frontera if any(tablero.paises[vecino].jugador.color == self.objetivos['destruir_color'] for vecino in pais.vecinos)]
            self.realizar_movimiento(tablero, paises_objetivo)

        else:
            # Si no hay un objetivo claro, mover tropas para equilibrar la frontera
            paises_frontera = self.obtener_paises_frontera(tablero)
            self.realizar_movimiento(tablero, paises_frontera)

    def obtener_paises_frontera(self, tablero):
        return [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)]

    def realizar_movimiento(self, tablero, paises_objetivo):
        pesos = tablero.calcular_pesos(self, paises_objetivo)
        pais_origen = max(self.paises, key=lambda pais: pais.tropas, default=None)
        pais_destino = min(paises_objetivo, key=lambda pais: pesos[pais], default=None)

        if pais_origen and pais_destino and pais_origen.tropas > 1:
            tropas_a_mover = (pais_origen.tropas - pais_destino.tropas) // 2
            if tropas_a_mover > 0:
                pais_origen.tropas -= tropas_a_mover
                pais_destino.tropas += tropas_a_mover

class JugadorGrafoOptimizado(Jugador):
    def __init__(self, nombre, color, mision):
        super().__init__(nombre, color, mision)
        self.interpretar_mision(mision)

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

    def reforzar(self, tablero):
        # Identificar una lista de países objetivo según la misión
        paises_objetivo = self.identificar_paises_objetivo(tablero)
        
        # Identificar posiciones clave
        posiciones_clave = self.identificar_posiciones_clave(tablero)

        # Verificar si hay países objetivo
        if not paises_objetivo:
            print("No hay países objetivo para reforzar. Reforzando al azar.")
            pais_a_reforzar = random.choice(self.paises)
            pais_a_reforzar.tropas += self.tropas_por_turno
            return

        G = tablero.construir_grafo_con_peso()

        # Calcular los caminos más cortos a los países objetivo
        distancias_objetivo = {}
        for pais in self.paises:
            distancias = nx.single_source_dijkstra_path_length(G, pais.nombre, weight='weight')
            distancias_objetivo[pais] = min(distancias[objetivo.nombre] for objetivo in paises_objetivo)

        # Ordenar los países actuales del jugador por proximidad a los objetivos y posiciones clave
        paises_por_reforzar = sorted(self.paises, key=lambda pais: (distancias_objetivo[pais], pais.nombre not in posiciones_clave))

        # Distribuir las tropas, teniendo en cuenta la comparación con los vecinos y posiciones clave
        tropas_disponibles = self.tropas_por_turno
        for pais in paises_por_reforzar:
            for vecino_nombre in pais.vecinos:
                vecino = tablero.paises[vecino_nombre]
                if vecino.jugador != self and pais.tropas <= vecino.tropas:
                    tropas_necesarias = vecino.tropas - pais.tropas + 1
                    tropas_a_asignar = min(tropas_necesarias, tropas_disponibles)
                    pais.tropas += tropas_a_asignar
                    tropas_disponibles -= tropas_a_asignar

            if tropas_disponibles == 0:
                break

        # Si aún hay tropas disponibles, distribuirlas equitativamente entre los países
        if tropas_disponibles > 0:
            tropas_por_pais = tropas_disponibles // len(self.paises)
            for pais in self.paises:
                pais.tropas += tropas_por_pais

    def identificar_paises_objetivo(self, tablero):
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
        print("////////////////////////////////////////////////////////////////////////")
        return [pais for pais in tablero.paises.values() if pais.jugador != self]

    def identificar_posiciones_clave(self, tablero):
        G = tablero.construir_grafo_con_peso()
        centralidad_intermediacion = nx.betweenness_centrality(G, weight='weight')
        centralidad_cercania = nx.closeness_centrality(G, distance='weight')
        
        # Factor de enemigos vecinos
        factor_enemigos = {pais.nombre: sum(tablero.paises[vecino].tropas for vecino in pais.vecinos if tablero.paises[vecino].jugador != self) for pais in self.paises}

        # Número de jugadores (para personalizar el umbral)
        num_jugadores = len(set(pais.jugador for pais in tablero.paises.values()))

        # Umbral adaptativo
        umbral = 0.1 * num_jugadores

        # Combinar métricas
        posiciones_clave = []
        for pais, centrality in centralidad_intermediacion.items():
            cercania = centralidad_cercania.get(pais, 0)
            enemigos = factor_enemigos.get(pais, 0)
            score = centrality + cercania - (enemigos * 0.01) # Ponderación de enemigos
            if score > umbral:
                posiciones_clave.append(pais)

        return posiciones_clave


    def atacar(self, tablero):
        # 1. Determinar los países objetivo en función de la misión
        paises_objetivo = self.interpretar_objetivo_ataque(tablero)

        # 2. Construir el grafo con peso
        G = tablero.construir_grafo_con_peso()

        # 3. Encontrar vecinos y países accesibles
        ataques_convenientes = []
        for objetivo in paises_objetivo:
            for vecino in objetivo.vecinos:
                pais_vecino = tablero.paises[vecino]
                if pais_vecino.jugador == self and pais_vecino.tropas > 1:
                    camino = nx.shortest_path(G, source=vecino, target=objetivo.nombre, weight='weight')
                    if camino:
                        pais_origen = tablero.paises[camino[0]]
                        # 4. Seleccionar ataques convenientes
                        if pais_origen.tropas > objetivo.tropas * 1.5:  # Condición de conveniencia
                            ataques_convenientes.append((pais_origen, objetivo))

        # 5. Realizar ataques
        for origen, destino in ataques_convenientes:
            tablero.batalla(origen, destino)

    def interpretar_objetivo_ataque(self, tablero):
        # Determinar los países objetivo en función de la misión
        if self.objetivos['continentes']:
            return [pais for pais in tablero.paises.values() if pais.continente in self.objetivos['continentes'] and pais.jugador != self]
        elif self.objetivos['territorios']:
            return [pais for pais in tablero.paises.values() if pais.jugador != self]
        elif self.objetivos['destruir_color']:
            return [pais for pais in tablero.paises.values() if pais.jugador.color == self.objetivos['destruir_color']]
        else:
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            return [pais for pais in tablero.paises.values() if pais.jugador != self]

    def mover_tropas(self, tablero):
        # Identificar los países objetivo según los objetivos
        paises_objetivo = self.identificar_paises_objetivo(tablero)
        if not paises_objetivo:
            paises_objetivo = self.obtener_paises_frontera(tablero)  # Si no hay objetivos claros, enfocarse en la frontera

        # Realizar movimientos basados en los países objetivo
        self.realizar_movimiento(tablero, paises_objetivo)


    def obtener_paises_frontera(self, tablero):
        return [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)]

    def realizar_movimiento(self, tablero, paises_objetivo):
        G = tablero.construir_grafo_con_peso()

        for pais_destino in paises_objetivo:
            # Encuentra el país de origen basado en la proximidad y la cantidad de tropas
            distancias = nx.single_source_dijkstra_path_length(G, pais_destino.nombre, weight='weight')
            pais_origen = min(self.paises, key=lambda pais: distancias[pais.nombre] + (1 / (pais.tropas + 1)), default=None)

            # Verifica si el movimiento es conveniente
            if pais_origen and pais_destino and pais_origen.tropas > pais_destino.tropas + 1:
                tropas_a_mover = (pais_origen.tropas - pais_destino.tropas) // 2
                pais_origen.tropas -= tropas_a_mover
                pais_destino.tropas += tropas_a_mover

class JugadorAleatorio(Jugador):
    def __init__(self, nombre, color, mision):
        super().__init__(nombre, color, mision)

    def reforzar(self, tablero):
        # Refuerza un país al azar
        pais_a_reforzar = random.choice(self.paises)
        pais_a_reforzar.tropas += self.tropas_por_turno

    def atacar(self, tablero):
        while True:
            # Ataca un país al azar
            paises_a_atacar = [pais for pais in tablero.paises.values() if pais.jugador != self]

            # Si no hay países a atacar, termina el turno de ataque
            if not paises_a_atacar:
                return

            pais_objetivo = random.choice(paises_a_atacar)

            # Selecciona un país de origen para el ataque que tenga suficientes tropas
            paises_origen_posibles = [pais for pais in self.paises if pais.tropas > 1]

            # Si no hay países de origen posibles, termina el turno de ataque
            if not paises_origen_posibles:
                return

            pais_origen = random.choice(paises_origen_posibles)

            # Ataca el país objetivo
            tablero.batalla(pais_origen, pais_objetivo)

    def mover_tropas(self, tablero):
        # Mueve las tropas de un país al azar a otro país al azar
        paises_origen_posibles = [pais for pais in self.paises if pais.tropas > 1]

        # Si no hay países de origen posibles, no hace nada
        if not paises_origen_posibles:
            return

        pais_origen = random.choice(paises_origen_posibles)
        pais_destino = random.choice(self.paises)

        tropas_a_mover = random.randint(1, pais_origen.tropas - 1)
        pais_origen.tropas -= tropas_a_mover
        pais_destino.tropas += tropas_a_mover

def crear_jugador(tipo, nombre, color, mision):
    if tipo == "JugadorMisionCompleja":
        return JugadorMisionCompleja(nombre, color, mision)
    elif tipo == "JugadorGrafo":
        return JugadorGrafo(nombre, color, mision) 
    elif tipo == "aleatorio":
        return JugadorAleatorio(nombre, color, mision)
    elif tipo == "JugadorGrafoOptimizado":
        return JugadorGrafoOptimizado(nombre, color, mision)
    else:
        raise ValueError(f"Tipo de jugador desconocido: {tipo}")

jugadores_info = [
    ("JugadorMisionCompleja", "Complejo 1", "red", misiones[0]),
    ("JugadorGrafo", "grafo 1", "blue", misiones[1]),
    ("JugadorGrafoOptimizado", "Optimizado 1", "green",misiones[2]),
    ("aleatorio", "aleatorio 1", "yellow", misiones[3]),
    ("aleatorio", "aleatorio 2", "black", misiones[4]),
    ("JugadorGrafo", "grafo 2", "purple", misiones[12]),
]

jugadores = [crear_jugador(tipo, nombre, color, mision) for (tipo, nombre, color, mision) in jugadores_info]

tablero = Tablero(jugadores)