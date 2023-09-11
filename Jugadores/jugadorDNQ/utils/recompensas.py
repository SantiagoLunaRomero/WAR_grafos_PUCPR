import random
# ----------------- Recompensas Tácticas ----------------------

def recompensa_reforzar_fronteras(tablero, jugador, pais_reforzado):
    """Calcula la recompensa por reforzar fronteras."""
    recompensa = 0
    for vecino_nombre in pais_reforzado.vecinos:
        vecino = tablero.paises[vecino_nombre]
        if vecino.jugador != jugador:
            diferencia_tropas = pais_reforzado.tropas - vecino.tropas
            recompensa += 1 / (1 + abs(diferencia_tropas))
    return recompensa

def recompensa_atacar_paises(tablero, jugador, pais_origen, pais_destino, exito_ataque):
    """Calcula la recompensa por atacar países."""
    if not exito_ataque:
        return -1  # Penalización por ataque fallido

    diferencia_tropas = pais_origen.tropas - pais_destino.tropas
    return (jugador.tropas_temporales/2)+( 1 / (1 + abs(diferencia_tropas)))

def recompensa_mover_tropas(tablero, jugador, pais_origen, pais_destino):
    """Calcula la recompensa por mover tropas."""
    recompensa = 0
    for vecino_nombre in pais_destino.vecinos:
        vecino = tablero.paises[vecino_nombre]
        if vecino.jugador != jugador:
            diferencia_tropas = pais_destino.tropas - vecino.tropas
            recompensa += 1 / (1 + abs(diferencia_tropas))
    return recompensa

# ----------------- Recompensas por Misiones ----------------------

def recompensa_por_conquista_continente(tablero, jugador, continente):
    paises_en_continente = [pais for pais in tablero.paises.values() if pais.continente == continente]
    paises_conquistados = [pais for pais in paises_en_continente if pais.jugador == jugador]
    return 10 * len(paises_conquistados) / len(paises_en_continente)

def recompensa_por_conquista_territorios(tablero, jugador, objetivo):
    territorios_conquistados = len([pais for pais in tablero.paises.values() if pais.jugador == jugador])
    return max(10 * territorios_conquistados / objetivo,10)

def recompensa_por_destruir_color(tablero, jugador, color):
    territorios_iniciales = len(tablero.paises)
    territorios_actuales = len([pais for pais in tablero.paises.values() if pais.jugador.color == color])
    return 10 * (territorios_iniciales - territorios_actuales) / territorios_iniciales

def recompensa_por_mision_europa_oceania_tercero(tablero, jugador):
    recompensa_europa = recompensa_por_conquista_continente(tablero, jugador, 'Europa')
    recompensa_oceania = recompensa_por_conquista_continente(tablero, jugador, 'Oceanía')

    # Lista de todos los continentes excepto Europa y Oceanía
    otros_continentes = ['Asia', 'América del Sur', 'África', 'América del Norte']
    recompensas_otros = [recompensa_por_conquista_continente(tablero, jugador, continente) for continente in otros_continentes]

    # Tomamos la recompensa máxima de los demás continentes
    max_recompensa_otro_continente = max(recompensas_otros)

    return (recompensa_europa + recompensa_oceania + max_recompensa_otro_continente) / 3

def calcular_recompensa_mision(tablero, jugador, descripcion):
    # Misiones cuando es "Conquistar na totalidade a Europa, a Oceanía e mais um terceiro"
    if "Conquistar na totalidade a Europa, a Oceanía e mais um terceiro" in descripcion:
        return recompensa_por_mision_europa_oceania_tercero(tablero, jugador)

    # Misiones de conquista de continentes
    elif any(cont in descripcion for cont in ['Europa', 'Oceanía', 'Asia', 'América del Sur', 'África', 'América del Norte']):
        continentes_mencionados = [cont for cont in ['Europa', 'Oceanía', 'Asia', 'América del Sur', 'África', 'América del Norte'] if cont in descripcion]
        return sum([recompensa_por_conquista_continente(tablero, jugador, cont) for cont in continentes_mencionados])

    # Misiones de conquista de número específico de territorios
    elif "TERRITÓRIOS" in descripcion:
        objetivo = 18 if "18 TERRITÓRIOS" in descripcion else 24
        return recompensa_por_conquista_territorios(tablero, jugador, objetivo)

    # Misiones de destruir ejércitos de un color específico
    elif "Destruir totalmente OS EXÉRCITOS" in descripcion:
        color = descripcion.split()[-1]
        return recompensa_por_destruir_color(tablero, jugador, color)

    return 0  # En caso de que no se cumpla ninguna de las condiciones anteriores

# ----------------- Recompensas Totales ----------------------

def recompensa_total_reforzar(tablero, jugador, pais_reforzado,exito_refuerzo):

    if not exito_refuerzo:
        return -3
    if pais_reforzado is None:
        return -1  # o cualquier valor que considere apropiado para esta situación
    
    recompensa_tactica = recompensa_reforzar_fronteras(tablero, jugador, pais_reforzado)
    recompensa_mision = calcular_recompensa_mision(tablero, jugador,jugador.get_mision())  # Asume que tienes una función que calcula la recompensa de misión
    return recompensa_tactica + recompensa_mision

def recompensa_total_atacar(tablero, jugador, pais_origen, pais_destino, exito_ataque):
    if not exito_ataque:
        return -3
    if pais_origen is None or pais_destino is None:
        return -1  # o cualquier valor que considere apropiado para esta situación
    
    recompensa_tactica = recompensa_atacar_paises(tablero, jugador, pais_origen, pais_destino, exito_ataque)
    recompensa_mision = calcular_recompensa_mision(tablero, jugador,jugador.get_mision())
    return recompensa_tactica + recompensa_mision

def recompensa_total_mover_tropas(tablero, jugador, pais_origen, pais_destino, exito_movimiento):
    if not exito_movimiento:
        return -3
    if pais_origen is None or pais_destino is None:
        return -1  # o cualquier valor que considere apropiado para esta situación
    
    recompensa_tactica = recompensa_mover_tropas(tablero, jugador, pais_origen, pais_destino)
    recompensa_mision = calcular_recompensa_mision(tablero, jugador,jugador.get_mision())
    return recompensa_tactica + recompensa_mision