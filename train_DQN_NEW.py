from Tablero2 import Tablero
from misiones import misiones
from Jugadores.JugadorMisionCompleja import JugadorMisionCompleja
from Jugadores.jugadorAleatorio import JugadorAleatorio
from Jugadores.jugadorDNQ.agentes.agente_dnq import JugadorDQN
from Jugadores.jugadorGrafo import JugadorGrafo
from Jugadores.jugadorGrafoOptimizado import JugadorGrafoOptimizado
import random
def crear_jugador(tipo, nombre, color, mision):
    if tipo == "JugadorMisionCompleja":
        return JugadorMisionCompleja(nombre, color, mision)
    elif tipo == "JugadorGrafo":
        return JugadorGrafo(nombre, color, mision) 
    elif tipo == "DNQ":
        return JugadorDQN(nombre, color, mision)
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
    ("DNQ", "DQN 1", "yellow", misiones[3]),
    ("aleatorio", "aleatori 4", "black", misiones[4]),
    ("aleatorio", "aleatorio 5", "purple", misiones[5]),
]
COLORES = ["red", "blue", "green", "yellow", "black", "purple"]

def jugador_aleatorio(excepto=None):
    tipos_jugadores = [
        "JugadorMisionCompleja", "JugadorGrafo", "JugadorGrafoOptimizado",
        "aleatorio"]
    if excepto:
        tipos_jugadores.remove(excepto)
    tipo = random.choice(tipos_jugadores)
    nombre = tipo + " " + str(random.randint(1, 10))  # Generamos un número aleatorio para el nombre
    return (tipo, nombre)

epsilon = 0.6
epsilon_inicial = 0.6 
for i in range(1,500):
    colores_disponibles = ["red", "blue", "green", "yellow", "black", "purple"]
    mision_dqn = misiones[random.randint(0, 12)]

    # Asignación de colores
    color1 = random.choice(colores_disponibles)
    colores_disponibles.remove(color1)
    color2 = random.choice(colores_disponibles)
    colores_disponibles.remove(color2)
    color3 = random.choice(colores_disponibles)
    colores_disponibles.remove(color3)
    color4 = random.choice(colores_disponibles)
    colores_disponibles.remove(color4)
    color5 = random.choice(colores_disponibles)
    colores_disponibles.remove(color5)
    color6 = random.choice(colores_disponibles)
    colores_disponibles.remove(color6)

    jugadores_info = [
        (*jugador_aleatorio(), color1, misiones[random.randint(0, 12)]),
        (*jugador_aleatorio(), color2, misiones[random.randint(0, 12)]),
        (*jugador_aleatorio(), color3, misiones[random.randint(0, 12)]),
        (*jugador_aleatorio(), color4, misiones[random.randint(0, 12)]),
        ("DNQ", "DQN 1", color5, mision_dqn),
        (*jugador_aleatorio(), color6, misiones[random.randint(0, 12)])
    ]

    jugadores = [crear_jugador(tipo, nombre, color, mision) for (tipo, nombre, color, mision) in jugadores_info]
    
    jugadores[4].epsilon_r = epsilon 
    jugadores[4].epsilon_a = epsilon
    jugadores[4].epsilon_m = epsilon
    tablero = Tablero(jugadores)
    tablero.jugar(1000)
    epsilon = epsilon_inicial-0.001*i

#for i in range(5):
 #   jugadores = [crear_jugador(tipo, nombre, color, mision) for (tipo, nombre, color, mision) in jugadores_info]
    #jugadores[3].epsilon_a = 0.0001
    #jugadores[3].epsilon_r = 0.0001
  #  tablero = Tablero(jugadores)
   # tablero.jugar(1000)
