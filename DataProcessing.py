import matplotlib

import mne
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from scipy.signal import butter, lfilter, freqz
from PIL import Image
import re

#below is filter stuff
#derived from http://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_bandpass(lowcutoff, highcutoff, fs, order=5):
    nyq = 0.5 * fs
    low_normal_cutoff = lowcutoff / nyq
    high_normal_cutoff = highcutoff / nyq
    b, a = butter(order, [low_normal_cutoff, high_normal_cutoff], btype='bandpass', analog=False)
    return b, a

def butter_bandpass_filter(data, lowcutoff, highcutoff, fs, order=5):
    b, a = butter_bandpass(lowcutoff, highcutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def convertSpikesStructureToLinearForm(spikesstructure):
    """converts a spikesStructure which identifies spikes "detected" on each
    channel into a simple array of sample nos where spikes were detected"""
    spikeSet = set()
    for arr in spikesstructure:
        for item in arr:
            spikeSet.add(item)
    out = list(spikeSet)
    out.sort()
    return out

def stupidIdentifySpikes(data, spikekernellength=128, cutoff=0.0133):
    thekernel = sp.signal.morlet(spikekernellength)
    #[CB 9/5/2015] So this kernel is only for "detecting" spikes of a given format.
    #a.k.a. it sucks.

    #plt.plot(thekernel)
    #plt.show()
    #ldata2, times2 = data[2:20:3, start:stop]

    accumulator = []
    for arr in data:
        correlated = sp.signal.correlate(arr, thekernel)
        accumulator.append(correlated)
    accumulated = np.vstack(accumulator)

    #for arr in accumulated:
    #    plt.plot(arr)
    #plt.show()

    spikesout = []
    for i in range(0, len(accumulated)):
        spikesout.append([])
        for i2 in range(0, len(accumulated[i])):
            if(accumulated[i][i2]>=cutoff):
                spikesout[i].append(i2)
    return spikesout

def amplitude_adjust_data(dataSeries, amplitudeFactor):
    out = map(lambda x: x*amplitudeFactor, dataSeries)

def getDisplayData(realData, start_time, end_time, amplitude_adjust, lowpass, highpass, channels=range(1,15)):
    """given some real EEG data, getDisplayData processes it in a way that is useful for display
      purposes and returns the results"""
    start, stop = realData.time_as_index([start_time, end_time])
    ldata, ltimes = realData[channels, start:stop]
    #spikesStructure = stupidIdentifySpikes(ldata, cutoff=0.0005)
    #linSpikes = convertSpikesStructureToLinearForm(spikesStructure)
    #avgdata = np.average(np.array(ldata),0)
    ldata2 = map(lambda x: amplitude_adjust*butter_bandpass_filter(x,lowpass,highpass,256), ldata)
    return (ldata2,ltimes)

def load_raw_annotations(rawAnnotationsPath):
    myfile = open(rawAnnotationsPath, 'r')
    startFound = False
    annotations = []
    for line in myfile:
        if not startFound:
            if re.match('\s*Time\s+Duration\s+Title', line) != None:
                startFound = True
        else:
            #note this assumes there is no duration in the file
            matches = re.match('(\d*):(\d*):(\d*)  \t\t(.*)', line)
            #print matches.groups()
            entry = ((int(matches.group(1)),int(matches.group(2)),int(matches.group(3))), None , matches.group(4))
            annotations.append(entry)
    myfile.close()
    return annotations

# truth is (time,duration,title)
# predictions is [time]
#  time is (hour, minute, second)
# returns (truePositives, falsePositives, falseNegatives)
def score_predictions(truth, predictions):
    spikeList = [] #tuple of (time, duration)
    for time,duration,title in truth:
        if title == 'spike':
            if duration is None: duration = (0,0,1)
            spikeList.append((time, duration))
    numSpikes = len(spikeList)
    numPredictions = len(predictions)
    numCorrect = 0
    for (spikehr,spikemin,spikesec),spikedur in spikeList:
        spiketime = (spikehr * 3600) + (spikemin * 60) + spikesec
        found = False
        for pred in predictions:
            predtime = (pred[0] * 3600) + (pred[1] * 60) + pred[2]
            if (spiketime+spikedur >= predtime and spiketime-spikedur <= predtime):
                found = True
                break
        if found:
            numCorrect += 1
    return (numCorrect, numPredictions - numCorrect, numSpikes - numCorrect)
