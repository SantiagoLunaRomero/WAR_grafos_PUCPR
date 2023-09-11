import os
import pickle

# Ruta a la carpeta que contiene los archivos .pickle
ruta_carpeta = "partidas/reforzar"
archivos = [os.path.join(ruta_carpeta, archivo) for archivo in os.listdir(ruta_carpeta) if archivo.endswith('.pkl')]

# Calcula la longitud de cada archivo
longitudes = {}
for archivo in archivos:
    with open(archivo, 'rb') as f:
        partida = pickle.load(f)
        longitudes[archivo] = len(partida)

# Guarda las longitudes en un archivo de texto
with open('Dataset_refuerzo.txt', 'w') as f:
    for archivo, longitud in longitudes.items():
        f.write(f"{archivo} ; {longitud}\n")
