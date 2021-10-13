import sys
import math
import threading
import multiprocessing
import pickle
import time
import numpy as np

from LayoutManager import LayoutManager

from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

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
    _PROC_POOL = None
    _MODEL = None
    _TEST_THREAD = None
    _DATA_POOL = None
    _INITED = False
    _WINDOW = None

    def initialize(data_pool, window):
        MLResources._INITED = True
        MLResources._PROC_POOL = multiprocessing.Pool()
        MLResources._DATA_POOL = data_pool
        # this is so we can access gui/event stuff
        MLResources._WINDOW = window
        # start the test thread - it just runs and predicts while a model is loaded
        # need the prediction label box of the gui
        MLResources._TEST_THREAD = threading.Thread(target=test_thread_main, args=[], daemon=True)
        MLResources._TEST_THREAD.start()

    def cleanup():
        MLResources._INITED = False
        if MLResources._PROC_POOL is not None:
            MLResources._PROC_POOL.close()
            MLResources._PROC_POOL = None
        MLResources._DATA_POOL = None
        MLResources._MODEL = None
        MLResources._WINDOW = None
        try:
            MLResources._TEST_THREAD.join(timeout=1)
            MLResources._TEST_THREAD = None
        except:
            # daemon should just terminate anyway
            MLResources._TEST_THREAD = None

    def proc_pool():
        return MLResources._PROC_POOL

    def data_pool():
        return MLResources._DATA_POOL

    def load_model(model_fname):
        with open(model_fname, 'r+b') as infile:
            MLResources._MODEL = pickle.load(infile)

    def ml_model():
        return MLResources._MODEL

    def start_training_job(ml_options):
        # spawn a thread to spin off actual process and maintain interface needs
        train_thread = threading.Thread(target=train_thread_main, args=[ml_options], daemon=True)
        train_thread.start()

    def _update_prediction(pred):
        MLResources._WINDOW.write_event_value(LayoutManager.Key.EVT_UPDATE_PREDICTION, pred[0])

    def _disable_train_button(disable):
        MLResources._WINDOW.write_event_value(LayoutManager.Key.EVT_DISABLE_TRAIN_BTN, disable)

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

def process_sample_seq(emg_arr):
    # grab the features
    maa = mean_absolute_amplitude(emg_arr)
    mwl = mean_waveform_length(emg_arr)
    msc = mean_slope_changes(emg_arr)
    mzc = mean_zero_crossings(emg_arr)
    return (maa, mwl, msc, mzc)

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

def convert_to_feat_vectors(gest, emg0, emg1):
    # we need to go through the sequence and process each example
    # each example is a varying-length seq of emg samples
    x = list()
    y = list()
    start_ind = 0
    while start_ind < len(gest):
        curr_gest,curr_emg0,curr_emg1,start_ind = pull_next_sample(gest, emg0, emg1, start_ind)
        feats = process_sample_seq(curr_emg0) + process_sample_seq(curr_emg1)
        # label is the same for all of curr_gest
        y.append(curr_gest[0])
        x.append(feats)
    return np.array(x),np.array(y)

def train_process_main(ml_options):
    # first we need to load in our training data
    gest,emg0,emg1 = read_data_file(ml_options.data_fname)
    # now convert those to features
    x,y = convert_to_feat_vectors(gest, emg0, emg1)
    # need to construct a pipeline for consistent future use
    estimators = []
    # standarize if we're going to
    if ml_options.opt_standardize:
        estimators.append(('standardize', StandardScaler()))
    # pick a predictor
    if ml_options.linearsvc: # choose LinearSVC
        estimators.append(('linear_svm', LinearSVC(max_iter=2000)))
    # and train
    clf = Pipeline(estimators)
    clf.fit(x, y)
    # and pickle that model for later
    with open(ml_options.model_fname, 'w+b') as outfile:
        pickle.dump(clf, file=outfile)

def train_thread_main(ml_options):
    # disable the train button to prevent multiple clicks
    MLResources._disable_train_button(True)
    # start and wait for the process
    res = MLResources.proc_pool().apply_async(func=train_process_main, args=[ml_options])
    res.wait()
    # and re-enable the button
    MLResources._disable_train_button(False)

def predict_cback(result):
    MLResources._update_prediction(result)

def predict_func(clf, emg_data):
    # need to turn emg data into features
    feats = ()
    for e in emg_data:
        feats += process_sample_seq(e)
    label = clf.predict(np.array([list(feats)]))
    return label

def test_thread_main():
    SEC_PER_TICK = 1.0 / 3
    last_predict_time = 0
    # we're going to loop and predict every tick
    while MLResources._INITED:
        curr_time = time.time()
        clf = MLResources.ml_model()
        # do we need to tick
        time_reached = (curr_time - last_predict_time) >= SEC_PER_TICK
        model_loaded = clf is not None
        if time_reached and model_loaded:
            # need to do a prediction
            # grab the predict buffers first
            emg_data = MLResources.data_pool().get_prediction_buffers()
            _ = MLResources.proc_pool().apply_async(func=predict_func, args=[clf, emg_data], callback=predict_cback)
            # update our last tick time
            last_predict_time = curr_time
        # we can sleep for a bit here
        time.sleep(.05)
