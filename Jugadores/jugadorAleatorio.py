from Jugadores.jugador import Jugador
import random

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