from tensorflow.keras.models import load_model
import cv2
import numpy as np
import matplotlib.pyplot as plt
from openvino.runtime import Core #pip3 install openvino==2023.0.2
import time

class recognition_troop_number():
    def __init__(self):
        self.model_path = "text-recognition-resnet-fc-ft-v1.xml"
        self.bin_path = "text-recognition-resnet-fc-ft-v1.bin"
        self.ie = Core()
        self.recognition_model = self.ie.read_model(
            model=self.model_path, weights=self.bin_path
        )
        self.compiled_model = self.ie.compile_model(model=self.recognition_model, device_name="CPU")
        self.input_layer = self.compiled_model.input(0)
        self.output_layer = self.compiled_model.output(0)
        self.letters = "~0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.network_height = self.input_layer.shape[2]
        self.network_width = self.input_layer.shape[3]
        print('layer input shape: ', self.input_layer.shape)

    def recog_image(self, image):
        time_recognition = time.time()
        print(image.shape)
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized_img = cv2.resize(gray_img, (self.network_width, self.network_height))
        infer_img = resized_img.reshape((1,) * 2 + resized_img.shape)
#        print(infer_img.shape)
        result = self.compiled_model([infer_img])[self.output_layer]
        time_recognition_end = time.time()
        print("time infer recognition: ", time_recognition_end - time_recognition)
        # # Squeeze the output to remove unnecessary dimension.
        recognition_results_test = np.squeeze(result)

        print(recognition_results_test.shape)

        result_debug = ''
        ret = ''
        stop_letter = False
        for letter in recognition_results_test:
            parsed_letter = self.letters[letter.argmax()]
            if (parsed_letter == '~'):
                stop_letter = True
            if (stop_letter == False):
                ret += parsed_letter
            result_debug += parsed_letter
        #print('debug: ', result_debug)
        if (ret == ''):
            ret = 'None'
        return ret



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

    umbral = 0.6  # Establece el valor de umbral que deseas
    # Aplica el umbral a la matriz de predicción
    predicted_mask = (predicted_mask >= umbral).astype(np.uint8)
    kernel = np.ones((7, 7), np.uint8)
    predicted_mask = cv2.morphologyEx(predicted_mask, cv2.MORPH_CLOSE, kernel)
    # Aplica la operación "opening" para eliminar áreas pequeñas (outliers)
    kernel_open = np.ones((5, 5), np.uint8)
    predicted_mask = cv2.morphologyEx(predicted_mask, cv2.MORPH_OPEN, kernel_open)
    # Aplica la dilatación para aumentar el ancho de los bordes
    kernel_dilate = np.ones((5, 5), np.uint8)
    predicted_mask = cv2.dilate(predicted_mask, kernel_dilate, iterations=1)

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
        mask = cv2.resize(predicted_mask[:, :, idx], (img.shape[1], img.shape[0]))
        x, y, w, h = cv2.boundingRect(mask)
        # Recortar la imagen original con el rectángulo que contiene la máscara
        original_img = img.copy()
        result_img = cv2.bitwise_and(original_img, original_img, mask=mask)
        cropped_img = result_img[y:y+h, x:x+w]

        masks_dict[country] = cropped_img#cv2.resize(predicted_mask[:, :, idx], (img.shape[1], img.shape[0]))
    return masks_dict


# Ejemplo de uso:
model_path = "DA_3500mobilenetv2.h5"
img_path = "war_img.png"
masks = predict_masks(model_path, img_path)
ocr = recognition_troop_number()

# Visualizar una de las máscaras (cambia la clave para visualizar diferentes máscaras)
for item, mask in masks.items():
    print(item)
    recog_image = mask.copy()
    res = ocr.recog_image(recog_image)
    print('resultado OCR: ', res)
    #print res until ~
    
    #gray_img = cv2.cvtColor(mask.copy, cv2.COLOR_BGR2GRAY)
    cv2.imshow(item, mask)
    cv2.resizeWindow(item, 600,600)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
# plt.imshow(masks["mexico"])
# plt.show()