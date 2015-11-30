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

def peakSpikeFinder(inputList):
	indices = peakFinder(inputList)
	spikes = {}
	for i in range(1, len(indices)):
		for k in indices[i]:
			if (k in indices[i-1] and k in indices[i+1]):
				spikes[i] = k

def frequencyFinder(inputList):
	indices = [[] for x in range(len(inputList))]
	for channel in inputList:
		for freq in range(len(channel)):
			if (channel[freq] < maxSpikeFrequency and channel[freq] > minSpikeFrequency):
				indices[inputList.index(channel)].append(freq)
	return indices