import sys
import math
import threading
import multiprocessing
import pickle
import numpy as np

from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler

class MLOptions:

    def __init__(self, data_fname, model_fname):
        # filenames for read and write
        self.data_fname = data_fname
        self.model_fname = model_fname
        # classifier type
        self.clf_linearsvc = True
        # processing options
        self.opt_standardize = True

    def linearsvc(self):
        self.clf_linearsvc = True
        # set other classifier options false here

    def set_standardize(self, onoff):
        self.opt_standardize = onoff

# dumb global for now
class MLResources:
    _POOL = None
    _MODEL = None

    def cleanup():
        if MLResources._POOL is not None:
            MLResources._POOL.close()
            MLResources._POOL = None

    def initialize():
        MLResources._POOL = multiprocessing.Pool()

    def proc_pool():
        return MLResources._POOL

    def load_model(model_fname):
        with open(model_fname, 'r+b') as infile:
            MLResources._MODEL = pickle.load(infile)

    def ml_model():
        return MLResources._MODEL

    def start_training_job(ml_options, train_btn):
        # spawn a thread to spin off actual process and maintain interface needs
        train_thread = threading.Thread(target=train_thread_main, args=[ml_options, train_btn], daemon=True)
        train_thread.start()

def pull_next_sample(gest_arr, emg0_arr, emg1_arr, start_ind):
    N = len(gest_arr)
    if start_ind >= N:
        return None,None,None,-1
    curr_gest = gest_arr[start_ind]
    end_ind = start_ind + 1
    while end_ind < N and gest_arr[end_ind] == curr_gest:
        end_ind += 1
    return gest_arr[start_ind:end_ind], emg0_arr[start_ind:end_ind], emg1_arr[start_ind:end_ind], end_ind

def mean_absolute_amplitude(arr):
    ret = 0
    for el in arr:
        ret += abs(el)
    return ret / len(arr)

def mean_waveform_length(arr):
    ret = 0
    for i in range(1, len(arr)):
        ret += abs(arr[i] - arr[i-1])
    return ret / len(arr)

def mean_slope_changes(arr):
    sc_cnt = 0
    for i in range(1, len(arr) - 1):
        slp1 = arr[i] - arr[i-1]
        slp2 = arr[i+1] - arr[i]
        # no sign function, use copysign with 1
        if math.copysign(1, slp1) != math.copysign(1, slp2):
            sc_cnt += 1
    return sc_cnt / len(arr)

def mean_zero_crossings(arr):
    zc_cnt = 0
    for i in range(1, len(arr)):
        # no sign function, use copysign with 1
        if math.copysign(1, arr[i]) != math.copysign(1, arr[i-1]):
            zc_cnt += 1
    return zc_cnt / len(arr)

def process_sample_seq(gest_arr, emg0_arr, emg1_arr):
    g = gest_arr[0] # these are all the same value
    # now grab the features for emg0
    maa0 = mean_absolute_amplitude(emg0_arr)
    mwl0 = mean_waveform_length(emg0_arr)
    msc0 = mean_slope_changes(emg0_arr)
    mzc0 = mean_zero_crossings(emg0_arr)
    # and the features for emg1
    maa1 = mean_absolute_amplitude(emg1_arr)
    mwl1 = mean_waveform_length(emg1_arr)
    msc1 = mean_slope_changes(emg1_arr)
    mzc1 = mean_zero_crossings(emg1_arr)
    return (g, maa0, mwl0, msc0, mzc0, maa1, mwl1, msc1, mzc1)

def read_data_file(fname):
    gest = list()
    emg0 = list()
    emg1 = list()
    with open(fname) as infile:
        # strip the header
        header = infile.readline().strip().split(',')
        gest_ind = header.index('label')
        emg0_ind = header.index('emg_0')
        emg1_ind = header.index('emg_1')
        # and pull each line
        for l in infile:
            parts = l.strip().split(',')
            gest.append(parts[gest_ind])
            emg0.append(float(parts[emg0_ind]))
            emg1.append(float(parts[emg1_ind]))
    return (gest,emg0,emg1)

def standardize_data(x):
    sscaler = StandardScaler()
    x = sscaler.fit_transform(x)
    return x

def train_linear_svc(x, y):
    # fit the model
    clf = LinearSVC()
    clf.fit(x, y)
    return clf

def convert_to_feat_vectors(gest, emg0, emg1):
    # we need to go through the sequence and process each example
    # each example is a varying-length seq of emg samples
    x = list()
    y = list()
    start_ind = 0
    while start_ind < len(gest):
        curr_gest,curr_emg0,curr_emg1,start_ind = pull_next_sample(gest, emg0, emg1, start_ind)
        label_feats = process_sample_seq(curr_gest, curr_emg0, curr_emg1)
        # label is the first element
        y.append(label_feats[0])
        x.append(label_feats[1:])
    return np.array(x),np.array(y)

def train_process_main(ml_options):
    # first we need to load in our training data
    gest,emg0,emg1 = read_data_file(ml_options.data_fname)
    # now convert those to features
    x,y = convert_to_feat_vectors(gest, emg0, emg1)
    # standarize if we're going to
    if ml_options.opt_standardize:
        x = standardize_data(x)
    # train a model with those
    clf = None
    if ml_options.linearsvc: # choose LinearSVC
        clf = train_linear_svc(x, y)
    # and pickle that model for later
    with open(ml_options.model_fname, 'w+b') as outfile:
        pickle.dump(clf, file=outfile)

def train_thread_main(ml_options, train_btn):
    # disable the train button to prevent multiple clicks
    train_btn.update(disabled=True)
    # start and wait for the process
    res = MLResources.proc_pool().apply_async(func=train_process_main, args=[ml_options])
    res.wait()
    # and re-enable the button
    train_btn.update(disabled=False)
