from img_proc import Series, Image
from rawpy import rawpy
path = "../../data/pics/20201127/Serienbilder093/"

s = Series(path)
s.read_images()
# s.save('img')
# s.difference()
# s.save('diff')
s.read_qr_code

i = s.images[0]


import cv2
a = s.images[2]

#edge detector
image=cv2.imread(path + "PNAN0122.tiff")
gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
horiz=cv2.Sobel(gray,0,1,0,cv2.CV_64F)
vert=cv2.Sobel(gray,0,0,1,cv2.CV_64F)

bitwise_or=cv2.bitwise_or(horiz,vert)
bitwise_or.max()

cv2.imwrite(path+"PNAN0119_edge.tiff", bitwise_or)


# QR code

from img_proc import Series, Image
import imageio
import cv2
from pyzbar import pyzbar
from matplotlib import pyplot as plt

# this works reasonably well
path = "../../data/pics/20201127/Serienbilder093/"
i = Image(path+"PNAN0995.RW2")
i.read_raw()
out = cv2.addWeighted( i.img, 2, i.img, 0, 0)
gray = cv2.cvtColor(out,cv2.COLOR_BGR2GRAY)

(thresh, bwimage) = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
plt.imshow(bwimage, cmap='gray'), plt.axis("off")

pyzbar.decode(bwimage)
imageio.imwrite(path+"bw1.png",bwimage)


# improvement?
contrast = cv2.addWeighted( i.img, 2, i.img, 0, 0)
gray = cv2.cvtColor(contrast,cv2.COLOR_BGR2GRAY)
plt.imshow(gray, cmap='gray'), plt.axis("off")
blur = cv2.GaussianBlur(gray, (9,9), 0)
plt.imshow(blur, cmap='gray'), plt.axis("off")
thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
plt.imshow(thresh, cmap='gray'), plt.axis("off")
code = pyzbar.decode(thresh)[0]
code.data.decode("utf-8")

imageio.imwrite(path+"bw2.png",thresh)

out = cv2.addWeighted( i.img, 2, i.img, 0, 0)



plt.hist(gray.flatten(), bins=50)

imageio.imwrite(path+"test3.png",out)

# plot
# plot
plt.imshow(out, cmap='gray'), plt.axis("off")

plt.imshow(imgen, cmap='gray'), plt.axis("off")

# detect QR code
detector = cv2.QRCodeDetector()
detector.detect(out)


path2 = "../../data/pics/qrcodes/"
image=cv2.imread(path + "PNAN0738.tiff")
image=cv2.imread(path2 + "qr1.png")
cv2.contra
cv2.imshow('Black white image', gray)
image=cv2.imread(path+"QRtest.png")


(thresh, bwimage) = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
cv2.imwrite(path+"QRtestBW.png",bwimage)

cv2.QRCodeDetector()