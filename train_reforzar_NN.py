import pickle
from Jugadores.jugadorDNQ.modelos.reforzar_nn import ReforzarNN
import numpy as np
import random
from sklearn.model_selection import train_test_split

# Cargar memoria
with open('memory.pkl', 'rb') as f:
    memory = pickle.load(f)

# Dividir la memoria en conjuntos de entrenamiento y validación
train_memory, val_memory = train_test_split(memory, test_size=0.2)

# Cargar modelo
model = ReforzarNN()
#model.load_model('reforzamiento_model.h5')

def get_batch(memory, batch_size):
    if len(memory) < batch_size:
        return random.sample(memory, len(memory))
    else:
        return random.sample(memory, batch_size)

# Entrenamiento
epochs = 200
batch_size = 128
for epoch in range(epochs):
    batch = get_batch(train_memory, batch_size)
    
    states = np.array([experience[0] for experience in batch])
    q_values = model.predict(states)

    for i, (state, action, reward, next_state) in enumerate(batch):
        if next_state is None:
            q_values[i, action] = reward
        else:
            next_q_values = model.predict(next_state.reshape(1, -1))
            max_next_q_value = np.max(next_q_values)
            q_values[i, action] = reward + 0.99 * max_next_q_value

    model.train_on_batch(states, q_values)

    # Evaluación en el conjunto de validación después de cada época
    val_batch = get_batch(val_memory, batch_size)
    val_states = np.array([experience[0] for experience in val_batch])
    val_q_values = model.predict(val_states)

    for i, (state, action, reward, next_state) in enumerate(val_batch):
        if next_state is None:
            val_q_values[i, action] = reward
        else:
            next_q_values = model.predict(next_state.reshape(1, -1))
            max_next_q_value = np.max(next_q_values)
            val_q_values[i, action] = reward + 0.99 * max_next_q_value

    val_loss = model.evaluate(val_states, val_q_values)
    print(f"Epoch {epoch+1}/{epochs}, Validation Loss: {val_loss}")

# Guardar modelo actualizado
model.save_model('reforzamiento_model_updated2.h5')
