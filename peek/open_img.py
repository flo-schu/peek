from image.process import Image
from evaluation.plot import Viz
import numpy as np
import cv2
from matplotlib import pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='Get meta data of image')
parser.add_argument('input' , type=str, help='path to image')
args = parser.parse_args()

i = Image(path=args.input)
i.read_raw()

imo = i.img[400:1300, 1000:2700,:]
ims = cv2.resize(imo, (0,0), fx=0.3, fy=0.3)
# Viz.color_analysis(im[150:750, 600:700,:], "r")
# Viz.color_analysis(im[150:750, 600:700,:], "g")
# Viz.color_analysis(im[150:750, 600:700,:], "b")
# plt.show()
print("start")
for r in range(0,10):
    im = 255-cv2.inRange(ims, np.array([0,0,0]), np.array([0,0,0])+r*10)
    im = i.min_filter(3, im)
    detector = cv2.QRCodeDetector()
    message, bbox, _ = detector.detectAndDecode(im)
    if message != "":
        break

# plt.imshow(im)
# plt.show()
# input()
# im = cv2.addWeighted( im, 2, im, 0, 0)
# im = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
# im = i.max_filter(3, im)
# im = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
# im = i.max_filter(3, im)


print(message, r)
plt.imshow(im)
plt.show()
