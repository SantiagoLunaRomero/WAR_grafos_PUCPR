import os
import random
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from Jugadores.jugadorDNQ.modelos.reforzar_nn import ReforzarNN

# Función para cargar datos y dividirlos en conjuntos de entrenamiento y validación
def cargar_datos(batch_size, dataset_file):
    with open(dataset_file, 'r') as f:
        data_info = f.readlines()

    archivos = [line.split(';')[0].strip() for line in data_info]
    estados_por_archivo = [int(line.split(';')[1].strip()) for line in data_info]
    
    # Dividir archivos en conjuntos de entrenamiento y validación
    archivos_train, archivos_val = train_test_split(archivos, test_size=0.2, random_state=42)

    def _cargar_batch(archivos):
        total_estados_cargados = 0
        states_batch = []
        q_values_batch = []
        indices_archivos = list(range(len(archivos)))
        random.shuffle(indices_archivos)

        for idx in indices_archivos:
            archivo = archivos[idx]
            with open(archivo, 'rb') as f:
                memoria = pickle.load(f)
                states_batch.extend([x[0] for x in memoria])
                q_values_batch.extend([(x[1], x[2], x[3]) for x in memoria])

            total_estados_cargados += estados_por_archivo[idx]

            if total_estados_cargados >= batch_size:
                yield states_batch[:batch_size], q_values_batch[:batch_size]
                states_batch, q_values_batch = states_batch[batch_size:], q_values_batch[batch_size:]
                total_estados_cargados -= batch_size

    return _cargar_batch(archivos_train), _cargar_batch(archivos_val)

# Resto del código sigue siendo el mismo
# Función para preparar datos para entrenar
def preparar_datos_para_entrenar(model, states, q_values):
    q_values_target = model.predict(np.array(states))
    
    # Obtener todos los next_states que no son None
    next_states = [tup[2] for tup in q_values if tup[2] is not None]
    if next_states:
        next_q_values_all = model.predict(np.array(next_states))
    
    idx_next_state = 0
    for i, (action, reward, next_state) in enumerate(q_values):
        reward = reward/1
        if next_state is None:
            q_values_target[i, action] = reward
        else:
            max_next_q_value = np.max(next_q_values_all[idx_next_state])
            q_values_target[i, action] = reward + 0.99 * max_next_q_value
            idx_next_state += 1

    return q_values_target
# Entrenamiento
model = ReforzarNN()

batch_size = 512*100
epochs = 3
data_dir = 'Dataset_refuerzo.txt'

train_data_gen, val_data_gen = cargar_datos(batch_size, data_dir)

for epoch in range(epochs):
    train_data_gen, val_data_gen = cargar_datos(batch_size, data_dir)
    for states_train, q_values_train in train_data_gen:
        q_values_target_train = preparar_datos_para_entrenar(model, states_train, q_values_train)
        print(len(states_train),len(q_values_target_train))
        model.train(np.array(states_train), np.array(q_values_target_train))
    # Evaluación en el conjunto de validación después de cada época
    val_loss_total = 0
    val_steps = 0
    for states_val, q_values_val in val_data_gen:
        q_values_target_val = preparar_datos_para_entrenar(model, states_val, q_values_val)
        loss_val = model.evaluate(np.array(states_val), np.array(q_values_target_val))
        val_loss_total += loss_val
        val_steps += 1
        if val_steps == 0:
            print(f"Epoch {epoch+1}/{epochs}, No validation data available")
        else:
            print(f"Epoch {epoch+1}/{epochs}, Validation Loss: {val_loss_total / val_steps}")

# Guarda el modelo después de entrenarlo
model.save_model('refuerzo_2.h5')
