from Jugadores.jugador import Jugador
import random

class JugadorAleatorio(Jugador):
    def __init__(self, nombre, color, mision):
        super().__init__(nombre, color, mision)

    def reforzar(self, tablero):
        # Selecciona un país al azar
        pais_a_reforzar = random.choice(self.paises)
        
        # Utiliza la función reforzar_pais del tablero
        success, message = tablero.reforzar_pais(pais_a_reforzar.nombre, self.tropas_por_turno, self)
        
        # Si quieres, puedes imprimir el mensaje para saber qué sucedió
        # print(message)


    def atacar(self, tablero):
        print("fase de ataque Aleatorio")
        while True:
            # Lista de países que el jugador aleatorio puede atacar (los vecinos de sus países que no le pertenecen)
            paises_a_atacar = [vecino for pais in self.paises for vecino in pais.vecinos if tablero.paises[vecino].jugador != self]

            # Si no hay países a atacar, termina el turno de ataque
            if not paises_a_atacar:
                return

            pais_objetivo_nombre = random.choice(paises_a_atacar)
            pais_objetivo = tablero.paises[pais_objetivo_nombre]

            # Selecciona un país de origen para el ataque que tenga suficientes tropas y sea vecino del objetivo
            paises_origen_posibles = [pais for pais in self.paises if pais.tropas > 2 and pais_objetivo_nombre in pais.vecinos]

            # Si no hay países de origen posibles, termina el turno de ataque
            if not paises_origen_posibles:
                return

            pais_origen = random.choice(paises_origen_posibles)

            # Ataca el país objetivo
            tablero.batalla(pais_origen, pais_objetivo,self)


    def mover_tropas(self, tablero):
        # Selecciona un país origen al azar que tenga más de 1 tropa
        paises_origen_posibles = [pais for pais in self.paises if pais.tropas > 1]

        # Si no hay países de origen posibles, no hace nada
        if not paises_origen_posibles:
            return

        pais_origen = random.choice(paises_origen_posibles)

        # Selecciona un país destino al azar que sea vecino del país origen
        paises_destino_posibles = [tablero.paises[vecino] for vecino in pais_origen.vecinos if tablero.paises[vecino].jugador == self]

        if not paises_destino_posibles:
            return

        pais_destino = random.choice(paises_destino_posibles)
        tropas_a_mover = random.randint(1, pais_origen.tropas - 1)

        # Utiliza la función mover_tropas del tablero
        try:
            tablero.mover_tropas(pais_origen.nombre, pais_destino.nombre, tropas_a_mover)
        except ValueError as e:
            print(f"Error al mover tropas: {e}")
