#!/usr/bin/python
import sys
import os
import subprocess
import time
import statistics
import yaml
import csv

globalAlgorithms = {"-g":"GESEMA", "-e":"Exhaustive", "-rg":"RandomGreedy"}


def timing(rep, file, confs, modes):

    results = {}

    writer = open(file.split(".")[0] + "TIMING.csv", "w+")
    writer.write("ALGORITHM;CONF;TIME;STDEV\n")

    for request in modes:
        results[globalAlgorithms[request]] = {}
        for execution in confs[modes.index(request)]:
            timeResults = []
            print("TIMING TEST: " + file + " || " + str(globalAlgorithms[request]) + " (" + execution + ")")
            for test in range(rep):
                start = time.time()
                if request == "-g":
                    subprocess.check_call("python GeSeMa.py " + file + " " + execution, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-rg":
                    subprocess.check_call("python RandomGreedyMapping.py " + file + " " + execution, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-e":
                    subprocess.check_call("python ExhaustiveMapping.py " + file, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                timeResults.append(time.time() - start)

            timeResults.sort()
            outliers = len(timeResults) // 20
            if outliers > 0:
                timeResults = timeResults[outliers:][:len(timeResults)-2*outliers]
            results[globalAlgorithms[request]][execution] = {}
            results[globalAlgorithms[request]][execution]["TIME"] = statistics.mean(timeResults)
            results[globalAlgorithms[request]][execution]["STDEV"] = statistics.stdev(timeResults)
            writer.write(globalAlgorithms[request] + ";" + execution + ";" + str(results[globalAlgorithms[request]][execution]["TIME"]) + ";" + str(results[globalAlgorithms[request]][execution]["STDEV"]) + "\n")

    writer.close()
    return results


def quality(rep, file, confs, modes):

    results = {}

    writer = open(file.split(".")[0] + "QUALITY.csv", "w+")
    writer.write("ALGORITHM;CONF;MEAN_RESULTS;STDEV_RESULTS;EXH_PARETO;EXH_WORST;MEAN_PARETO_G;STDEV_PARETO_G;MEAN_PARETO_F;STDEV_PARETO_F;REL_PARETO_F;REL_PARETO_WC_F;\n")

    subprocess.check_call("python ExhaustiveMapping.py " + file + " -o parameter.csv ", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
    exhaustiveFile = open("parameter.csv", "r")
    exhaustiveReader = csv.reader(exhaustiveFile, delimiter=';')
    exhaustiveData = [distribution for distribution in exhaustiveReader]
    exhaustiveFile.close()
    exhaustiveDists = [distribution[0] for distribution in exhaustiveData]
    exhaustiveDists.pop()
    pfCandidates = int(exhaustiveData[-1][1])
    exhaustiveFronts = [distribution[-1] for distribution in exhaustiveData]
    pfWorst = max([int(f) for f in exhaustiveFronts[1:]])

    for request in modes:
        for execution in confs[modes.index(request)]:
            print("QUALITY TEST: " + file + " || " + str(globalAlgorithms[request]) + " (" + execution + ")")
            generalFronts = []
            realPareto = []
            quantityFronts = []
            
            for test in range(rep):

                analyzerFronts = [] 
                if request == "-g":
                    subprocess.check_call("python GeSeMa.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-rg":
                     subprocess.check_call("python RandomGreedyMapping.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)

                analyzerFile = open("output.csv", "r")
                analyzerReader = csv.reader(analyzerFile, delimiter=';')
                analyzerData = [distribution[0] for distribution in analyzerReader]
                analyzerData.remove('MAPPING')
                analyzerFile.close()

                for distribution in analyzerData:
                    analyzerFronts.append(exhaustiveFronts[exhaustiveDists.index(distribution)])

                generalFronts = generalFronts + [int(f) for f in analyzerFronts]
                realPareto.append(analyzerFronts.count(0))
                quantityFronts.append(len(analyzerFronts))
                os.remove("output.csv")

            writer.write(globalAlgorithms[request] + ";" + execution + ";" + str(statistics.mean(quantityFronts)) + ";" + str(statistics.stdev(quantityFronts)) + ";" + str(pfCandidates) + ";" + str(pfWorst) + ";" + str(statistics.mean(generalFronts)) + ";" + str(statistics.stdev(generalFronts)) + ";" + str(statistics.mean(realPareto)) + ";" + str(statistics.stdev(realPareto)) + ";" + str(statistics.mean(realPareto)/pfCandidates) + ";" + str((statistics.mean(realPareto) - statistics.stdev(realPareto))/pfCandidates) + "\n")

    os.remove("parameter.csv")
    writer.close()


if len(sys.argv) < 7:
    print("USAGE [TIMING TEST]: *.py -t [-e] [-g {LIST OF CONFIGURATIONS}] [-rg {LIST OF CONFIGURATIONS}] -r ROUNDS -f FILE")
    print("\t-t: Timing test flag")
    print("\t-g: GeSeMa timing (SEQUENCE OF STRINGS BETWEEN \" OF CONFIGURATIONS)")
    print("\t-e: Exhaustive timing")
    print("\t-r: Number of timing rounds (INT)")
    print("\t-f: File path and name (STRING)")
    print("")
    print("USAGE [QUALITY TEST]: *.py -q [-g {LIST OF CONFIGURATIONS}] [-rg {LIST OF CONFIGURATIONS}] -r ROUNDS -f FILE")
    print("\t-q: Quality test flag")
    print("\t-g: GeSeMa quality (SEQUENCE OF STRINGS BETWEEN \" OF CONFIGURATIONS)")
    print("\t-r: Number of timing rounds (INT)")
    print("\t-f: File path and name (STRING)")
    exit()

if sys.argv[-4] != "-r" and not sys.argv[-3].isdigit():
    print("ERROR: INVALID NUMBER/FLAG OF ROUNDS")
    exit()

if sys.argv[-2] != "-f" and not os.path.isfile(sys.argv[-1]):
    print("ERROR: INVALID PATH/NAME/FLAG OF FILE")
    exit()

rep = int(sys.argv[-3])
file = sys.argv[-1]
confs = []
modes = []

if sys.argv[1] == "-t":
    cConf = []
    cMode = sys.argv[2]
    if not cMode in ["-g", "-e"]:
        print("ERROR: INVALID FLAG OF ALGORITHM")
        exit()
    for index in range(3, len(sys.argv)):
        if sys.argv[index] == "-r":
            confs.append(cConf)
            modes.append(cMode)
            break
        if sys.argv[index] in ["-g", "-e", "-rg"]:
            confs.append(cConf)
            modes.append(cMode)
            cConf = []
            cMode = sys.argv[index]
            continue
        else:
            cConf.append(sys.argv[index])
    timing(rep, file, confs, modes)

elif sys.argv[1] == "-q":

    cConf = []
    cMode = sys.argv[2]
    if not cMode in ["-g"]:
        print("ERROR: INVALID FLAG OF ALGORITHM")
        exit()
    for index in range(3, len(sys.argv)):
        if sys.argv[index] == "-r":
            confs.append(cConf)
            modes.append(cMode)
            break
        if sys.argv[index] in ["-g", "-rg"]:
            confs.append(cConf)
            modes.append(cMode)
            cConf = []
            cMode = sys.argv[index]
            continue
        else:
            cConf.append(sys.argv[index])
    quality(rep, file, confs, modes)