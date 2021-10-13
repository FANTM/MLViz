import sys
import math

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

feat_names = ['label', 'maa0', 'mwl0', 'msc0', 'mzc0', 'maa1', 'mwl1', 'msc1', 'mzc1']
feat_fmt = '{0},{1},{2},{3},{4},{5},{6},{7},{8}'
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
    return feat_fmt.format(g, maa0, mwl0, msc0, mzc0, maa1, mwl1, msc1, mzc1)

# read in processed data from the two sensors
DATA_FILE = sys.argv[1]
gest = list()
emg0 = list()
emg1 = list()
with open(DATA_FILE) as infile:
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

# now go through the sequence and process each sample sequence
print(feat_fmt.format(*feat_names))
start_ind = 0
while start_ind < len(gest):
    curr_gest, curr_emg0, curr_emg1, start_ind = pull_next_sample(gest, emg0, emg1, start_ind)
    to_print = process_sample_seq(curr_gest, curr_emg0, curr_emg1)
    print(to_print)