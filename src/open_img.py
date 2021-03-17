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

im = i.img[500:1500, 1200:2700,:]
# im = cv2.resize(im, (0,0), fx=0.75, fy=0.75)

# Viz.color_analysis(im[150:750, 600:700,:], "r")
# Viz.color_analysis(im[150:750, 600:700,:], "g")
# Viz.color_analysis(im[150:750, 600:700,:], "b")
# plt.show()
im = 255-cv2.inRange(im, np.array([0,0,0]), np.array([70,40,40]))
# plt.imshow(im)
# plt.show()
# input()
# im = cv2.addWeighted( im, 2, im, 0, 0)
# im = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
# im = i.max_filter(3, im)
# im = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
im = i.min_filter(5, im)

detector = cv2.QRCodeDetector()
message, bbox, _ = detector.detectAndDecode(im)

print(message)
print(i.img)
print(np.median(i.img[:,:,0].flatten()))
plt.imshow(i.img)
plt.show()
