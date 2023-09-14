import time
import os
import cv2
import sys

print('comecando a leitura da tela')

def get_white_pixels(image):
    #cv2 binary image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    image = cv2.threshold(image, 230, 255, cv2.THRESH_BINARY )[1]
    return image


detect_folder = './printscreen_consumer/'

while True:
    #detect if a new file jpg or png was created
    #if yes, read the file and predict the countries
    #get all files from detect_folder
    files = os.listdir(detect_folder)
    #sort by filesystem date, get newest
    if (len(files) > 0):
        
        files.sort(key=lambda x: os.path.getmtime(os.path.join(detect_folder, x)))

        newest_file = files[-1]
        print(files)
        print('newest file', newest_file)
        #delete all files
        
        image = cv2.imread(detect_folder+newest_file)
        image = get_white_pixels(image)
        cv2.imwrite("result.jpg", image)
        sys.exit(1)
        for file in files:
            os.remove(detect_folder+file)   
    #sys.exit(1)

        #read the image
    #time sleep
    time.sleep(0.5)
