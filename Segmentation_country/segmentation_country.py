from tensorflow.keras.models import load_model
import cv2
import numpy as np
import matplotlib.pyplot as plt
from openvino.runtime import Core #pip3 install openvino==2023.0.2
import time

class recognition_class():
    def __init__(self, model_path, bin_path):
        self.model_path = model_path 
        self.bin_path = bin_path
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


    def pre_process_mask(self, mask):
        pre_processed_im = cv2.threshold(mask.copy(), 230, 255, cv2.THRESH_BINARY )[1]
        image_gray = cv2.cvtColor(pre_processed_im, cv2.COLOR_BGR2GRAY)
        
        kernel = np.ones((5,5),np.uint8)
        final_img = cv2.morphologyEx(image_gray, cv2.MORPH_CLOSE, kernel)
        #final_img = cv2.morphologyEx(final_img, cv2.MORPH_OPEN, kernel)
        #cv2.imwrite(output_filename, image_gray)

        kernel = np.ones((3,3),np.uint8)
        final_img = cv2.dilate(final_img,kernel,iterations = 1)
        cnts,new = cv2.findContours(final_img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)
        
        contour_choice = None
        area_choice = None
        for c in cnts:
            area = cv2.contourArea(c)        
            if(area < 50 and area > 1):
                contour_choice = c
                area_choice = area
                break

        x,y,w,h = cv2.boundingRect(contour_choice)

        # Aumenta el tamaño del bounding box
        nuevo_x = max(0, x - 10)  # Puedes ajustar el valor 10 según tus necesidades
        nuevo_y = max(0, y - 10)  # Puedes ajustar el valor 10 según tus necesidades
        nuevo_w = min(final_img.shape[1] - nuevo_x, w + 20)  # Puedes ajustar el valor 20 según tus necesidades
        nuevo_h = min(final_img.shape[0] - nuevo_y, h + 20)  # Puedes ajustar el valor 20 según tus necesidades

        # Recorta la imagen con el nuevo bounding box
        crop_img = mask.copy()[nuevo_y:nuevo_y+nuevo_h, nuevo_x:nuevo_x+nuevo_w]
        crop_img = cv2.resize(crop_img, (32, 32))
        # Crear un nuevo arreglo con tamaño 100x32 y llenarlo con ceros
        nueva_imagen = np.zeros((32, 100, 3), dtype=np.uint8)

        # Calcular las coordenadas para centrar la imagen redimensionada en el nuevo arreglo
        x_offset = (nueva_imagen.shape[1] - crop_img.shape[1]) // 2
        y_offset = (nueva_imagen.shape[0] - crop_img.shape[0]) // 2

        # Colocar la imagen redimensionada en el centro del nuevo arreglo
        nueva_imagen[y_offset:y_offset+crop_img.shape[0], x_offset:x_offset+crop_img.shape[1]] = crop_img
        return nueva_imagen
    
    def recog_image(self, image, item):

        if(image.shape[0] == 0 or image.shape[1] == 0):
            return None
        
        pre_processed_im = self.pre_process_mask(image.copy())
        

        gray_img = cv2.cvtColor(pre_processed_im, cv2.COLOR_BGR2GRAY)
        resized_img = cv2.resize(gray_img, (self.network_width, self.network_height))
        write_image = resized_img.copy()
        infer_img = resized_img.reshape((1,) * 2 + resized_img.shape)

        result = self.compiled_model([infer_img])[self.output_layer]
        recognition_results_test = np.squeeze(result)

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
            ret = '1'

        #filename = 'output_crops_mask/' + item + '_' + str(ret) + '.jpg'
        #cv2.imwrite(filename, write_image)
        return ret


class segmentation_country_class():

    def __init__(self, model_path):
        self.model_path = model_path
        self.model = load_model(self.model_path, compile=False)
        # self.countries_order = [
        #     "alaska", "mackenzie", "groenladia", "vancouver", "ottawa", "labrador",
        #     "california", "nova york", "mexico", "venezuela", "peru", "brasil", 
        #     "argentina", "islandia", "inglaterra", "francia", "alemania", "suecia",
        #     "polonia", "moscou", "omsk", "dudinka", "siberia", "vladvostok", 
        #     "argelia", "egipto", "orientemedio", "aral", "Tchita", "congo", "sudan",
        #     "india", "china", "mongolia", "africa del sur", "madagascar", "vietnan",
        #     "japon", "sumatra", "borneo", "neuva guinea", "australia"
        # ]
        self.countries_order = [
            "Alaska", "Mackenzie", "Groenlandia", "Vancouver", "Ottawa", "Labrador",
            "California", "Nueva York", "México", "Venezuela", "Perú", "Brasil", 
            "Argentina", "Islandia", "Inglaterra", "Francia", "Alemania", "Suecia",
            "Polonia", "Moscú", "Omsk", "Dudinka", "Siberia", "Vladivostok", 
            "Argelia", "Egipto", "Oriente Medio", "Aral", "Chita", "Congo", "Sudán",
            "India", "China", "Mongolia", "Sudáfrica", "Madagascar", "Vietnam",
            "Japón", "Sumatra", "Borneo", "Nueva Guinea", "Australia"
        ]

                
    def predict_masks(self, img_path):
        img = cv2.imread(img_path)
        input_shape = (320, 608, 3)
        img_resized = cv2.resize(img, (input_shape[1], input_shape[0]))/ 255
        img_preprocessed = np.array([img_resized])
        
        # Obtener la predicción del modelo
        prediction = self.model.predict(img_preprocessed)
        predicted_mask = prediction[0]

        umbral = 0.5  # Establece el valor de umbral que deseas
        # Aplica el umbral a la matriz de predicción
        predicted_mask = (predicted_mask >= umbral).astype(np.uint8)
        kernel = np.ones((15, 15), np.uint8)
        predicted_mask = cv2.morphologyEx(predicted_mask, cv2.MORPH_CLOSE, kernel)
        #predicted_mask = cv2.morphologyEx(predicted_mask, cv2.MORPH_CLOSE, kernel)
        # Aplica la operación "opening" para eliminar áreas pequeñas (outliers)
        #kernel_open = np.ones((5, 5), np.uint8)
        #predicted_mask = cv2.morphologyEx(predicted_mask, cv2.MORPH_OPEN, kernel_open)
        
        # Aplica la dilatación para aumentar el ancho de los bordes
        kernel_dilate = np.ones((3, 3), np.uint8)
        predicted_mask = cv2.dilate(predicted_mask, kernel_dilate, iterations=1)

        # Nombres de los países en orden

        # Crear un diccionario para almacenar las máscaras predichas
        masks_dict = {}
        # for idx, country in enumerate(self.countries_order):
        #     mask = cv2.resize(predicted_mask[:, :, idx], (img.shape[1], img.shape[0]))
        #     x, y, w, h = cv2.boundingRect(mask)
        #     # Recortar la imagen original con el rectángulo que contiene la máscara
        #     original_img = img.copy()
        #     result_img = cv2.bitwise_and(original_img, original_img, mask=mask)
        #     cropped_img = result_img[y:y+h, x:x+w]

        #     masks_dict[country] = cropped_img#cv2.resize(predicted_mask[:, :, idx], (img.shape[1], img.shape[0]))
        min_mask_size = 100  # Establece el umbral mínimo de tamaño
        for idx, country in enumerate(self.countries_order):
            mask = cv2.resize(predicted_mask[:, :, idx], (img.shape[1], img.shape[0]))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Ordena los contornos de mayor a menor área
                contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
                if cv2.contourArea(contours[0]) >= min_mask_size:
                    x, y, w, h = cv2.boundingRect(contours[0])
                    # Aplica el rectángulo de recorte solo si el tamaño del contorno es suficiente
                    original_img = img.copy()
                    result_img = cv2.bitwise_and(original_img, original_img, mask=mask)
                    cropped_img = result_img[y:y+h, x:x+w]
                    masks_dict[country] = cropped_img
                else:
                    # Si el contorno más grande no cumple el umbral de tamaño, usa la imagen original
                    x, y, w, h = cv2.boundingRect(mask)
                    original_img = img.copy()
                    result_img = cv2.bitwise_and(original_img, original_img, mask=mask)
                    cropped_img = result_img[y:y+h, x:x+w]
                    masks_dict[country] = cropped_img
            else:
                # Si no se encontraron contornos, usa la imagen original
                x, y, w, h = cv2.boundingRect(mask)
                original_img = img.copy()
                result_img = cv2.bitwise_and(original_img, original_img, mask=mask)
                cropped_img = result_img[y:y+h, x:x+w]
                masks_dict[country] = cropped_img
        return masks_dict



#----------------- EXEMPLO DE USO ABAIXO -----------------#

# segmentation_obj = segmentation_country_class("./DA_3500mobilenetv2.h5")
# masks = segmentation_obj.predict_masks("war_img.png")
# ocr = recognition_class("text-recognition-resnet-fc-ft-v1.xml","text-recognition-resnet-fc-ft-v1.bin")

# # Visualizar una de las máscaras (cambia la clave para visualizar diferentes máscaras)
# for item, mask in masks.items():
#     print(item)
#     recog_image = mask.copy()
#     res = ocr.recog_image(recog_image)
#     print('resultado OCR: ', res)

#     cv2.imshow(item, mask)
#     cv2.resizeWindow(item, 600,600)

#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
