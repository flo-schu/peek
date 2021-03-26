import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict, cross_val_score
from sklearn import metrics as skm
from ml.plots import plot_precision_recall_vs_threshold, plot_roc_curve, plot_precision_vs_recall

digits = load_digits()
X, y = digits["data"], digits["target"]

some_digit = X[100]
some_digit_image = some_digit.reshape(8,8)
plt.imshow(some_digit_image, cmap = cm.binary,
          interpolation="nearest")
plt.axis("off")
plt.show()

y[100]

X_train, X_test = X[:1000], X[1000:]
y_train, y_test = y[:1000], y[1000:]

shuffle_index = np.random.permutation(1000) # creates a random array
X_train, y_train = X_train[shuffle_index], y_train[shuffle_index]

# binary classification

forest_clf = RandomForestClassifier(random_state=42)
forest_clf.fit(X_train, y_train) # train the classifier
forest_clf.predict([X[0]]) # make it predict some digit

# show some results
for index in range(0, X.shape[0], 10):
    digit = X[index]
    predicted = forest_clf.predict([digit])
    if predicted:
        print("{} == {}".format(predicted, y[index]), end="\n")

# generate cross validated predictions
y_pred = cross_val_predict(forest_clf, X_train, y_train, cv=3)
cross_val_score(forest_clf, X_train, y_train, cv=3, scoring="accuracy")


conf_mx = skm.confusion_matrix(y_train, y_pred, labels=[0,1,2,3,4,5,6,7,8,9])
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
# recall is the percentage of identified fours of all fours (97 / 98 in this case)
# sum(y_train_4) # for checking the sum of all fours in y_train_4
# precision is correctly identified / all identified
# if I identify 100 objects as apples but only 50 correctly i get a precision of 0.5

# extract y probabilities
y_probas = cross_val_predict(forest_clf, X_train,
                             y_train, cv=3,
                             method="predict_proba")

precisions, recalls, thresholds = skm.precision_recall_curve(y_train==1, y_probas[:,1])
plot_precision_recall_vs_threshold(precisions, recalls, thresholds)

fpr, tpr, thresholds = skm.roc_curve(y_train==1, y_probas[:,1])
# fpr = false positive rate = (1 - true negative rate)
# tpr = true positive rate

# area under the curve
plot_roc_curve(fpr, tpr, "Roc Curve")

# How to implement for my data.
# [ ] improve image segmentation. better selection of organisms. 
#     There must be a better way for this...
#     https://www.upgrad.com/blog/image-segmentation-techniques/
# [ ] organisms must be centered in the image. Otherwise I'm pretty sure
#     random forests will have problems -> no features are generated
# [ ] read: https://benanne.github.io/2015/03/17/plankton.html
# [ ] artificially increase dataset size (see blog post)