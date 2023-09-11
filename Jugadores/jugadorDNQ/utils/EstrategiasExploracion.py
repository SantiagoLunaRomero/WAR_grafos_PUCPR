import random

class EstrategiasExploracion:

    @staticmethod
    def reforzar(jugador, tablero):
        # Elegir un país al azar de los que el jugador controla
        pais_elegido = random.choice(jugador.paises)
        
        # Reforzar el país elegido con una tropa
        exito_refuerzo=tablero.reforzar_pais(pais_elegido.nombre, 1, jugador)
        
        return pais_elegido,exito_refuerzo

    @staticmethod
    def atacar(jugador, tablero):
        paises_a_atacar = [vecino for pais in jugador.paises for vecino in pais.vecinos if tablero.paises[vecino].jugador != jugador]

        # Si no hay países a atacar, termina el turno de ataque
        if not paises_a_atacar:
            return None, None, False

        pais_objetivo_nombre = random.choice(paises_a_atacar)
        pais_objetivo = tablero.paises[pais_objetivo_nombre]

        # Selecciona un país de origen para el ataque que tenga suficientes tropas y sea vecino del objetivo
        paises_origen_posibles = [pais for pais in jugador.paises if pais.tropas > 2 and pais_objetivo_nombre in pais.vecinos]

        # Si no hay países de origen posibles, termina el turno de ataque
        if not paises_origen_posibles:
            return None, None, False

        pais_origen = random.choice(paises_origen_posibles)

        # Registra el número de tropas en el país objetivo antes de la batalla
        tropas_objetivo_previas = pais_objetivo.tropas

        # Ataca el país objetivo
        exito_ataque = tablero.batalla(pais_origen, pais_objetivo,jugador)
        exito_ataque = exito_ataque[0]
        # Verifica si el ataque fue exitoso (conquista o reducción de tropas)
        #exito_ataque = tablero.paises[pais_objetivo_nombre].jugador == jugador or pais_objetivo.tropas < tropas_objetivo_previas

        return pais_origen, pais_objetivo, exito_ataque

    @staticmethod
    def mover_tropas(jugador, tablero):
        # Selecciona un país origen al azar que tenga más de 1 tropa
        paises_origen_posibles = [pais for pais in jugador.paises if pais.tropas > 1]

        # Si no hay países de origen posibles, retorna None
        if not paises_origen_posibles:
            return None, None, False

        pais_origen = random.choice(paises_origen_posibles)

        # Selecciona un país destino al azar que sea vecino del país origen
        paises_destino_posibles = [tablero.paises[vecino] for vecino in pais_origen.vecinos if tablero.paises[vecino].jugador == jugador]

        if not paises_destino_posibles:
            return None, None, False

        pais_destino = random.choice(paises_destino_posibles)

        # Intenta mover una tropa
        try:
            tablero.mover_tropas(pais_origen.nombre, pais_destino.nombre, 1)  # Mueve solamente una tropa
            return pais_origen, pais_destino, True
        except ValueError as e:
            print(f"Error al mover tropas: {e}")
            return pais_origen, pais_destino, False

