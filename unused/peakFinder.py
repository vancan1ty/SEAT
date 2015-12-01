import random
import time
# Takes in input as the list of lists and
# outputs a list of indices for each channel
# based on the spike frequency range of 20ms-70ms
def frequencyFinder(inputList):
    minSpikeFrequency = 14.25
    maxSpikeFrequency = 51
    indices = [[] for x in range(len(inputList))]
    for channel in inputList:
        print inputList.index(channel)
        for freq in range(len(channel)):
            if (channel[freq] < maxSpikeFrequency and channel[freq] > minSpikeFrequency):
                indices[inputList.index(channel)].append(freq)
    print "Freq done"
    return indices

# Helper function for peakSpikeFinder
def peakFinder(inputList):
    indices = [[] for x in range(len(inputList))]
    channelNum = 0;
    for channel in inputList:
        current = 1
        print inputList.index(channel)
        while (current < len(channel)-2):
            if (channel[current] > channel[current-1] and channel[current] < channel[current+1]):
                indices[channelNum].append(current)
            current += 1
        channelNum += 1
    print "Helper done"
    return indices

# Returns a list of indices, which are peaks, and have
# fields in the channel above abd the channel below,
# based on a referential montage
def peakSpikeFinder(inputList):
    indices = peakFinder(inputList)
    spikes = indices
    for i in range(1, len(indices)-1):
        print i
        for k in range(len(indices[i])):
            try:
                if (indices[i][k] in indices[i-1] and indices[i][k] in indices[i+1]):
                    continue
                else:
                    spikes[i].pop(k)
            except:
                continue
    print "Field done"
    return indices

# Main function. Call with list of list of frequencies
# Returns a list of list of indices with detected spikes.
def spikeFinder(inputList):
    frequencyBasedSpikes = frequencyFinder(inputList)
    fieldBasedSpikes = peakSpikeFinder(inputList)
    indices = [[] for x in range(len(inputList))]
    for channel in range(len(inputList)):
        print channel
        for i in range(len(inputList[channel])):
            if (i in frequencyBasedSpikes[channel] and i in fieldBasedSpikes[channel]):
                indices[channel].append(i)
    print "Main done"
    return indices

def randomLists():
	randomLists = [[] for x in range(8)]
	for k in randomLists:
	    for x in range(1000):
	        randomNum = random.random()
	        randomNum = 100*randomNum
	        k.append(int(randomNum))

	something = spikeFinder(randomLists)
	time.sleep(10)
	return something
