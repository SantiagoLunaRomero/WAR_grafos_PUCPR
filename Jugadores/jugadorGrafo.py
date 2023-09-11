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
        # Identificar una lista de países objetivo según la misión
        paises_objetivo = self.identificar_paises_objetivo(tablero)

        # Verificar si hay países objetivo
        if not paises_objetivo:
            print("_________________________________No hay países objetivo para reforzar. Reforzando al azar.")
            pais_a_reforzar = random.choice(self.paises)
            tablero.reforzar_pais(pais_a_reforzar.nombre, self.tropas_por_turno, self)
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
                    
                    # Usar la función de tablero para reforzar el país
                    tablero.reforzar_pais(pais.nombre, tropas_a_asignar, self)
                    tropas_disponibles -= tropas_a_asignar

            if tropas_disponibles == 0:
                break

        # Si aún hay tropas disponibles, distribuirlas equitativamente entre los países
        if tropas_disponibles > 0:
            tropas_por_pais = tropas_disponibles // len(self.paises)
            for pais in self.paises:
                tablero.reforzar_pais(pais.nombre, tropas_por_pais, self)


    def identificar_paises_objetivo(self, tablero):
        paises_objetivo = []

        # Objetivo: Conquistar continentes específicos
        if self.objetivos['continentes']:
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.continente in self.objetivos['continentes'] and pais.jugador != self]

        # Considerar el objetivo especial de un tercer continente
        if self.objetivos.get('tercero', False):
            tercer_continente = self.identificar_tercer_continente()
            paises_objetivo += [pais for pais in tablero.paises.values() if pais.continente == tercer_continente and pais.jugador != self]

        # Objetivo: Conquistar un cierto número de territorios
        if self.objetivos['territorios']:
            paises_objetivo += [pais for pais in tablero.paises.values() if pais.jugador != self]

        # Objetivo: Destruir un color específico
        if self.objetivos['destruir_color']:
            paises_objetivo += [pais for pais in tablero.paises.values() if pais.jugador.color == self.objetivos['destruir_color']]

        # Eliminar duplicados
        paises_objetivo = list(set(paises_objetivo))

        return paises_objetivo

    def atacar(self, tablero):
        print("fase de ataque grafo")
        # 1. Determinar los países objetivo en función de la misión
        paises_objetivo = self.interpretar_objetivo_ataque(tablero)

        # 2. Construir el grafo con peso
        G = tablero.construir_grafo_con_peso()

        # 3. Identificar el país objetivo más cercano
        distancias_objetivo = {}
        for pais in self.paises:
            distancias = nx.single_source_dijkstra_path_length(G, pais.nombre, weight='weight')
            for objetivo in paises_objetivo:
                if objetivo not in distancias_objetivo:
                    distancias_objetivo[objetivo] = distancias[objetivo.nombre]
                else:
                    distancias_objetivo[objetivo] = min(distancias_objetivo[objetivo], distancias[objetivo.nombre])
        if not distancias_objetivo:
            return
        objetivo_mas_cercano = min(distancias_objetivo, key=distancias_objetivo.get)

        # 4. Identificar el vecino más cercano a ese país objetivo y que pertenezca al jugador
        distancias_vecinos = {}
        for vecino in objetivo_mas_cercano.vecinos:
            pais_vecino = tablero.paises[vecino]
            if pais_vecino.jugador == self:
                distancias_vecinos[pais_vecino] = nx.dijkstra_path_length(G, pais_vecino.nombre, objetivo_mas_cercano.nombre, weight='weight')

        # Verificar si hay vecinos válidos
        if not distancias_vecinos:
            return  # Si no hay vecinos válidos, termina la función

        pais_vecino_mas_cercano = min(distancias_vecinos, key=distancias_vecinos.get)

        # 5. Atacar ese vecino si cumple con las condiciones
        if objetivo_mas_cercano.nombre in pais_vecino_mas_cercano.vecinos and pais_vecino_mas_cercano.tropas > objetivo_mas_cercano.tropas * 1.5:
            tablero.batalla(pais_vecino_mas_cercano, objetivo_mas_cercano,self)




    def interpretar_objetivo_ataque(self, tablero):
        # Determinar los países objetivo en función de la misión
        paises_objetivo = []
        if self.objetivos['continentes']:
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.continente in self.objetivos['continentes'] and pais.jugador != self]
        elif self.objetivos['territorios']:
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.jugador != self]
        elif self.objetivos['destruir_color']:
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.jugador.color == self.objetivos['destruir_color']]
        else:
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            paises_objetivo = [pais for pais in tablero.paises.values() if pais.jugador != self]

        # Considerar el objetivo especial de un tercer continente
        if hasattr(self.objetivos, 'tercero') and self.objetivos['tercero']:
            tercer_continente = self.identificar_tercer_continente()
            paises_objetivo += [pais for pais in tablero.paises.values() if pais.continente == tercer_continente and pais.jugador != self]

        return paises_objetivo

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

        # Crear una lista de todos los posibles pares de países origen-destino
        posibles_movimientos = [(origen, destino) for origen in self.paises for destino in paises_objetivo if destino.nombre in origen.vecinos]

        # Si no hay posibles movimientos, simplemente regresa
        if not posibles_movimientos:
            return

        # Seleccionar el par que optimiza nuestras condiciones
        mejor_movimiento = max(posibles_movimientos, key=lambda x: (x[0].tropas, -pesos[x[1]]))

        pais_origen, pais_destino = mejor_movimiento

        tropas_disponibles = pais_origen.tropas_disponibles_para_mover()
        if pais_origen.tropas > 1:
            tropas_a_mover = (pais_origen.tropas - pais_destino.tropas) // 2
            tropas_a_mover = min(tropas_a_mover, tropas_disponibles)
            if tropas_a_mover > 0:
                tablero.mover_tropas(pais_origen.nombre, pais_destino.nombre, tropas_a_mover)

