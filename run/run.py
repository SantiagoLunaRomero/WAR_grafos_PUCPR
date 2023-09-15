import pyautogui
import datetime

import pygetwindow as gw
import win32gui
import sys
import cv2
import os
import time
import numpy as np
sys.path.append('../')
from Segmentation_country.segmentation_country import segmentation_country_class, recognition_class
from agents.simple_agent_matrix import simple_agent_matrix


def get_chrome_printscreen(filename_save):
    # Nombre de la ventana de Google Chrome
    chrome_window_title = "Google Chrome"

    # Obtener todas las ventanas abiertas
    windows = gw.getAllTitles()

    # Buscar la ventana de Google Chrome en la lista de ventanas
    chrome_window = None
    for window_title in windows:
        if chrome_window_title in window_title:
            chrome_window = gw.getWindowsWithTitle(window_title)[0]
            break

    # Verificar si se encontró la ventana de Chrome
    if chrome_window is None:
        print('nenhuma janela chrome detectada')
        return False

    # Obtener el título de la ventana de Chrome
    chrome_title = win32gui.GetWindowText(chrome_window._hWnd)

    window_title = chrome_title

    # # Obtener la ventana por su título
    window = gw.getWindowsWithTitle(window_title)

    # # Verificar si se encontró la ventana
    if len(window) == 0:
        print(f"No se encontró una ventana con el título '{window_title}'.")

    else:
        # Seleccionar la primera ventana encontrada (puedes ajustar esto si hay varias)
        target_window = window[0]

        # Activar la ventana
        target_window.activate()

        # Capturar la ventana activa
        #
        screenshot = pyautogui.screenshot(region=[target_window.left, target_window.top, target_window.width, target_window.height])

        # Generar un nombre de archivo único basado en la fecha y hora
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"screenshot_{timestamp}.png"

        # Guardar la captura de pantalla en un archivo
        screenshot.save(filename)

        print(f"Captura de pantalla de la ventana '{window_title}' guardada como {filename}")

        cv_image = cv2.imread(filename)

        crop_image = cv_image[200:900, 200:1300]
        # cv2.imshow("cropped", crop_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        cv2.imwrite(filename_save, crop_image)
        os.remove(filename)
        return True

def get_player_color(image):

    player_color = ''
    print('get player color')
    a2D = image.reshape(-1,image.shape[-1])
    #remove a2D [0,0,0] items
    print('a2D shape: ', a2D.shape)
    time_start = time.time()
    a2D = a2D[np.all(a2D != [0,0,0], axis=1)] #removendo black pixels
    #removendo pixels brancos
    a2D = a2D[np.all(a2D!=[255,255,255], axis=1)]
    print('a2D pos remocao black pixels e pixels brancos shape: ', a2D.shape)
    col_range = (256, 256, 256) # generically : a2D.max(0)+1
    a1D = np.ravel_multi_index(a2D.T, col_range)
    bgr_format = np.unravel_index(np.bincount(a1D).argmax(), col_range)
    #sai no formato [Blue, Green, Red] de chances
    print('cor predominante: ', bgr_format )
    time_end = time.time()
    print('time to get color: ', time_end - time_start)
    cv2.imshow('teste', image)
    cv2.resizeWindow('teste', 600,600)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    None

segmentation_prediction = segmentation_country_class("./DA_rodrigo_4000_mobilenetv2.h5")
ocr = recognition_class("text-recognition-resnet-fc-ft-v3-acc.xml","text-recognition-resnet-fc-ft-v3-norm.bin")
screenshot_filepath = "crop_screenshot_teste.jpg"




agente = simple_agent_matrix()

while(True):
    print('Digite o seu comando: \n')
    print('1 - Tirar printscreen\n')
    print('2 - Tirar printscreen e fazer ocr\n')
    print('3 - usar jpg teste\n')
    print('4 - get matrix estado com imagem printscreen\n')
    comando = input('Digite o comando: ')
    
    os.system('cls')
    if (comando == '1'):
        if (not get_chrome_printscreen(screenshot_filepath)):
            print("No se encontró una ventana con el título 'Google Chrome'")
            sys.exit()
        print('Printscreen tirado com sucesso!\n')
    if (comando == '2'):
        if (not get_chrome_printscreen(screenshot_filepath)):
            print("No se encontró una ventana con el título 'Google Chrome'")
            sys.exit()
        print('Printscreen tirado com sucesso!\n')
        masks = segmentation_prediction.predict_masks(screenshot_filepath)
        
        for item, mask in masks.items():
            recog_image = mask.copy()
            res = ocr.recog_image(recog_image)
            print("pais: {0} com {1} tropas".format(item, res))
            if ((mask is None) or (res is None)):
                print('mask is none')
                continue
            
            cv2.imshow(item, mask)
            cv2.resizeWindow(item, 600,600)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    if (comando == '3'):
        test_path = 'crop_teste.jpg'
        masks = segmentation_prediction.predict_masks(screenshot_filepath)
        for item, mask in masks.items():
            recog_image = mask.copy()
            res = ocr.recog_image(recog_image)
            print("pais: {0} com {1} tropas".format(item, res))
            if ((mask is None) or (res is None)):
                print('mask is none')
                continue


            # cv2.imshow(item, mask)
            # cv2.resizeWindow(item, 600,600)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            # cv2.imshow(item, mask)
            # cv2.resizeWindow(item, 600,600)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
        # imgeral = cv2.imread(screenshot_filepath)
        # cv2.imshow('imagem', imgeral)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    if (comando == '4'):
        player_dict = {}
        imgeral = cv2.imread(screenshot_filepath)
        masks = segmentation_prediction.predict_masks(screenshot_filepath)
        for item, mask in masks.items():
            
            recog_image = mask.copy()
            color = get_player_color(recog_image)
            troop = ocr.recog_image(recog_image)
            
            print("pais: {0} com {1} tropas".format(item, troop))
            
            if ((mask is None) or (troop is None)):
                print('pais nao identificado')
                continue


# cv_image = cv2.imread("crop_screenshot.jpg")
# masks = segmentation_prediction.predict_masks("crop_screenshot.jpg")




