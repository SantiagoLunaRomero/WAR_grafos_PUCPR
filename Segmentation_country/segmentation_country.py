from tensorflow.keras.models import load_model
import cv2
import numpy as np
import matplotlib.pyplot as plt

def predict_masks(model_path, img_path):
    # Cargar el modelo
    model = load_model(model_path, compile=False)
    
    # Leer y procesar la imagen
    img = cv2.imread(img_path)
    input_shape = (320, 608, 3)
    img_resized = cv2.resize(img, (input_shape[1], input_shape[0]))/ 255
    img_preprocessed = np.array([img_resized])
    
    # Obtener la predicción del modelo
    prediction = model.predict(img_preprocessed)
    predicted_mask = prediction[0]

    umbral = 0.4  # Establece el valor de umbral que deseas
    # Aplica el umbral a la matriz de predicción
    predicted_mask = (predicted_mask >= umbral).astype(np.uint8)

    # Nombres de los países en orden
    countries_order = [
        "alaska", "mackenzie", "groenladia", "vancouver", "ottawa", "labrador",
        "california", "nova york", "mexico", "venezuela", "peru", "brasil", 
        "argentina", "islandia", "inglaterra", "francia", "alemania", "suecia",
        "polonia", "moscou", "omsk", "dudinka", "siberia", "vladvostok", 
        "argelia", "egipto", "orientemedio", "aral", "Tchita", "congo", "sudan",
        "india", "china", "mongolia", "africa del sur", "madagascar", "vietnan",
        "japon", "sumatra", "borneo", "neuva guinea", "australia"
    ]
    
    # Crear un diccionario para almacenar las máscaras predichas
    masks_dict = {}
    for idx, country in enumerate(countries_order):
        masks_dict[country] = cv2.resize(predicted_mask[:, :, idx], (img.shape[1], img.shape[0]))

    return masks_dict

# Ejemplo de uso:
model_path = "Segmentation_country\DA_mobilenetv2_300_.h5"
img_path = "Segmentation_country\war_img_ (23).png"
masks = predict_masks(model_path, img_path)

# Visualizar una de las máscaras (cambia la clave para visualizar diferentes máscaras)
plt.imshow(masks["alaska"]*255, cmap='gray')
plt.show()