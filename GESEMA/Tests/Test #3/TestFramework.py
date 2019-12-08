#!/usr/bin/python
import sys
import os
import subprocess
import time
import statistics
import yaml
import csv


def timing(rep, file, confs, exhaustive):

    results = {"EXHAUSTIVE": {}, "GESEMA": {}}

    writer = open(file.split(".")[0] + "TIMING.csv", "w+")
    writer.write("ALGORITHM;CONF;TIME;STDEV\n")

    if exhaustive:
        timeResults = []
        for test in range(rep):
            start = time.time()
            subprocess.check_call("python3 ExhaustiveMapping.py " + file, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
            timeResults.append(time.time() - start)
        results["EXHAUSTIVE"]["TIME"] = statistics.mean(timeResults)
        results["EXHAUSTIVE"]["STDEV"] = statistics.stdev(timeResults)
        writer.write("EXHAUSTIVE;--;" + str(results["EXHAUSTIVE"]["TIME"]) + ";" + str(results["EXHAUSTIVE"]["STDEV"]) + "\n")

    for execution in confs:
        timeResults = []
        print("TEST: " + file + " || " + execution)
        for test in range(rep):
            start = time.time()
            subprocess.check_call("python3 GeneticMapping.py " + file + " " + execution, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
            timeResults.append(time.time() - start)

        timeResults.sort()
        outliers = len(timeResults) // 20
        print(len(timeResults))
        if outliers > 0:
            timeResults = timeResults[outliers:][:len(timeResults)-2*outliers]
        print(len(timeResults))
        results["GESEMA"][execution] = {}
        results["GESEMA"][execution]["TIME"] = statistics.mean(timeResults)
        results["GESEMA"][execution]["STDEV"] = statistics.stdev(timeResults)
        writer.write("GESEMA;" + execution + ";" + str(results["GESEMA"][execution]["TIME"]) + ";" + str(results["GESEMA"][execution]["STDEV"]) + "\n")

    writer.close()
    return results


def quality(rep, file, confs, mode):

    results = {}

    writer = open(file.split(".")[0] + "QUALITY.csv", "w+")
    writer.write("ALGORITHM;CONF;MEAN_RESULTS;STDEV_RESULTS;EXH_PARETO;MEAN_PARETO;STDEV_PARETO;REL_PARETO;REL_PARETO_WC\n")

    subprocess.check_call("python3 ExhaustiveMapping.py " + file + " -o parameter.csv " + mode, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
    exhaustiveFile = open("parameter.csv", "r")
    exhaustiveReader = csv.reader(exhaustiveFile, delimiter=';')
    exhaustiveData = [distribution for distribution in exhaustiveReader]
    exhaustiveFile.close()
    exhaustiveDists = [distribution[0] for distribution in exhaustiveData]
    exhaustiveDists.pop()
    pfCandidates = int(exhaustiveData[-1][1])
    exhaustiveFronts = [distribution[-1] for distribution in exhaustiveData]


    for execution in confs:
        generalFronts = []
        realPareto = []
        quantityFronts = []
        for test in range(rep):
            analyzerFronts = []
            subprocess.check_call("python3 GeneticMapping.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
            analyzerFile = open("output.csv", "r")
            analyzerReader = csv.reader(analyzerFile, delimiter=';')
            analyzerData = [distribution[0] for distribution in analyzerReader]
            analyzerData.remove('MAPPING')
            analyzerFile.close()

            for distribution in analyzerData:
                analyzerFronts.append(exhaustiveFronts[exhaustiveDists.index(distribution)])

            generalFronts = generalFronts + analyzerFronts
            realPareto.append(analyzerFronts.count('0'))
            quantityFronts.append(len(analyzerFronts))
            os.remove("output.csv")

        writer.write("GESEMA;" + execution + ";" + str(statistics.mean(quantityFronts)) + ";" + str(statistics.stdev(quantityFronts)) + ";" + str(pfCandidates) + ";" + str(statistics.mean(realPareto)) + ";" + str(statistics.stdev(realPareto)) + ";" + str(statistics.mean(realPareto)/pfCandidates) + ";" + str((statistics.mean(realPareto) - statistics.stdev(realPareto))/pfCandidates) + "\n")

    os.remove("parameter.csv")
    writer.close()


if len(sys.argv) < 5 or (sys.argv[1] == "-t" and len(sys.argv) < 6):
    print("USAGE: *.py -t -e|-ne ROUNDS FILE [LIST OF CONFIGURATIONS]")
    print("USAGE: *.py -q -i|-f ROUNDS FILE [LIST OF CONFIGURATIONS]")
    exit()

if not sys.argv[3].isdigit():
    print("ERROR: INVALID NUMBER OF ROUNDS")
    exit()

if not os.path.isfile(sys.argv[4]):
    print("ERROR: INVALID FILE (" + sys.argv[4] + ")")
    exit()

if sys.argv[1] == "-t":
    if sys.argv[2] == "-e":
        timing(int(sys.argv[3]), sys.argv[4], sys.argv[5:], True)
    elif sys.argv[2] == "-ne":
        timing(int(sys.argv[3]), sys.argv[4], sys.argv[5:], False)
    else:
        print("ERROR: INVALID FLAG " + sys.argv[2])
elif sys.argv[1] == "-q":
    if sys.argv[2] in ["-i", "-f"]:
        quality(int(sys.argv[3]), sys.argv[4], sys.argv[5:], sys.argv[2])
    else:
        print("ERROR: INVALID FLAG " + sys.argv[2])
else:
    print("ERROR: INVALID FLAG " + sys.argv[1])
