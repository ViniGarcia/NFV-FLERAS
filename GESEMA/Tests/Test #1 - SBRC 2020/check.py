import csv
import numpy
import statistics

def paretoIndexes(aggregations):

		aggregations = numpy.array(aggregations)
		i_dominates_j = numpy.all(aggregations[:,None] >= aggregations, axis=-1) & numpy.any(aggregations[:,None] > aggregations, axis=-1)
		remaining = numpy.arange(len(aggregations))
		fronts = numpy.empty(len(aggregations), int)
		frontier_index = 0

		while remaining.size > 0:
			dominated = numpy.any(i_dominates_j[remaining[:,None], remaining], axis=0)
			fronts[remaining[~dominated]] = frontier_index
			remaining = remaining[dominated]
			frontier_index += 1

		return fronts.tolist()

def check(files, metrics):

	results = [[]] * (metrics + 1)
	individual = [[],[],[]]


	for name in files:
		openFile = open(name, "r")
		openData = csv.reader(openFile, delimiter=';')
		openData = [distribution for distribution in openData]
		openFile.close()
		openDist = [distribution[0] for distribution in openData]
		openDist.pop(0)

		individual[0].append(openDist)
		results[0] = results[0] + openDist

		for mtc in range(metrics):
			openMtc = [distribution[mtc+1] for distribution in openData]
			openMtc.pop(0)

			results[mtc+1] = results[mtc+1] + openMtc

	aggregations = []
	for index in range(len(results[1])):
		candidate = []
		for mtc in range(metrics):
			candidate.append(results[mtc+1][index])
		aggregations.append(candidate)

	results.append(paretoIndexes(aggregations))

	for file in individual[0]:
		individual[1].append([])

		for dist in file:
			i = results[0].index(dist)
			individual[1][-1].append(results[-1][i])

		individual[2].append((max(individual[1][-1]), min(individual[1][-1]), statistics.mean(individual[1][-1]), statistics.stdev(individual[1][-1])))

	print(individual[2])


check(["output1x500.csv", "output2x500.csv", "output3x500.csv"], 2)
check(["output1x1000.csv", "output2x1000.csv", "output3x1000.csv"], 2)
check(["output1x1500.csv", "output2x1500.csv", "output3x1500.csv"], 2)
check(["output1x2000.csv", "output2x2000.csv", "output3x2000.csv"], 2)