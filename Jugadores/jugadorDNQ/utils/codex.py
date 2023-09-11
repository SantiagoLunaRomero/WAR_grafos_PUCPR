from misiones import misiones
import numpy as np
def estado_a_vector(jugador, tablero):
    # Obtener la matriz de estado aplanada
    matriz_estado = tablero.crear_matriz_estado().flatten()
    
    # Codificar el color del jugador en formato one-hot
    colores_mapa = {'red': 0, 'blue': 1, 'green': 2, 'yellow': 3, 'black': 4, 'purple': 5}
    color_vector = np.zeros(6)
    color_vector[colores_mapa[jugador.color]] = 1
    
    # Codificar la misión del jugador en formato one-hot
    descripcion_a_indice = {mision.descripcion: i for i, mision in enumerate(misiones)}
    mision_vector = np.zeros(len(misiones))
    mision_vector[descripcion_a_indice[jugador.mision.descripcion]] = 1
    
    # Concatenar todos los vectores
    return np.concatenate([matriz_estado, color_vector, mision_vector])


