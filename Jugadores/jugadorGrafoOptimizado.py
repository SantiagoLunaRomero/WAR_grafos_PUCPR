from Jugadores.jugador import Jugador
import networkx as nx
import random
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

    def refuerzo_por_proximidad(self, tablero, paises_por_reforzar):
        tropas_disponibles = self.tropas_por_turno
        for pais in paises_por_reforzar:
            for vecino_nombre in pais.vecinos:
                vecino = tablero.paises[vecino_nombre]
                if vecino.jugador != self and pais.tropas <= vecino.tropas:
                    tropas_necesarias = vecino.tropas - pais.tropas + 1
                    tropas_a_asignar = min(tropas_necesarias, tropas_disponibles)
                    tablero.reforzar_pais(pais.nombre, tropas_a_asignar, self)
                    tropas_disponibles -= tropas_a_asignar
                if tropas_disponibles == 0:
                    break
            if tropas_disponibles == 0:
                break
        return tropas_disponibles

    def refuerzo_equitativo(self, tablero, tropas_disponibles):
        tropas_por_pais = tropas_disponibles // len(self.paises)
        tropas_restantes = tropas_disponibles % len(self.paises)
        
        for pais in self.paises:
            tablero.reforzar_pais(pais.nombre, tropas_por_pais, self)

        for pais in self.paises:
            if tropas_restantes > 0:
                tablero.reforzar_pais(pais.nombre, 1, self)
                tropas_restantes -= 1
                
    def calcular_distancias_objetivo(self, G, paises_objetivo):
        distancias_objetivo = {}
        for pais in self.paises:
            distancias = nx.single_source_dijkstra_path_length(G, pais.nombre, weight='weight')
            distancias_objetivo[pais] = min(distancias[objetivo.nombre] for objetivo in paises_objetivo)
        return distancias_objetivo


    def ordenar_paises_por_proximidad(self, paises_objetivo, tablero):
        G = tablero.construir_grafo_con_peso()
        distancias_objetivo = self.calcular_distancias_objetivo(G, paises_objetivo)
        
        # Ordenar países por proximidad y luego por número de tropas (menos tropas primero)
        return sorted(self.paises, key=lambda pais: (distancias_objetivo[pais], -pais.tropas))

    def reforzar_por_proximidad_objetivo(self, tablero, paises_objetivo):
        paises_por_reforzar = self.ordenar_paises_por_proximidad(paises_objetivo, tablero)
        tropas_disponibles = self.tropas_por_turno

        for pais in paises_por_reforzar:
            for vecino_nombre in pais.vecinos:
                vecino = tablero.paises[vecino_nombre]
                if vecino.jugador != self and pais.tropas <= vecino.tropas:
                    tropas_necesarias = vecino.tropas - pais.tropas + 1
                    tropas_a_asignar = min(tropas_necesarias, tropas_disponibles)
                    tablero.reforzar_pais(pais.nombre, tropas_a_asignar, self)
                    tropas_disponibles -= tropas_a_asignar

                if tropas_disponibles == 0:
                    break

            if tropas_disponibles == 0:
                break

        return tropas_disponibles


    def distribuir_tropas_por_importancia(self, paises_por_reforzar, tropas_disponibles,tablero):
        # Porcentajes de distribución: 30%, 25%, 20%, 15%, 10%...
        # Estos porcentajes se ajustarán según la cantidad de países a reforzar.
        porcentajes = [0.3, 0.25, 0.2, 0.15, 0.1]
        while len(porcentajes) < len(paises_por_reforzar):
            porcentajes.append(porcentajes[-1] * 0.8)
        
        tropas_asignadas = 0
        for pais, porcentaje in zip(paises_por_reforzar, porcentajes):
            tropas_a_asignar = int(tropas_disponibles * porcentaje)
            tablero.reforzar_pais(pais.nombre, tropas_a_asignar, self)
            tropas_asignadas += tropas_a_asignar

        return tropas_disponibles - tropas_asignadas
    
    def reforzar(self, tablero):
        paises_objetivo = self.identificar_paises_objetivo(tablero)

        if hasattr(self.objetivos, 'tercero') and self.objetivos['tercero']:
            tercer_continente = self.identificar_tercer_continente()
            paises_objetivo += [pais for pais in tablero.paises.values() if pais.continente == tercer_continente and pais.jugador != self]

        if not paises_objetivo:
            print("No hay países objetivo para reforzar. Reforzando al azar.")
            pais_a_reforzar = random.choice(self.paises)
            tablero.reforzar_pais(pais_a_reforzar.nombre, self.tropas_por_turno, self)
            return
        
        # Si la misión es conquistar 18 territorios con al menos 2 tropas
        if self.objetivos['territorios'] == 18 and self.objetivos['tropas_minimas'] == 2:
            paises_con_menos_de_dos_tropas = [pais for pais in self.paises if pais.tropas < 2]
            for pais in paises_con_menos_de_dos_tropas:
                tropas_necesarias = 2 - pais.tropas
                if self.tropas_por_turno >= tropas_necesarias:
                    tablero.reforzar_pais(pais.nombre, tropas_necesarias, self)
                    #.tropas_por_turno -= tropas_necesarias

        paises_por_reforzar = self.ordenar_paises_por_proximidad(paises_objetivo, tablero)
        tropas_disponibles = self.tropas_por_turno

        tropas_restantes = self.distribuir_tropas_por_importancia(paises_por_reforzar, tropas_disponibles,tablero)

        if tropas_restantes > 0:
            self.refuerzo_equitativo(tablero, tropas_restantes)


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
        print("fase de ataque grafo optimizado")
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
                    # Solo consideramos el país vecino si es un vecino directo del objetivo
                    if objetivo.nombre in pais_vecino.vecinos:
                        # 4. Seleccionar ataques convenientes
                        if pais_vecino.tropas > objetivo.tropas * 1.2:  # Condición de conveniencia
                            ataques_convenientes.append((pais_vecino, objetivo))

        # 5. Realizar ataques
        for origen, destino in ataques_convenientes:
            # Ataque múltiple
            while origen.tropas > 1 and origen.tropas > destino.tropas * 1.2:
                tablero.batalla(origen, destino,self)
                if destino.jugador == self:  # Si el país objetivo ha sido conquistado, salimos del bucle
                    break


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
        # Identificar los países objetivo según los objetivos
        paises_objetivo = self.identificar_paises_objetivo(tablero)
        
        # Si el jugador tiene el objetivo de un tercer continente
        if hasattr(self.objetivos, 'tercero') and self.objetivos['tercero']:
            continentes = ['América del Norte', 'América del Sur', 'África', 'Asia']
            pais_count_por_continente = {continente: sum(1 for pais in self.paises if pais.continente == continente) for continente in continentes}
            tercer_continente = max(pais_count_por_continente, key=pais_count_por_continente.get)
            paises_tercer_continente = [pais for pais in tablero.paises.values() if pais.continente == tercer_continente and pais.jugador != self]
            paises_objetivo.extend(paises_tercer_continente)  # Añadir países del tercer continente a los objetivos

        # Si después de considerar todos los objetivos no hay países objetivo
        if not paises_objetivo:
            paises_objetivo = self.obtener_paises_frontera(tablero)  # Enfocarse en la frontera

        print(f"Paises objetivo: {[pais.nombre for pais in paises_objetivo]}")
        # Realizar movimientos basados en los países objetivo
        self.realizar_movimiento(tablero, paises_objetivo)


    def obtener_paises_frontera(self, tablero):
        return [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)]

    def realizar_movimiento(self, tablero, paises_objetivo):
        G = tablero.construir_grafo_con_peso()

        # Estrategia de Ataque Directo
        for pais_destino in sorted(paises_objetivo, key=lambda pais: pais.tropas):  # Ordenamos por la cantidad de tropas del objetivo
            paises_vecinos = [tablero.paises[vecino] for vecino in pais_destino.vecinos if tablero.paises[vecino].jugador == self and tablero.paises[vecino].tropas > 1] # Considerando solo vecinos con al menos 2 tropas
            
            if not paises_vecinos:
                continue
            
            pais_origen = max(paises_vecinos, key=lambda pais: pais.tropas_disponibles_para_mover(), default=None)
            
            if pais_origen.tropas_disponibles_para_mover() > pais_destino.tropas + 1:
                tropas_a_mover = min(pais_origen.tropas_disponibles_para_mover() - 1, (pais_origen.tropas_disponibles_para_mover() - pais_destino.tropas) // 2 + 1)

                try:
                    tablero.mover_tropas(pais_origen.nombre, pais_destino.nombre, tropas_a_mover)
                    pais_origen.mover_tropas(tropas_a_mover)
                    print(f"Se movieron {tropas_a_mover} tropas de {pais_origen.nombre} a {pais_destino.nombre}.")
                except ValueError as e:
                    print(f"Error al mover tropas de {pais_origen.nombre} a {pais_destino.nombre}: {e}")

        # Estrategia de Refuerzo
        for pais_destino in self.obtener_paises_frontera(tablero):
            if pais_destino in paises_objetivo:  # Si ya hemos intentado mover tropas a este destino, lo saltamos
                continue
            
            paises_vecinos = [tablero.paises[vecino] for vecino in pais_destino.vecinos if tablero.paises[vecino].jugador == self and tablero.paises[vecino].tropas > 1] # Considerando solo vecinos con al menos 2 tropas
            pais_origen = max(paises_vecinos, key=lambda pais: pais.tropas_disponibles_para_mover(), default=None)
            
            if not pais_origen or pais_origen.tropas_disponibles_para_mover() <= 1:
                continue
            
            tropas_a_mover = (pais_origen.tropas_disponibles_para_mover() - 1) // 2
            try:
                tablero.mover_tropas(pais_origen.nombre, pais_destino.nombre, tropas_a_mover)
                pais_origen.mover_tropas(tropas_a_mover)
                print(f"Se movieron {tropas_a_mover} tropas de {pais_origen.nombre} a {pais_destino.nombre} para reforzar.")
            except ValueError as e:
                print(f"Error al mover tropas de {pais_origen.nombre} a {pais_destino.nombre} para reforzar: {e}")



