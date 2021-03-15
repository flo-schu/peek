from image.process import Image
import cv2
from matplotlib import pyplot as plt

i = Image(path="../data/pics/20210302/PNAN7994.RW2")
i.read_raw()

im = i.img[500:1500, 1300:2600,:]
# im = cv2.resize(im, (0,0), fx=0.75, fy=0.75)
im = cv2.addWeighted( im, 2, im, 0, 0)
im = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
im = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
im = i.max_filter(3, im)
# im = i.min_filter(3, im)


detector = cv2.QRCodeDetector()
message, bbox, _ = detector.detectAndDecode(im)

print(message)

plt.imshow(im)
plt.show()
