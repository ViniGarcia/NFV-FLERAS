import csv
import statistics

final_result = []
f_in = open("final.csv", "w+")

with open('output.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=";")
	result = [[] for _ in range(12)]
	names = []
	for index,row in enumerate(csv_reader):
		print(index, row)
		if index % 13 == 0:
			continue
		result[(index % 13) - 1].append(float(row[3]))
		if index < 13: 
			names.append(row[0])

	for element in result:
		final_result.append((statistics.mean(element), statistics.stdev(element)))

	print("file;mean;stdev")
	f_in.write("file;mean;stdev\n")
	for index in range(12):
		print(str(names[index]) + ";" + str(final_result[index][0]) + ";" + str(final_result[index][1]))
		f_in.write(str(names[index]) + ";" + str(final_result[index][0]) + ";" + str(final_result[index][1]) + "\n")
		
f_in.close()
