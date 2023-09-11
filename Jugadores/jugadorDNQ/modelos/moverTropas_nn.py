import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Softmax, Reshape, Concatenate, Input
from tensorflow.keras.models import Model
from keras.callbacks import TensorBoard
from tensorflow.keras.optimizers import Adam
import os
tensorboard = TensorBoard(log_dir='./logs_m', histogram_freq=0, write_graph=True, write_images=True)

class MoverTropasNN:
    def __init__(self, input_dim=271, num_paises=42):
        self.model = self.build_model(input_dim, num_paises)

    def build_model(self, input_dim, num_paises):
        # Entrada
        input_layer = Input(shape=(input_dim,))
        
        # Capas ocultas
        x = Dense(128, activation='relu')(input_layer)
        x = Dense(64, activation='relu')(x)
        
        # Dividimos la última capa en dos partes: una para el país de origen y otra para el país destino
        pais_origen = Dense(num_paises, activation='linear')(x)
        pais_destino = Dense(num_paises, activation='linear')(x)
        
        # Combinamos las dos salidas en un único modelo
        output = Concatenate(axis=1)([pais_origen, pais_destino])
        
        model = Model(inputs=input_layer, outputs=output)
        optimizer = Adam(learning_rate= 0.001)
        # Compilar el modelo
        model.compile(optimizer=optimizer, loss='mean_squared_error', metrics=['accuracy'])

        return model

    def predict(self, state):
        return self.model.predict(state)

    def train(self, states, q_values_target):
        self.model.fit(states, q_values_target, verbose=0,callbacks=[tensorboard])

    def train_on_batch(self, states, q_values_target):
        loss, _ = self.model.train_on_batch(states, q_values_target)
        return loss
        
    def evaluate(self, states, q_values_target):
        loss, _ = self.model.evaluate(states, q_values_target, verbose=0,callbacks=[tensorboard])
        return loss
    
    def set_weights(self, weights):
        self.model.set_weights(weights)

    def get_weights(self):
        return self.model.get_weights()
    
    def save_model(self, file_name):
        self.model.save(file_name)
        
    def load_model(self, file_name):
        if os.path.exists(file_name):
            self.model = tf.keras.models.load_model(file_name)





