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
#from agents.simple_agent_matrix import simple_agent_matrix
from misiones import misiones
from tablero_jugador import Tablero
from Jugadores.jugador import Jugador
from Jugadores.jugadorGrafoOptimizado_2Cambios import JugadorGrafoOptimizado

import math
from matplotlib import pyplot as plt   

def calcular_diferencia_color(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2 = color2

    diferencia = math.sqrt((r2 - r1)**2 + (g2 - g1)**2 + (b2 - b1)**2)
    return diferencia

def identificar_color(color_a_identificar, color_referencia, umbral):
    diferencia = calcular_diferencia_color(color_a_identificar, color_referencia)
    if diferencia <= umbral:
        return True
    else:
        print(diferencia,umbral)
        return False


# color_a_identificar = (50, 30, 180)  # Cambia estos valores por los del color que quieres identificar
# color_referencia = (150, 35, 100)
# umbral = 10  # Puedes ajustar este umbral según lo que consideres una variación pequeña

# resultado = identificar_color(color_a_identificar, color_referencia, umbral)
# print(resultado)
# # Ploteo de los colores
# colores = [color_referencia, color_a_identificar]
# etiquetas = ['Color de Referencia', 'Color a Identificar']

# plt.figure(figsize=(5, 2))
# for i in range(len(colores)):
#     plt.subplot(1, 2, i+1)
#     plt.imshow([[colores[i]]])
#     plt.axis('off')
#     plt.title(etiquetas[i])

# plt.show()
# sys.exit()




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
        #os.remove(filename)
        return True

def get_player_color(image):

    try:
        player_color = ''
        a2D = image.reshape(-1,image.shape[-1])
        #remove a2D [0,0,0] items
        a2D = a2D[np.all(a2D >= [10,10,10], axis=1)] #removendo black pixels
        #removendo pixels brancos
        a2D = a2D[np.all(a2D<=[240,240,240], axis=1)]
        print('a2D pos remocao black pixels e pixels brancos shape: ', a2D.shape)
        col_range = (256, 256, 256) # generically : a2D.max(0)+1
        a1D = np.ravel_multi_index(a2D.T, col_range)
        bgr_format = np.unravel_index(np.bincount(a1D).argmax(), col_range)
        print('bgr_format: ', bgr_format)
        #colores = ["blue", "red", "green", "purple", "yellow", "black"]
        colores ={"red" : [49,34,185],
                "blue":[181,148,21],
                "green":[53,141,87],
                "yellow":[30,176,218],
                "purple":[116,46,76],
                "black":[56,56,56]} #BLUE GREEN RED
        
        player_color=None
        for key in colores:
            if (identificar_color(bgr_format, colores[key], 10)):
                player_color = key
                break
            else:
                player_color = "blue"
        #time_end = time.time()
        #print('time to get color: ', time_end - time_start)
    except Exception as e:
        player_color = "blue"
        print('error: ', e)
    finally:
        return player_color


def create_matrix_from_masks(masks, ocr: recognition_class):
    #cria matriz de adjacencia
    matrix = []
    territory_army_dict = {}
    for item,mask in masks.items():
        try:
            army = int(ocr.recog_image(mask))
        except Exception as e:
            print('Erro recog image tropas {0}'.format(item))
            print('Erro: ', e)            
            army = 1
        if(army is None):
            army = 1

        player_color = get_player_color(mask.copy())

        territory_army_dict[item] = [army,player_color]

        if (player_color is None):
            print('pais: {0} com {1} tropas e cor {2}'.format(item, army, player_color))

            print('pais {0} army {1} color {2}'.format(item, army, player_color))        
            # cv2.imshow(item, mask)
            # cv2.resizeWindow(item, 300, 300)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
        filename = 'output_crops_mask/' + item + '_' + str(army) + '_' + player_color +'.jpg'
        cv2.imwrite(filename, mask)

    # for territory, army in territory_army_dict.items():
    #     print('territory {0} e army {1}'.format(territory, army))

        # #cria linha da matriz
        # matrix_line = []
        # for territory2, army2 in territory_army_dict.items():
        #     if (territory == territory2):
        #         matrix_line.append(0)
        #     else:
        #         matrix_line.append(1)
        # matrix.append(matrix_line)
    
    return territory_army_dict


segmentation_prediction = segmentation_country_class("./DA_rodrigo_4000_mobilenetv2.h5")
ocr = recognition_class("text-recognition-resnet-fc-ft-v3-norm.xml","text-recognition-resnet-fc-ft-v3-norm.bin")
screenshot_filepath = "crop_screenshot_completo.jpg"
#CORES  = [  0   ,  1  ,   2   ,    3    ,  4     ,   5  ]
colores = ["blue","red","green","purple","yellow","black"]
#MISAON
cinza_objectivo = 0
Jugador_puc = JugadorGrafoOptimizado("JOGADOR_PUCPR_IA", colores[0], misiones[cinza_objectivo])

mision_desconocida = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
jugador1 = Jugador("1",colores[1],mision_desconocida)
jugador2 = Jugador("2",colores[2],mision_desconocida)
jugador3 = Jugador("3",colores[3],mision_desconocida)
jugador4 = Jugador("4",colores[4],mision_desconocida)
jugador5 = Jugador("5",colores[5],mision_desconocida)

jugadores = [Jugador_puc,jugador1,jugador2,jugador3,jugador4,jugador5]
tablero = Tablero(jugadores)
Jugador_puc.interpretar_mision(misiones[cinza_objectivo])
Jugador_puc.descripcion = misiones[cinza_objectivo].descripcion

#agente = simple_agent_matrix()

while(True):
    print('Digite o seu comando: \n')
    print('1 - Tirar printscreen\n')
    print('2 - Tirar printscreen e fazer ocr\n')
    print('3 - jogar agente\n')
    print('4 - get matriz com ultimo printscreen \n')
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

    if (comando == '3'):
        masks = segmentation_prediction.predict_masks(screenshot_filepath)
        dic = create_matrix_from_masks(masks, ocr)

        tablero.actualizarFronDic(dic)
        tablero.mostrar_tablero()
        
        print('selecione a acao: \n')
        print('1 - reforcar\n')
        
        print('2 - atacar\n')
        print('3 - mover\n')
        acao = input('selecione a acao: \n')

        Jugador_puc.tropas_por_turno = 3
        Jugador_puc.actualizar_tropas_por_turno()
        Jugador_puc.iniciar_turno()

        Jugador_puc.reforzar(tablero)

        Jugador_puc.atacar(tablero)
        
        Jugador_puc.mover_tropas(tablero)
        tablero.reset_tropas_recibidas()

        # for key,value in dic:
        #     print('key: ', key)

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
        dic = create_matrix_from_masks(masks, ocr)
        print('pre actualizar matriz')
        print(len(dic))
        tablero.actualizarFronDic(dic)
        tablero.mostrar_tablero()

# cv_image = cv2.imread("crop_screenshot.jpg")
# masks = segmentation_prediction.predict_masks("crop_screenshot.jpg")




