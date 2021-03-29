import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict, cross_val_score, train_test_split
from sklearn import metrics as skm
from ml.plots import plot_precision_recall_vs_threshold, plot_roc_curve, plot_precision_vs_recall

from ml.data import load_annotated_data
data = load_annotated_data(
    path_annotations="data/machine_learning/tag_db.csv",
    path_imgs="data/machine_learning/annotated_images/",
    label_column="label",
    id_columns=["img_date","img_id","img_time","id"],
    add_data=["area"])


X, y = data["data"], data["labels"]
X = X.reshape((X.shape[0], np.prod(X.shape[1:])), order="C")


org = X[10]
org_img = org.reshape(100,100,3)
plt.imshow(org_img, cmap = cm.binary,
          interpolation="nearest")
plt.axis("off")
plt.show()

y[10]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, shuffle=True)

# binary classification

forest_clf = RandomForestClassifier(random_state=42)
forest_clf.fit(X_train, y_train) # train the classifier
forest_clf.predict([X[2]]) # make it predict some digit

# show some results
for index in range(0, X.shape[0], 1):
    digit = X[index]
    predicted = forest_clf.predict([digit])
    if predicted:
        print("{} == {}".format(predicted, y[index]), end="\n")

# generate cross validated predictions
y_pred = cross_val_predict(forest_clf, X_train, y_train, cv=3)
cross_val_score(forest_clf, X_train, y_train, cv=3, scoring="accuracy")


conf_mx = skm.confusion_matrix(y_train, y_pred)
plt.matshow(conf_mx, cmap=plt.cm.gray)
plt.show()
# interpretation
#               predicted
#             | 4  | Not 4 |
#       --------------------
# True     4  | 97 |    1  |  98
# True  not 4 |  2 |  900  | 902
#       --------------------
#               99    901


print(skm.classification_report(y_train, y_pred))
# # recall is the percentage of identified fours of all fours (97 / 98 in this case)
# # sum(y_train_4) # for checking the sum of all fours in y_train_4
# # precision is correctly identified / all identified
# # if I identify 100 objects as apples but only 50 correctly i get a precision of 0.5

# # extract y probabilities
# y_probas = cross_val_predict(forest_clf, X_train,
#                              y_train, cv=3,
#                              method="predict_proba")

# precisions, recalls, thresholds = skm.precision_recall_curve(y_train==1, y_probas[:,1])
# plot_precision_recall_vs_threshold(precisions, recalls, thresholds)

# fpr, tpr, thresholds = skm.roc_curve(y_train==1, y_probas[:,1])
# # fpr = false positive rate = (1 - true negative rate)
# # tpr = true positive rate

# # area under the curve
# plot_roc_curve(fpr, tpr, "Roc Curve")

# How to implement for my data.
# [/] improve image segmentation. better selection of organisms. 
#     There must be a better way for this...
#     https://www.upgrad.com/blog/image-segmentation-techniques/
#     Maybe not the right approach
# [~] go again for edge detection and thresholding. Because with the 
#     classifier it is no problem to overselect (I believe). Approach
#     radical smoothing and homogenizing (max/min stuff). Then adaptive thresholding
#     by regions and then edge.
#     -> after all not super promising. A lot of work and lots of errors
# [ ] organisms must be centered in the image. Otherwise I'm pretty sure
#     random forests will have problems -> no features are generated
# [ ] read: https://benanne.github.io/2015/03/17/plankton.html
# [ ] artificially increase dataset size (see blog post)
# [-] write different annotation implementations
#     + [x] quick and dirty (only tag img of original)
#     + [ ] click tagging with suggestion of contours --> finds also positions
#           of tags. Good if segmentation is run with ML itself
#     + [ ] show whole image with annotated tags
#     + [ ] create a dir with annotated images
# [ ] train my own Haar Cascade classifier
# read https://medium.com/swlh/object-detection-and-instance-segmentation-a-detailed-overview-94ca109274f2
# for non-max surpression read:
# https://www.analyticsvidhya.com/blog/2020/08/selecting-the-right-bounding-box-using-non-max-suppression-with-implementation/
# https://github.com/matterport/Mask_RCNN --> swgmentation


# Problems:
# [ ] duplicates. When segmenting, duplicates are produced and this willthen be 
#     tagged multiple times
# [ ] contours overlap. This is super annoying. -> non max surpression
# [ ] both should be solvable by merging contours
# [ ] continue: 
#     0. REMEMBER: Es ist nicht schlimm wenn haufenweise scheiß detektiert wird
#        der Classifier sollte in der Lage sein das auszusortieren und non
#        maximum surpression zum schluss müsste ausreichen
#     1. finish current detection 
#     2. run detector on cluster
#     3. train and predict model