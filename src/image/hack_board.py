from img_proc import Series, Image
from rawpy import rawpy
path = "../../data/pics/20201203/Serienbilder043/"

i= Image(path+"PNAN1226.RW2")
i.read_raw()
i.read_qr_code()
i.id


with open(path+"PNAN1226.RW2", 'rb') as f:
    header = f.read(128).split()

int(header[1]), int(header[2])

header[2]

from PIL import Image as pilimg
import PIL_plugin_rw2

pilimg.open(path+"PNAN1226.RW2" )


with rawpy.imread(path+"PNAN1226.RW2") as raw:
    img = raw

img
s = Series(path)
s.read_images()
s.images[0].black_level_per_channel
# s.save('img')
# s.difference()
# s.save('diff')
s.read_qr_code

i = s.images[0]


a = s.images[2]

#edge detector
from img_proc import Series, Image
import cv2
from matplotlib import pyplot as plt
path = "../../data/pics/20201203/Serienbilder043/"

i= Image(path+"PNAN1166.RW2")
i.read_raw()
i.read_qr_code()
gray = cv2.cvtColor(i.img,cv2.COLOR_BGR2GRAY)
plt.imshow(gray,cmap="gray")
horiz=cv2.Sobel(gray,0,1,0,cv2.CV_64F)
vert=cv2.Sobel(gray,0,0,1,cv2.CV_64F)

bitwise_or=cv2.bitwise_or(horiz,vert)
bitwise_or.max()

cv2.imwrite(path+"1166_edge.tiff", bitwise_or)


# motion
from img_proc import Series, Image
import cv2
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from skimage.measure import compare_ssim
import imutils
import numpy as np
import imageio


path = "../../data/pics/20201203/Serienbilder043/"
s = Series(path)
s.read_images()

a = s.images[0].img
b = s.images[1].img

ag = cv2.cvtColor(a,cv2.COLOR_BGR2GRAY)
bg = cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
diff = a.copy()

diff = cv2.absdiff(a, b)
a1 = a.astype('int') 
b1 = b.astype('int') 
diff2 = np.diff((a1,b1),axis=0)[0]
diff3 = np.where(diff2 >= 0, diff2, 0)

cv2.imwrite(path+"3_diff.tiff", diff3)

gray = cv2.cvtColor(diff3.astype('uint8'),cv2.COLOR_BGR2GRAY)
cv2.imwrite(path+"3_diff_gray.tiff", gray)

plt.hist(gray.flatten(), bins=100)

cv2.imwrite(path+"1166_edge.tiff", bitwise_or)
#threshold the gray image to binarise it. Anything pixel that has
#value more than 3 we are converting to white
#(remember 0 is black and 255 is absolute white)
#the image is called binarised as any value less than 3 will be 0 and
# all values equal to and more than 3 will be 255
(T, thresh) = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
cv2.imwrite(path+"1166_thresh.tiff", thresh)
cnts = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

type(cnts)


tagged = b.copy()
sliced = b.copy()
mar = 10
pot_orgs = []

for c in cnts:
    # fit a bounding box to the contour
    if max(c.shape) > 10:
        (x, y, w, h) = cv2.boundingRect(c)
        pot_orgs.append(sliced[y-mar:y+h+mar,x-mar:x+w+mar])
        cv2.rectangle(tagged, (x-mar, y-mar), (x + w + mar, y + h + mar), (0, 255, 0), 2)


imageio.imwrite(path+"changes3.png", new)

dimy = 128
for i in range(len(pot_orgs)):
    snip = pot_orgs[i]
    dim = (int(snip.shape[1]*dimy/snip.shape[0]), int(dimy))
    im = cv2.resize(snip, dim, interpolation = cv2.INTER_AREA)
    imageio.imwrite(path+"1166/"+str(i)+".tiff", im)

s.difference()

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


# evaluate accuracy, smooth

from img_proc import Series, Image
from rawpy import rawpy
from matplotlib import pyplot as plt
import imageio
import numpy as np
import cv2
path = "../../data/pics/20201203/Serienbilder043/"


s = Series(path)
s.read_images()
diffs, contours, tagged_ims = s.motion_analysis(lag=1)


kernel = np.ones((10,10),np.float32)/100

ims = np.array([i.img for i in s.images])
imgrey = np.array([cv2.cvtColor(i.img, cv2.COLOR_BGR2GRAY) for i in s.images])
imsmoothed = np.array([cv2.filter2D(i.img,-1,kernel) for i in s.images])

dst = cv2.filter2D(s.images[0].img,-1,kernel)

plt.plot(dst[:,300,0].transpose())
plt.plot(imgrey[:,300,:].transpose())
plt.plot(ims[:,300,:,0].transpose())
plt.plot(imsmoothed[:,300,:,2].transpose(), alpha=.5)


diff= np.diff(imsmoothed.astype(int), axis=0)
diff2= np.diff(ims.astype(int), axis=0)

plt.plot(diff[:,10,:,0].transpose())
plt.plot(diff2[:,10,:,0].transpose())

maxdif = diff.max(axis=2)
maxdif2 = diff2.max(axis=2)

plt.plot(maxdif[:,:,0].transpose())
plt.plot(maxdif2[:,:,0].transpose())