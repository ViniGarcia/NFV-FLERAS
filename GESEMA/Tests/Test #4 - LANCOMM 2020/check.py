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

def check(files, metrics, f_in):

	results = [[]] * (metrics + 1)
	individual = [[],[],[]]

	for name in files:
		openFile = open(name, "r")
		openData = csv.reader(openFile, delimiter=';')
		openData = [distribution for distribution in openData]
		openFile.close()

		steps = [distribution[-2] for distribution in openData]
		remove = steps.count('0') + 1
		openData = openData[remove:]

		openDist = [distribution[0] for distribution in openData]
		individual[0].append(openDist)
		results[0] = results[0] + openDist

		for mtc in range(metrics):
			openMtc = [distribution[mtc+1] for distribution in openData]
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

		if len(individual[1][-1]) > 1:
			individual[2].append((max(individual[1][-1]), min(individual[1][-1]), statistics.mean(individual[1][-1]), statistics.stdev(individual[1][-1])))
		else:
			individual[2].append((max(individual[1][-1]), min(individual[1][-1]), statistics.mean(individual[1][-1]), 0))

	print(files)
	for index in range(len(files)):
		f_in.write(files[index] + ";" + str(individual[2][index][0]) + ";" + str(individual[2][index][1]) + ";" + str(individual[2][index][2]) + ";" + str(individual[2][index][3]) + "\n")
		print(files[index] + ";" + str(individual[2][index][0]) + ";" + str(individual[2][index][1]) + ";" + str(individual[2][index][2]) + ";" + str(individual[2][index][3]))



f_in = open("output.csv", "a+")
f_in.write("File;Internal;External;Mean;StdDev\n")
print("File;Internal;External;Mean;StdDev")
#print("0 (No node changes)->")
check(["output_fm_0.csv", "output_df_0.csv"], 2, f_in)
#print("1 (One node change per round) ->")
check(["output_fm_1.csv", "output_df_1.csv"], 2, f_in)
#print("2 (Two nodes change per round) ->")
check(["output_fm_2.csv", "output_df_2.csv"], 2, f_in)
#print("3 (Three nodes change per round) ->")
check(["output_fm_3.csv", "output_df_3.csv"], 2, f_in)
#print("4 (Four nodes change per round) ->")
check(["output_fm_4.csv", "output_df_4.csv"], 2, f_in)
#print("5 (Five nodes change per round) ->")
check(["output_fm_5.csv", "output_df_5.csv"], 2, f_in)
f_in.close()