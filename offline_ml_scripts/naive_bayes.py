import matplotlib.pyplot as plt
import numpy as np
import sys

from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

DATA_FILE = sys.argv[1]

label_names = []
feat_names = None
y = []
x = []

# read in the data
with open(DATA_FILE) as infile:
    # assume the header is the same in each
    feat_names = infile.readline().strip().split(',')
    # each line is a gesture followed by floats sep'd by commas
    for l in infile:
        parts = l.strip().split(',')
        # just do the dumb simple thing to get label indices
        g = parts[0]
        if g not in label_names:
            label_names.append(g)
        # get our numeric label for the model
        curr_label = label_names.index(g)
        y.append(curr_label)
        x.append([float(v) for v in parts[1:]])

# get into numpy form
y = np.array(y)
x = np.array(x)

# standardize features just this once before all other work
# we don't want individual features being more meaningful due to scale
sscaler = StandardScaler()
x = sscaler.fit_transform(x)

# we'll want to do stratified k-fold CV
# and then evaluate on all k-fold predictions
y_true = np.array([])
y_pred = np.array([])
skf = StratifiedKFold(n_splits=5)
for train_index, test_index in skf.split(x, y):
    x_train, x_test = x[train_index], x[test_index]
    y_train, y_test = y[train_index], y[test_index]
    # do the actual training and classifying for this fold
    print('Fitting model...')
    clf = GaussianNB()
    clf.fit(x_train, y_train)
    curr_pred = clf.predict(x_test)
    # store our true and predicted labels for this fold
    y_true = np.append(y_true, y_test)
    y_pred = np.append(y_pred, curr_pred)

print(y_true)
print(y_pred)

# replace predictions with label names
y_true = np.array([label_names[int(v)] for v in y_true])
y_pred = np.array([label_names[int(v)] for v in y_pred])

#print(y_true)
#print(y_pred)

# grab a confusion matrix for these
cm = confusion_matrix(y_true, y_pred, labels=label_names)
print(cm)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=label_names)
disp.plot()
plt.show()