import matplotlib

matplotlib.use('TkAgg')
#[CB 9/5/2015] Note the above line is basically for my windows setup.
#everything is screwy in windows.  In mac or linux, you could probably remove it.
import mne
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from scipy.signal import butter, lfilter, freqz
from PIL import Image

data = mne.io.read_raw_edf("../EEGDATA/CAPSTONE_AB/BASHAREE_TEST.edf",preload=True)
#data.plot()

thekernel = sp.signal.morlet(128)
plt.plot(thekernel)
plt.show()

#start, stop = data.time_as_index([100, 200])
#ldata, ltimes = data[:, start:stop]
#ldata2, times2 = data[2:20:3, start:stop]

#plt.plot([1,5,4])
#plt.plot([3,4,3])
#plt.show()

accumulator = []
for arr in ldata:
    convolved = sp.signal.correlate(arr, thekernel)
    accumulator.append(convolved)
accumulated = np.vstack(accumulator)

for arr in ldata:
    plt.plot(arr)
plt.show()

for arr in accumulated:
    plt.plot(arr)
plt.show()

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

doplot = False
counter = 0;
def myshow():
   """this function is intended to work around the limitations of CB's python setup
     which doesn't work properly with matplotlib interactive mode.  depending on doplot
     this either calls plt.show() or plt.savefig()"""
   global counter
   if (doplot):
       plt.show()
   else:
       fname = "figures/figure"+str(counter)+".png"
       plt.savefig(fname)
       im = Image.open(fname)
       im.show()
       counter=counter+1

def lowpass_stuff():
    # Filter requirements.
    order = 6
    fs = 1024       # sample rate, Hz
    cutoff = 4 # desired cutoff frequency of the filter, Hz

    # Get the filter coefficients so we can check its frequency response.
    b, a = butter_lowpass(cutoff, fs, order)

    # Plot the frequency response.
    w, h = freqz(b, a, worN=8000)
    plt.subplot(2, 1, 1)
    plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
    plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
    plt.axvline(cutoff, color='k')
    plt.xlim(0, 0.5*fs)
    plt.title("Lowpass Filter Frequency Response")
    plt.xlabel('Frequency [Hz]')
    plt.grid()

    # Demonstrate the use of the filter.
    # First make some data to be filtered.
    T = 5.0         # seconds
    n = int(T * fs) # total number of samples
    t = np.linspace(0, T, n, endpoint=False)
    # "Noisy" data.  We want to recover the 1.2 Hz signal from this.
    data = np.sin(1.2*2*np.pi*t) + 1.5*np.cos(9*2*np.pi*t) + 0.5*np.sin(12.0*2*np.pi*t)

    # Filter the data, and plot both the original and filtered signals.
    y = butter_lowpass_filter(data, cutoff, fs, order)

    plt.subplot(2, 1, 2)
    plt.plot(t, data, 'b-', label='data')
    plt.plot(t, y, 'g-', linewidth=2, label='filtered data')
    plt.xlabel('Time [sec]')
    plt.grid()
    plt.legend()

    plt.subplots_adjust(hspace=0.35)
    myshow()

def bandpass_stuff():
    # Filter requirements.
    order = 6
    fs = 1024       # sample rate, Hz
    lowcutoff = 20 # desired cutoff frequency of the filter, Hz
    highcutoff = 80 # high cutoff

    # Get the filter coefficients so we can check its frequency response.
    b, a = butter_bandpass(lowcutoff, highcutoff, fs, order)

    # Plot the frequency response.
    w, h = freqz(b, a, worN=8000)
    plt.subplot(2, 1, 1)
    plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
    plt.plot(lowcutoff, 0.5*np.sqrt(2), 'ko')
    plt.plot(highcutoff, 0.5*np.sqrt(2), 'ko')
    plt.axvline(lowcutoff, color='k')
    plt.axvline(highcutoff, color='k')
    plt.xlim(0, 0.5*fs)
    plt.title("Bandpass Filter Frequency Response")
    plt.xlabel('Frequency [Hz]')
    plt.grid()
    myshow()

lowpass_stuff()
