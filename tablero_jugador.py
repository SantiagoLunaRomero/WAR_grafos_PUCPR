import networkx as nx
#import matplotlib.pyplot as plt
import random
import numpy as np

# importar archivos
from misiones import misiones
from misiones import descripcion_a_indice

class Pais:
    def __init__(self, nombre, continente, vecinos):
        self.nombre = nombre
        self.continente = continente
        self.jugador = None
        self.tropas = 0
        self.tropas_iniciales = 0  # Tropas al inicio del turno
        self.tropas_movidas = 0  # Tropas que se han movido durante el turno
        self.vecinos = vecinos
        self.tropas_recibidas = 0

    def set_tropas_iniciales(self):
        """Establecer el número de tropas al inicio del turno."""
        self.tropas_iniciales = self.tropas

    def tropas_disponibles_para_mover(self):
        """Determinar cuántas tropas están disponibles para mover."""
        return self.tropas_iniciales - self.tropas_movidas

    def mover_tropas(self, cantidad):
        """Mover tropas de este país. Actualiza las tropas movidas."""
        if cantidad > self.tropas_disponibles_para_mover():
            raise ValueError("Intentando mover más tropas de las disponibles.")
        self.tropas_movidas += cantidad

    def iniciar_turno(self):
        """Resetea las tropas movidas y establece las tropas iniciales al inicio de cada turno."""
        self.tropas_movidas = 0
        self.tropas_recibidas = 0 
        self.set_tropas_iniciales()

    def get_nombre(self):
        return self.nombre

    def __str__(self):
        return (f"{self.nombre} - Continente: {self.continente}, Jugador: {self.jugador}, "
                f"Tropas: {self.tropas}, Tropas Iniciales: {self.tropas_iniciales}, Tropas Movidas: {self.tropas_movidas}, Vecinos: {self.vecinos}")

class Tablero:
    def __init__(self, jugadores):
        self.jugadores = jugadores
        self.turno = 0
        self.paises = self.generar_paises()
        #self.asignar_paises_a_jugadores()
        #self.grafo = self.construir_grafo_con_peso()
        self.matriz_historial = []

    def generar_paises(self):
      paises = {
                'Brasil': Pais('Brasil', 'América del Sur', ['Argentina', 'Venezuela', 'Perú']),
                'Argentina': Pais('Argentina', 'América del Sur', ['Perú', 'Brasil']),
                'Venezuela': Pais('Venezuela', 'América del Sur', ['Brasil', 'Perú', 'México']),
                'Perú': Pais('Perú', 'América del Sur', ['Argentina', 'Brasil']),

                'México': Pais('México', 'América del Norte', ['Venezuela', 'Nueva York', 'California']),
                'Nueva York': Pais('Nueva York', 'América del Norte', ['México', 'California', 'Ottawa', 'Labrador']),
                'California': Pais('California', 'América del Norte', ['México', 'Nueva York', 'Ottawa', 'Vancouver']),
                'Ottawa': Pais('Ottawa', 'América del Norte', ['Nueva York', 'California', 'Vancouver', 'Labrador']),
                'Vancouver': Pais('Vancouver', 'América del Norte', ['Mackenzie', 'Alaska', 'Ottawa', 'California']),
                'Mackenzie': Pais('Mackenzie', 'América del Norte', ['Alaska', 'Vancouver', 'Ottawa', 'Groenlandia']),
                'Alaska': Pais('Alaska', 'América del Norte', ['Mackenzie', 'Vancouver', 'Vladivostok']),
                'Labrador': Pais('Labrador', 'América del Norte', ['Ottawa', 'Nueva York', 'Groenlandia']),
                'Groenlandia': Pais('Groenlandia', 'América del Norte', ['Labrador', 'Mackenzie', 'Islandia']),

                'Islandia': Pais('Islandia', 'Europa', ['Groenlandia', 'Inglaterra']),
                'Inglaterra': Pais('Inglaterra', 'Europa', ['Islandia', 'Suecia', 'Francia', 'Alemania']),
                'Suecia': Pais('Suecia', 'Europa', ['Inglaterra', 'Moscú']),
                'Alemania': Pais('Alemania', 'Europa', ['Inglaterra', 'Francia', 'Polonia']),
                'Francia': Pais('Francia', 'Europa', ['Inglaterra', 'Alemania', 'Polonia']),
                'Polonia': Pais('Polonia', 'Europa', ['Alemania', 'Francia', 'Moscú']),
                'Moscú': Pais('Moscú', 'Europa', ['Suecia', 'Polonia', 'Omsk', 'Aral', 'Oriente Medio']),

                'Argelia': Pais('Argelia', 'África', ['Brasil', 'Francia', 'Egipto', 'Sudán', 'Congo']),
                'Egipto': Pais('Egipto', 'África', ['Argelia', 'Francia', 'Polonia', 'Sudán', 'Oriente Medio']),
                'Congo': Pais('Congo', 'África', ['Argelia', 'Sudán', 'Sudáfrica']),
                'Sudán': Pais('Sudán', 'África', ['Argelia', 'Egipto', 'Madagascar', 'Sudáfrica', 'Congo']),
                'Madagascar': Pais('Madagascar', 'África', ['Sudán', 'Sudáfrica']),
                'Sudáfrica': Pais('Sudáfrica', 'África', ['Congo', 'Sudán', 'Madagascar']),

                'Oriente Medio': Pais('Oriente Medio', 'Asia', ['Egipto', 'Moscú', 'Aral', 'India']),
                'Aral': Pais('Aral', 'Asia', ['Moscú', 'Oriente Medio', 'Omsk', 'China', 'India']),
                'Omsk': Pais('Omsk', 'Asia', ['Moscú', 'Dudinka', 'Mongolia', 'China', 'Aral']),
                'Dudinka': Pais('Dudinka', 'Asia', ['Omsk', 'Siberia', 'Chita', 'Mongolia']),
                'Siberia': Pais('Siberia', 'Asia', ['Dudinka', 'Chita', 'Vladivostok']),
                'Chita': Pais('Chita', 'Asia', ['Siberia', 'Dudinka', 'Vladivostok', 'China', 'Mongolia']),
                'Mongolia': Pais('Mongolia', 'Asia', ['Omsk', 'Dudinka', 'Chita', 'China']),
                'Vladivostok': Pais('Vladivostok', 'Asia', ['Siberia', 'Chita', 'Japón', 'Alaska']),
                'China': Pais('China', 'Asia', ['Mongolia', 'Aral', 'India', 'Vietnam', 'Vladivostok', 'Japón']),
                'India': Pais('India', 'Asia', ['China', 'Oriente Medio', 'Aral', 'Vietnam', 'Sumatra']),
                'Japón': Pais('Japón', 'Asia', ['Vladivostok', 'China']),
                'Vietnam': Pais('Vietnam', 'Asia', ['India', 'China', 'Borneo']),

                'Borneo': Pais('Borneo', 'Oceanía', ['Vietnam', 'Nueva Guinea', 'Australia']),
                'Sumatra': Pais('Sumatra', 'Oceanía', ['India', 'Australia']),
                'Nueva Guinea': Pais('Nueva Guinea', 'Oceanía', ['Borneo', 'Australia']),
                'Australia': Pais('Australia', 'Oceanía', ['Sumatra', 'Borneo', 'Nueva Guinea']),
            }
        # La lógica de generación de países se mantiene igual.
      return paises
    


    def asignar_paises_a_jugadores(self):
        # La lógica de asignación de países a jugadores se mantiene igual.
        nombres_paises = list(self.paises.keys())
        random.shuffle(nombres_paises)
        for i, nombre_pais in enumerate(nombres_paises):
            pais = self.paises[nombre_pais]
            jugador = self.jugadores[i % len(self.jugadores)]
            pais.jugador = jugador  # Aquí está la corrección
            jugador.paises.append(pais)
            if pais.tropas <= 0:
               pais.tropas = 1

    def actualizarmatriz(self, matriz):
        nombres_paises = list(self.paises.keys())
        colores = ["blue", "red", "green", "purple", "yellow", "black"]

        for i in range(len(matriz)):
            jugador_color = colores[i]
            jugador = next((jug for jug in self.jugadores if jug.color == jugador_color), None)

            if jugador is None:
                continue  # Salta si no hay jugador con el color actual
            jugador.paises = []
            for j in range(len(matriz[i])):
                if j < len(nombres_paises):
                    cantidad_tropas = matriz[i][j]
                    if cantidad_tropas > 0:
                        pais = self.paises[nombres_paises[j]]
                        pais.jugador = jugador
                        if pais not in jugador.paises:
                            jugador.paises.append(pais)
                        pais.tropas = cantidad_tropas
        
        self.construir_grafo_con_peso()
        #self.actualizar_grafo()

    def reforzar_pais(self, pais_nombre, tropas, jugador):
        """
        Refuerza un país específico con un número dado de tropas.
        Asegura que el jugador no asigne más tropas de las disponibles.
        """

        # Check if the country belongs to the player
        if self.paises[pais_nombre].jugador != jugador:
            return False, "El país no pertenece al jugador."
        
        # Check if the player has enough troops to assign
        if tropas > jugador.tropas_por_turno:
            return False, "No tienes suficientes tropas para asignar."

        # Assign tropas
        self.paises[pais_nombre].tropas += tropas
        jugador.tropas_por_turno -= tropas

        return True, f"{tropas} tropas asignadas a {pais_nombre}."

    def lanzar_dados(self, num_dados):
        return sorted([random.randint(1, 6) for _ in range(num_dados)], reverse=True)

    def batalla(self, pais_origen, pais_destino,jugador):
        if pais_origen not in jugador.paises:
            return False, f"No puedes atacar desde {pais_origen.nombre} porque no le pertece al jugador : {jugador.nombre}"
        if pais_destino in jugador.paises:
            return False, f"No puedes atacar desde {pais_destino.nombre} porque le pertece al jugador : {jugador.nombre}"
        
        # Verificar si los dos países son vecinos
        if pais_destino.nombre not in pais_origen.vecinos:
            return False, f"No puedes atacar a {pais_destino.nombre} desde {pais_origen.nombre} porque no son vecinos."

        dados_atacante = self.lanzar_dados(min(3, pais_origen.tropas - 1))
        dados_defensor = self.lanzar_dados(min(3, pais_destino.tropas))

        # Ordenar los dados
        dados_atacante.sort(reverse=True)
        dados_defensor.sort(reverse=True)

        resultado = []
        resultado.append(f"{pais_origen.jugador.nombre} lanza {dados_atacante}")
        resultado.append(f"{pais_destino.jugador.nombre} lanza {dados_defensor}")

        for dado_atacante, dado_defensor in zip(dados_atacante, dados_defensor):
            if dado_atacante > dado_defensor:
                pais_destino.tropas -= 1
                resultado.append(f"{pais_destino.jugador.nombre} pierde una tropa en {pais_destino.nombre}")
            else:
                pais_origen.tropas -= 1
                resultado.append(f"{pais_origen.jugador.nombre} pierde una tropa en {pais_origen.nombre}")

        if pais_destino.tropas == 0:
            pais_destino.jugador.paises.remove(pais_destino)
            pais_destino.jugador = pais_origen.jugador
            pais_destino.jugador.paises.append(pais_destino)
            pais_destino.tropas = 1
            pais_origen.tropas -= 1
            pais_origen.jugador.ganar_tropas_temporales(3)
            resultado.append(f"{pais_origen.jugador.nombre} ha conquistado {pais_destino.nombre}")

        if pais_origen.tropas < 0:
            return False, f"El país {pais_origen.nombre} tiene un número negativo de tropas: {pais_origen.tropas}"

        if pais_destino.tropas < 0:
            return False, f"El país {pais_destino.nombre} tiene un número negativo de tropas: {pais_destino.tropas}"

        return True, "\n".join(resultado)

######################################################## mover tropas.
    def reset_tropas_recibidas(self):
        for pais in self.paises.values():
            pais.tropas_recibidas = 0
    
    def mover_tropas(self, nombre_pais_origen, nombre_pais_destino, numero_tropas):
        # Para mover tropas, ambos países deben ser propiedad del mismo jugador y deben ser vecinos.
        pais_origen = self.paises[nombre_pais_origen]
        pais_destino = self.paises[nombre_pais_destino]
        
        # Verificar si hay suficientes tropas en el país de origen para mover
        if pais_origen.tropas <= 1:
            #print(f"{nombre_pais_origen} no tiene suficientes tropas para mover.")
            raise ValueError(f"{nombre_pais_origen} no tiene suficientes tropas para mover.")
        
        # Verificar que los dos países son vecinos
        if nombre_pais_destino not in pais_origen.vecinos:
            raise ValueError(f"No puedes mover tropas a {nombre_pais_destino} desde {nombre_pais_origen} porque no son vecinos.")
        
        # Verificar que ambos países son del mismo jugador
        if pais_origen.jugador != pais_destino.jugador:
            raise ValueError("Solo puedes mover tropas entre tus propios territorios.")
        
        # Verificar que no estás intentando mover más tropas de las disponibles
        tropas_disponibles = pais_origen.tropas_disponibles_para_mover()
        if numero_tropas > tropas_disponibles:
            raise ValueError(f"Solo puedes mover {tropas_disponibles} tropas de {nombre_pais_origen}.")
        
        # En el método mover_tropas, antes de mover las tropas, vamos a agregar:
        if numero_tropas > (pais_origen.tropas - pais_origen.tropas_recibidas):
            raise ValueError(f"No puedes mover las tropas que {nombre_pais_origen} recién recibió en este turno.")
        
        if numero_tropas >= pais_origen.tropas:
            raise ValueError(f"No puedes mover todas las tropas de {nombre_pais_origen}. Debes dejar al menos una tropa atrás.")
        
        
        # Ahora, realizar el movimiento de tropas
        pais_origen.mover_tropas(numero_tropas)  # Actualizar las tropas movidas en el país de origen
        pais_origen.tropas -= numero_tropas
        pais_destino.tropas += numero_tropas
        pais_destino.tropas_recibidas += numero_tropas  # <-- Añadimos las tropas recibidas
        #print("Aqui.:")
        #print(f"Se movieron {numero_tropas} tropas de {nombre_pais_origen} a {nombre_pais_destino}.")


    # Primero, debemos agregar una verificación para garantizar que todas las tropas sean un número positivo.
    # Si encontramos un país con un número negativo de tropas, lanzaremos un error.

    def verificar_tropas(tablero):
        for pais in tablero.paises.values():
            if pais.tropas < 0:
                raise ValueError(f"El país {pais.nombre} tiene un número negativo de tropas: {pais.tropas}")

    # Luego, usamos esta función en la construcción del grafo.



    def siguiente_turno(self):
        self.turno = (self.turno + 1) % len(self.jugadores)

    def verificar_ganador(self):
        # Si todos los países son propiedad de un mismo jugador, ese jugador ha ganado.
        propietario_pais_inicial = list(self.paises.values())[0].propietario
        for pais in self.paises.values():
            if pais.propietario != propietario_pais_inicial:
                return False
        return True

    def jugar(self, numero_turnos):
      jugadores_activos = [jugador for jugador in self.jugadores if jugador.paises]

      for i in range(numero_turnos):
          print("..............TURNO............ : ",i)
          jugador = jugadores_activos[self.turno % len(jugadores_activos)]

          # Si un jugador no tiene países, se elimina del juego
          if not jugador.paises:
              #jugador.informar_perdida(self,recompensa = -100)
              jugadores_activos.remove(jugador)
              if not jugadores_activos:
                  print("Todos los jugadores han sido eliminados. ¡El juego ha terminado!")
                  return
              continue

          jugador.tropas_por_turno = 3
          if i > 800:
            jugador.ganar_tropas_temporales(2)
          elif i > 400:
            jugador.ganar_tropas_temporales(1)
          jugador.actualizar_tropas_por_turno()
          jugador.iniciar_turno()
          # El jugador realiza sus acciones
          print("_______Fase de refuerzo________")
          jugador.reforzar(self)
          if i > 6:  # A partir del turno 7 se permite atacar y mover tropas
             print("_______Fase de ataque________")
             jugador.atacar(self)
             print("_______Fase de movimiento________")
             jugador.mover_tropas(self)
             self.reset_tropas_recibidas()

          # Verificamos si algún jugador ha completado su misión
          if jugador.mision.esta_completa(jugador, self):
            print(f"{jugador.nombre} ha completado su misión y es el ganador!")
            for j in self.jugadores:
                if j != jugador:  # Informar a todos excepto al ganador
                    j.informar_perdida(self,recompensa = -10)
                else:  # Informar al ganador
                    j.informar_victoria(self)
            return

          self.siguiente_turno()

      for jugador in self.jugadores:
          jugador.informar_perdida(self,recompensa = -5)
      print("Ningún jugador ha completado su misión.")

    def construir_grafo_con_peso(self):
        self.verificar_tropas()
        G = nx.Graph()
        for nombre_pais, pais in self.paises.items():
            G.add_node(nombre_pais, tropas=pais.tropas, jugador=pais.jugador.nombre)
            for vecino in pais.vecinos:
                peso = self.paises[vecino].tropas
                G.add_edge(nombre_pais, vecino, weight=peso)
        return G
    
    def matriz_de_adyacencia(self, orden_nodos=None):
        return nx.adjacency_matrix(self.grafo, nodelist=self.paises.keys()).todense()
    
    def calcular_pesos(self, jugador, paises_a_reforzar):
        G = self.construir_grafo_con_peso()
        pesos = {}
        for pais in paises_a_reforzar:
            distancias = nx.single_source_dijkstra_path_length(G, pais.nombre, weight='weight')
            peso_total = sum(distancias.values())
            pesos[pais] = peso_total  # aquí estamos usando el objeto pais en lugar de su nombre
        return pesos

    def actualizar_grafo(self):
      for nombre_pais, pais in self.paises.items():
          self.grafo.nodes[nombre_pais]['tropas'] = pais.tropas
          self.grafo.nodes[nombre_pais]['jugador'] = pais.jugador.nombre
          for vecino in pais.vecinos:
              self.grafo.edges[nombre_pais, vecino]['weight'] = self.paises[vecino].tropas


    def crear_matriz_estado(self):
        self.actualizar_grafo()
        # Definir el mapeo de colores a índices
        colores_mapa = {'red': 0, 'blue': 1, 'green': 2, 'yellow': 3, 'black': 4, 'purple': 5}

        # Inicializar la matriz con ceros (6 jugadores, número de países)
        matriz_estado = np.zeros((6, len(self.paises)))

        # Llenar la matriz con la información de las tropas de los jugadores en los países
        for color, i in colores_mapa.items():
            jugador = next((jug for jug in self.jugadores if jug.color == color), None)
            
            # Si no hay jugador con el color actual, continuar con el siguiente color
            if jugador is None:
                continue

            # Solo agregar las tropas si el país pertenece al jugador
            if jugador.paises:
                for j, nombre_pais in enumerate(self.paises):
                    if self.grafo.nodes[nombre_pais]['jugador'] == jugador.nombre:
                        matriz_estado[i, j] = self.grafo.nodes[nombre_pais]['tropas']

        # Guardar la matriz en el historial
        #self.matriz_historial.append(matriz_estado)
        return matriz_estado

    def dibujar_grafo(self):
      colores = [self.paises[nodo].jugador.color for nodo in self.grafo.nodes]

      pos = nx.spring_layout(self.grafo)  # Esto es para definir la posición de los nodos. Puedes usar otros layouts.

      nx.draw(self.grafo, pos, node_color=colores, with_labels=True)
      #plt.show()

    def get_matriz_historial(self):
        return self.matriz_historial

    def mostrar_tablero(self):
            for pais in self.paises.values():
                print(f"Nombre del país: {pais.nombre}")
                print(f"Continente: {pais.continente}")
                print(f"Propietario: {pais.jugador.nombre}")
                print(f"Tropas: {pais.tropas}")
                print(f"Vecinos: {pais.vecinos}")
                print("-----")