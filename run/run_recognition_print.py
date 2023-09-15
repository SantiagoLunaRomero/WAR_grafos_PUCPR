import time
import os
import cv2
import sys

print('comecando a leitura da tela')
class recognition_print():
    def __init__(self, detect_folder):
        self.detect_folder = './printscreen_consumer/'
        None

    def run(self):
                
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
                cv2.imwrite("result.jpg", image)
                sys.exit(1)
                for file in files:
                    os.remove(detect_folder+file)   
            #sys.exit(1)

                #read the image
            #time sleep
            time.sleep(0.5)


