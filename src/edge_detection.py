

# ich muss die detection nur oben machen. Denn da sind die unbeweglichen Culex.
# Alles was nicht an der wasseroberfläche ist, bewegt sich. Dann muss ich nur noch die 
# Intersection der oben bewgten und edge detektierten voneinander abziehen.

# step by step. Next Daphnia low has to be increased in order not to caputre 

# so I could take the kernel and look
plt.imshow(r[:,:,0]+r[:,:,1])
plt.imshow(r[:,:,0]*2+r[:,:,1]/(r[:,:,2]+1))

i = r[:,:,0] + r[:,:,1]
# %matplotlib
# i.show()
gray = cv.cvtColor(img.img,cv.COLOR_BGR2GRAY)
plt.imshow(i,cmap="gray")
plt.imshow(gray,cmap="gray")
horiz = cv.Sobel(i, 0, 1, 0, cv.CV_64F, ksize=5)
vert  = cv.Sobel(i, 0, 0, 1, cv.CV_64F, ksize=5)

sob = cv.bitwise_or(horiz,vert)
plt.imshow(sob)
# (T, thresh) = cv.threshold(bitwise_or, 250, 255, cv.THRESH_BINARY)
# plt.imshow(thresh,cmap="gray")
cnts = cv.findContours(sob, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)


cv2.imwrite(path+"1166_thresh.tiff", thresh)

plt.imshow(bitwise_or, cmap="gray")

# corner detection


img = i.img
gray = np.float32(gray)
dst = cv.cornerHarris(gray,10,3,0.04)
#result is dilated for marking the corners, not important
dst = cv.dilate(dst,None)
# Threshold for an optimal value, it may vary depending on the image.
img[dst>0.01*dst.max()]=[255,0,0]
plt.imshow(img)


a = Annotations(i, 'motion_analysis', '../data/tag_db.csv')
a.load_processed_tags()
# %matplotlib
a.start()
a.show_tag_number(0)

# - [ ] Important: Write detector for Culex
# - [ ] what about zero sized images?
# - [ ] Address memory problems when six images were taken from one nanocosm (need 1.2 GB
        # memory)