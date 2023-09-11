from Tablero import Tablero
from misiones import misiones
from Jugadores.JugadorMisionCompleja import JugadorMisionCompleja
from Jugadores.jugadorRL import AgenteRL
from Jugadores.jugadorAleatorio import JugadorAleatorio
from Jugadores.jugadorGrafo import JugadorGrafo
from Jugadores.jugadorGrafoOptimizado import JugadorGrafoOptimizado

def crear_jugador(tipo, nombre, color, mision):
    if tipo == "JugadorMisionCompleja":
        return JugadorMisionCompleja(nombre, color, mision)
    elif tipo == "JugadorGrafo":
        return JugadorGrafo(nombre, color, mision) 
    elif tipo == "aleatorio":
        return JugadorAleatorio(nombre, color, mision)
    elif tipo == "JugadorGrafoOptimizado":
        return JugadorGrafoOptimizado(nombre, color, mision)
    elif tipo == "JuagorRl":
        return AgenteRL(nombre, color, mision)
    else:
        raise ValueError(f"Tipo de jugador desconocido: {tipo}")

jugadores_info = [
    ("JugadorMisionCompleja", "Complejo 1", "red", misiones[0]),
    ("JugadorGrafo", "grafo 1", "blue", misiones[1]),
    ("JugadorGrafoOptimizado", "Optimizado 1", "green",misiones[2]),
    ("aleatorio", "aleatorio 1", "yellow", misiones[3]),
    ("JuagorRl", "agenteRL 2", "black", misiones[4]),
    ("JugadorGrafo", "grafo 2", "purple", misiones[5]),
]

jugadores = [crear_jugador(tipo, nombre, color, mision) for (tipo, nombre, color, mision) in jugadores_info]

tablero = Tablero(jugadores)
tablero.jugar(100)