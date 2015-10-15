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
    """demonstrates lowpass filter"""
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
    """demonstrates bandpass filter"""
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

def dostuff():
    """demonstrates displaying data, and showing spike line"""
    data = mne.io.read_raw_edf("../EEGDATA/CAPSTONE_AB/BASHAREE_TEST.edf",preload=True)
    start, stop = data.time_as_index([100, 200])
    ldata, ltimes = data[2:8, start:stop]
    spikesStructure = stupidIdentifySpikes(ldata, cutoff=0.0005)
    linSpikes = convertSpikesStructureToLinearForm(spikesStructure)
    print linSpikes
    for arr in ldata:
        plt.plot(arr)
    for spike in linSpikes:
        plt.axvline(spike, color='k')
    plt.show()

# def show_data(start_time, end_time, amplitude_adjust, lowpass ,highpass):

# t = np.arange(0, len(data))
# ticklocs = []
# ax = plt.subplot(212)
# plt.xlim(0,10)
# plt.xticks(np.arange(10))
# dmin = data.min()
# dmax = data.max()
# dr = (dmax - dmin)*0.7 # Crowd them a bit.
# y0 = dmin
# y1 = (47-1) * dr + dmax
# plt.ylim(y0, y1)

# segs = []
# for i in range(47):
#     segs.append(np.hstack((t[:,np.newaxis], data[:,i,np.newaxis])))
#     ticklocs.append(i*dr)

# offsets = np.zeros((numRows,2), dtype=float)
# offsets[:,1] = ticklocs

# lines = LineCollection(segs, offsets=offsets,
#                        transOffset=None,
#                        )

# ax.add_collection(lines)

# # set the yticks to use axes coords on the y axis
# ax.set_yticks(ticklocs)
# ax.set_yticklabels(['PG3', 'PG5', 'PG7', 'PG9'])

# xlabel('time (s)')

# reads annotation data from disk to and creates tuples of the data
# returns list of (time, duration, title) 
#  time is (hour, minute, second)


#data = mne.io.read_raw_edf("../EEGDATA/CAPSTONE_AB/BASHAREE_TEST.edf",preload=True)
