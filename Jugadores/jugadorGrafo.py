from Jugadores.jugador import Jugador
import networkx as nx
import random

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