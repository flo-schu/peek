import numpy as np
from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import matplotlib.cm as cm

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
y_train_4 = (y_train == 4) 
y_test_4 = (y_test == 4)

from sklearn.linear_model import SGDClassifier
sgd_clf = SGDClassifier(random_state=42) # instantiate
sgd_clf.fit(X_train, y_train_4) # train the classifier
sgd_clf.predict([some_digit]) # make it predict some digit

# show some results
for index in range(0, X.shape[0], 10):
    digit = X[index]
    predicted = sgd_clf.predict([digit])
    if predicted:
        print("{} == {}".format(predicted, y[index]), end="\n")


from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix, precision_score, recall_score, precision_recall_curve, f1_score

y_train_pred = cross_val_predict(sgd_clf, X_train, y_train_4, cv=3)

confusion_matrix(y_train_4, y_train_pred, labels=[True, False])
# interpretation
#               predicted
#             | 4  | Not 4 |
#       --------------------
# True     4  | 97 |    1  |  98
# True  not 4 |  2 |  900  | 902
#       --------------------
#               99    901

recall_score(y_true=y_train_4, y_pred=y_train_pred)
# is the percentage of identified fours of all fours (97 / 98 in this case)
# sum(y_train_4) # for checking the sum of all fours in y_train_4

precision_score(y_true=y_train_4, y_pred=y_train_pred)
# is correctly identified / all identified
# if I identify 100 objects as apples but only 50 correctly i get a precision of 0.5


f1_score(y_train_4, y_train_pred)
# harmonic mean from precision and recall

y_scores = cross_val_predict(sgd_clf, X_train, y_train_4, cv=3, method="decision_function")

def plot_precision_recall_vs_threshold(precisions, recalls, thresholds):
    plt.plot(thresholds, precisions[:-1], "b--", label="Precision")
    plt.plot(thresholds, recalls[:-1], "g-", label="Recall")
    plt.xlabel("Threshold")
    plt.legend(loc="upper right")
    plt.ylim([0, 1.05])
    plt.show()

precisions, recalls, thresholds = precision_recall_curve(y_train_4, y_scores)

plot_precision_recall_vs_threshold(precisions, recalls, thresholds)

# now I can identify the ideal threshold value (from my decision function)
# for optimizing recall and precision

# returns the score of a digit
sgd_clf.decision_function([some_digit])



plt.plot(precisions, recalls, "b--", label="Precision")
plt.xlabel("Precision")
plt.ylabel("Recall")
plt.legend(loc="upper left")
plt.show()

y_train_pred_90 = (y_scores > -600)
precision_score(y_train_4, y_train_pred_90)
recall_score(y_train_4, y_train_pred_90)

from sklearn.metrics import roc_curve

fpr, tpr, thresholds = roc_curve(y_train_4, y_scores)
# fpr = false positive rate = (1 - true negative rate)
# tpr = true positive rate

def plot_roc_curve(fpr, tpr, label=None):
    plt.plot(fpr, tpr, linewidth=2, label=label)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([0, 1, 0, 1])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    
plot_roc_curve(fpr, tpr, "Roc Curve")
plt.show()

from sklearn.metrics import roc_auc_score
roc_auc_score(y_train_4, y_scores)
# area under the curve

## RANDOM FORESTS

from sklearn.ensemble import RandomForestClassifier
forest_clf = RandomForestClassifier(random_state=42)
y_probas_forest = cross_val_predict(forest_clf, X_train,
                                    y_train_4, cv=3,
                                    method="predict_proba")
y_probas_forest

y_scores_forest = y_probas_forest[:, 1] 

fpr_forest, tpr_forest, thresholds_forest = roc_curve(y_train_4, y_scores_forest)
plot_precision_recall_vs_threshold(*precision_recall_curve(y_train_4, y_scores_forest))

plt.plot(fpr, tpr, "b:", label="SGD")
plot_roc_curve(fpr_forest, tpr_forest, "Random Forest")
plt.legend(loc="lower right")
plt.show()