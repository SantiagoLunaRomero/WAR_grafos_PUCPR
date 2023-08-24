from Tablero import Tablero
from misiones import misiones
from Jugadores.JugadorMisionCompleja import JugadorMisionCompleja
from Jugadores.jugadorRL import AgenteRL
from Jugadores.jugadorRL2 import AgenteRL2
from Jugadores.jugadorAleatorio import JugadorAleatorio
from Jugadores.jugadorGrafo import JugadorGrafo
from Jugadores.jugadorGrafoOptimizado import JugadorGrafoOptimizado
from Jugadores.jugadorDQN_enhanced import FusionAgenteDQN
import random

def crear_jugador(tipo, nombre, color, mision):
    if tipo == "JugadorMisionCompleja":
        return JugadorMisionCompleja(nombre, color, mision)
    elif tipo == "JugadorGrafo":
        return JugadorGrafo(nombre, color, mision) 
    elif tipo == "JuagorRl2":
        return AgenteRL2(nombre, color, mision)
    elif tipo == "aleatorio":
        return JugadorAleatorio(nombre, color, mision)
    elif tipo == "JugadorGrafoOptimizado":
        return JugadorGrafoOptimizado(nombre, color, mision)
    elif tipo == "JuagorRl":
        return AgenteRL(nombre, color, mision)
    elif tipo == "JugadorDQN":
        return FusionAgenteDQN(nombre, color, mision)
    else:
        raise ValueError(f"Tipo de jugador desconocido: {tipo}")

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

recomensa_acumulada = []
epsilon_cada_partida = []

def limpiar_archivo():
    # Contar el número de transiciones en el archivo
    with open("transitions.json", 'r') as file:
        line_count = sum(1 for _ in file)
    print(line_count)
    # Si el número de transiciones excede 2*max_size, truncar el archivo
    if line_count > int(1.1 * 3000):
        with open("transitions.json", 'r') as file:
            lines = file.readlines()
            
        # Conservar solo las últimas transiciones igual a 2*max_size
        with open("transitions.json", 'w') as file:
            file.writelines(lines[-int(1.1*3000):])

#limpiar_archivo()

for i in range(1,500):
    colores_disponibles = ["red", "blue", "green", "yellow", "black", "purple"]
    mision_dqn = misiones[random.randint(0, 12)]
    if i%25==0:
        limpiar_archivo()
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
        ("JugadorDQN", "DQN 1", color5, mision_dqn),
        (*jugador_aleatorio(), color6, misiones[random.randint(0, 12)])
    ]

    jugadores = [crear_jugador(tipo, nombre, color, mision) for (tipo, nombre, color, mision) in jugadores_info]
    jugadores[4].epsilon = jugadores[4].epsilon-0.0001*i
    tablero = Tablero(jugadores)
    tablero.jugar(1000)
    recomensa_acumulada.append(jugadores[4].recompensa_acumulada)
    epsilon_cada_partida.append(jugadores[4].epsilon)

    # Guardamos la información en el archivo después de cada iteración
    with open('datos_juego.txt', 'a') as archivo:  # 'a' indica que se añadirán datos al final del archivo
        archivo.write(f"Recompensa acumulada en la partida {i}: {jugadores[4].recompensa_acumulada}\n")
        archivo.write(f"Epsilon en la partida {i}: {jugadores[4].epsilon}\n\n")
    

print("Recompensa acumulada: ", recomensa_acumulada)
print("Epsilon acumulado: ", epsilon_cada_partida)