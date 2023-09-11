import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Softmax
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Dropout
import os
from keras.callbacks import TensorBoard
tensorboard = TensorBoard(log_dir='./logs_r', histogram_freq=0, write_graph=True, write_images=True)
class ReforzarNN:
    def __init__(self):
        self.model = self.build_model()

    def build_model(self):
        model = Sequential()

        # Capa de entrada y primera capa oculta
        model.add(Dense(128, activation='relu', input_dim=271))
        model.add(Dropout(0.2))
        # Segunda capa oculta
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.2))
        # Capa de salida
        model.add(Dense(42, activation='linear'))
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