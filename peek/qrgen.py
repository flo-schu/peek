# script to a QR code which is attached to the nanocosms 
# so their foto can be automatically matched to an ID 

#TODO: put workhorse inside class in image.prep

import numpy as np
import qrcode
import os
import cv2
import matplotlib.pyplot as plt

# generate QR codes
# parameters
dirname = "../../data/pics/qrcodes"

message = "NANO20_{}"
qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_Q,
    box_size=10,
    border=6
)



n = 80
xspace = 0 # pixels
yspace = 0
nrows = 10
ncols = 8

for i in np.arange(1,n+1):
    print(message.format(i))
    qr.clear()
    qr.add_data(message.format(i))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    plt.imshow(img, cmap="gray")
    img.save(os.path.join(dirname,"qr"+str(i)+".png"))



# arrange in grid
# parameters
dirname = "../../data/pics/qrcodes"
n = 80
xspace = 0 # pixels
yspace = 0
nrows = 10
ncols = 8

ims = []
for i in np.arange(1,n+1):
    print(i)
    ims.append(cv2.imread(os.path.join(dirname,"qr"+str(i)+".png")))

# set up blank doc
x,y,z = ims[0].shape
xdim = x * ncols + xspace * ncols
ydim = y * nrows + yspace * nrows
zdim = z
doc = np.ndarray((ydim,xdim,zdim), dtype=int)
doc += 256

for i in np.arange(nrows):
    for j in np.arange(ncols):
        index = i*ncols+j
        if index <= n-1:
            ymin = i*y+yspace
            ymax = (i+1)*y+yspace
            xmin = j*x+xspace
            xmax = (j+1)*x+xspace
            doc[ymin:ymax, xmin:xmax, :] = ims[index]
    
cv2.imwrite(dirname+"/Codes.png",doc)

