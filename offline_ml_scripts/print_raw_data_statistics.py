import sys

def avg(arr):
    return round(sum(arr) / (1.0 * len(arr)), ndigits=1)

def pull_next_sample(gest_arr, emg0_arr, emg1_arr, start_ind):
    N = len(gest_arr)
    if start_ind >= N:
        return None,None,None,-1
    curr_gest = gest_arr[start_ind]
    end_ind = start_ind + 1
    while end_ind < N and gest_arr[end_ind] == curr_gest:
        end_ind += 1
    return gest_arr[start_ind:end_ind], emg0_arr[start_ind:end_ind], emg1_arr[start_ind:end_ind], end_ind

def process_sample_seq(gest_arr, emg0_arr, emg1_arr, lengths):
    g = gest_arr[0] # same gesture for the whole array
    # make sure the current gesture has been seen
    if g not in lengths:
        lengths[g] = list()
    lengths[g].append(len(gest_arr))

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
lengths = dict()
start_ind = 0
while start_ind < len(gest):
    curr_gest, curr_emg0, curr_emg1, start_ind = pull_next_sample(gest, emg0, emg1, start_ind)
    process_sample_seq(curr_gest, curr_emg0, curr_emg1, lengths)

fmt = '={0}=\t  count: {1}\tmin: {2}\tmax: {3}\tavg: {4}'
for g in lengths.keys():
    gn = len(lengths[g])
    gmin = min(lengths[g])
    gmax = max(lengths[g])
    gavg = avg(lengths[g])
    print(fmt.format(g, gn, gmin, gmax, gavg))