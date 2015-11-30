# Takes in input as the list of lists and
# outputs a list of indices for each channel
# based on the spike frequency range of 20ms-70ms
def frequencyFinder(inputList):
    minSpikeFrequency = 14.25
    maxSpikeFrequency = 51
    indices = [[] for x in range(len(inputList))]
    for channel in inputList:
        for freq in range(len(channel)):
            if (channel[freq] < maxSpikeFrequency and channel[freq] > minSpikeFrequency):
                indices[inputList.index(channel)].append(freq)
    return indices

# Helper function for peakSpikeFinder
def peakFinder(inputList):
    indices = [[] for x in range(len(inputList))]
    chanelNum = 0;
    for channel in inputList:
        current = 1
        while (current < len(channel)-2):
            if (channel[current] > channel[current-1] and channel[current] < channel[current+1]):
                indices[chanelNum].append(current)
        channelNum += 1
    return indices

# Returns a list of indices, which are peaks, and have
# fields in the channel above abd the channel below,
# based on a referential montage
def peakSpikeFinder(inputList):
    indices = peakFinder(inputList)
    spikes = indices
    for i in range(1, len(indices)):
        for k in range(len(indices[i])):
            if (indices[i][k] in indices[i-1] and indices[i][k] in indices[i+1]):
                continue
            else:
            	spikes[i].pop(k)
    return indices

# Main function. Call with list of list of frequencies
# Returns a list of list of indices with detected spikes.
def spikeFinder(inputList):
	frequencyBasedSpikes = frequencyFinder(inputList)
	fieldBasedSpikes = peakSpikeFinder(inputList)
	indices = [[] for x in range(len(inputList))]
	for channel in range(len(inputList)):
		for i in range(len(inputList[channel])):
			if (i in frequencyBasedSpikes[channel] and i in fieldBasedSpikes[channel]):
				indices[channel].append(i)
	return indices

