import pyautogui
import datetime

import pygetwindow as gw
import win32gui
import sys
import cv2
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
    sys.exit(1)
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
    
    crop_screenshot = screenshot.crop((0, 0, 100, 100))
    cv2.imwrite("crop_screenshot.jpg", crop_screenshot)