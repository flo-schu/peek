from matplotlib import pyplot as plt

def plot_roc_curve(fpr, tpr, label=None):
    plt.plot(fpr, tpr, linewidth=2, label=label)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([0, 1, 0, 1])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')

def plot_precision_recall_vs_threshold(precisions, recalls, thresholds):
    plt.plot(thresholds, precisions[:-1], "b--", label="Precision")
    plt.plot(thresholds, recalls[:-1], "g-", label="Recall")
    plt.xlabel("Threshold")
    plt.legend(loc="upper right")
    plt.ylim([0, 1.05])
    plt.show()
    
def plot_precision_vs_recall(precisions, recalls):
    plt.plot(precisions, recalls, "b--", label="Precision")
    plt.xlabel("Precision")
    plt.ylabel("Recall")
    plt.legend(loc="upper left")
    plt.show()