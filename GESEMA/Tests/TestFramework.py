#!/usr/bin/python
import sys
import os
import subprocess
import time
import statistics
import yaml
import csv
import math

globalAlgorithms = {"-g":"GeSeMa", "-ex":"Exhaustive", "-sg":"StochasticKGreedy", "-ra":"Random", "-tg":"TraditionalGreedy"}


def paretoFrontierSubroutine(results, frontiers, front_index, exchange_indexes, objectives):

    new_front = []
    add_front = []

    for index in exchange_indexes:
        it_dominates = True

        for candidate in range(len(frontiers[front_index])):
            count_dominated = 0

            for objective in range(len(objectives)):
                if objectives[objective] == "MAXIMIZATION":
                    if results[index][objective] < results[frontiers[front_index][candidate]][objective]:
                        count_dominated += 1
                elif objectives[objective] == "MINIMIZATION":
                    if results[index][objective] > results[frontiers[front_index][candidate]][objective]:
                        count_dominated += 1

            if count_dominated > 0:
                it_dominates = False
                break

        if it_dominates:
            new_front.append(index)
        else:
            add_front.append(index)

    frontiers[front_index] = frontiers[front_index] + add_front
    if len(new_front) > 0:
        frontiers.insert(front_index, new_front)


def paretoFrontiers(results, objectives):

    frontiers = [[0], []]
    indexes = [i for i in range(1, len(results))]

    while True:
        if len(indexes) == 0:
            break
        index = indexes.pop(0)

        for front in range(len(frontiers)):
            is_dominated = False
            it_dominates = []

            for candidate in range(len(frontiers[front])):
                count_dominated = 0
                result_equity = True

                for objective in range(len(objectives)):
                    if objectives[objective] == "MAXIMIZATION":
                        if results[index][objective] < results[frontiers[front][candidate]][objective]:
                            count_dominated += 1
                        if result_equity and results[index][objective] != results[frontiers[front][candidate]][objective]:
                            result_equity = False
                    elif objectives[objective] == "MINIMIZATION":
                        if results[index][objective] > results[frontiers[front][candidate]][objective]:
                            count_dominated += 1
                        if result_equity and results[index][objective] != results[frontiers[front][candidate]][objective]:
                            result_equity = False

                if result_equity:
                    break
                if count_dominated == len(objectives):
                    is_dominated = True
                    break
                if count_dominated == 0:
                    it_dominates.append(frontiers[front][candidate])

            if result_equity:
                frontiers[front].append(index)
                break
            if not is_dominated and len(it_dominates) < len(frontiers[front]):
                frontiers[front].append(index)
                if len(it_dominates) > 0:
                    frontiers[front] = list(set(frontiers[front]) - set(it_dominates))
                    paretoFrontierSubroutine(results, frontiers, front + 1, it_dominates, objectives)
                break
            if is_dominated:
                continue
            if len(it_dominates) == len(frontiers[front]):
                frontiers.insert(front, [index])
                break

    return frontiers[:-1]


def timing(rep, file, confs, modes):

    results = {}

    writer = open(file.split(".")[0] + "TIMING.csv", "w+")
    writer.write("ALGORITHM;CONF;TIME;STDEV\n")

    if "-tg" in modes:
        confs[modes.index("-tg")].append("UNIQUE")
    if "-ex" in modes:
        confs[modes.index("-ex")].append("UNIQUE")

    for request in modes:
        results[globalAlgorithms[request]] = {}
        for execution in confs[modes.index(request)]:
            timeResults = []
            print("TIMING TEST: " + file + " || " + str(globalAlgorithms[request]) + " (" + execution + ")")
            for test in range(rep):
                print("ROUND #" + str(test))
                start = time.time()
                if request == "-g":
                    subprocess.check_call("5.GeSeMa.py " + file + " " + execution, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-ex":
                    subprocess.check_call("1.Exhaustive.py " + file, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-ra":
                    subprocess.check_call("2.Random.py " + file + " " + execution, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-tg":
                    subprocess.check_call("3.Greedy.py " + file, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-sg":
                    subprocess.check_call("4.SK-Greedy.py " + file + " " + execution, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
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


def definitiveQuality(rep, file, confs, modes):

    writer = open(file.split(".")[0] + "QUALITY.csv", "w+")
    writer.write("ALGORITHM;CONF;MEAN_RESULTS;STDEV_RESULTS;EXH_PARETO;EXH_WORST;MEAN_PARETO_G;STDEV_PARETO_G;MEAN_PARETO_F;STDEV_PARETO_F;REL_PARETO_F;REL_PARETO_WC_F;\n")

    subprocess.check_call("ExhaustiveMapping.py " + file + " -o parameter.csv ", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
    exhaustiveFile = open("parameter.csv", "r")
    exhaustiveReader = csv.reader(exhaustiveFile, delimiter=';')
    exhaustiveData = [distribution for distribution in exhaustiveReader]
    exhaustiveFile.close()
    exhaustiveDists = [distribution[0] for distribution in exhaustiveData]
    exhaustiveDists.pop()
    pfCandidates = int(exhaustiveData[-1][1])
    exhaustiveFronts = [distribution[-1] for distribution in exhaustiveData]
    pfWorst = max([int(f) for f in exhaustiveFronts[1:]])

    if "-tg" in modes:
        confs[modes.index("-tg")].append("UNIQUE")

    for request in modes:
        for execution in confs[modes.index(request)]:
            print("QUALITY TEST: " + file + " || " + str(globalAlgorithms[request]) + " (" + execution + ")")
            generalFronts = []
            realPareto = []
            quantityFronts = []
            
            for test in range(rep):
                print("ROUND #" + str(test))

                analyzerFronts = [] 
                if request == "-g":
                    subprocess.check_call("5.GeSeMa.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-ra":
                    subprocess.check_call("2.Random.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-tg":
                    subprocess.check_call("3.Greedy.py " + file + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-sg":
                    subprocess.check_call("4.SK-Greedy.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)

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

                if request == "-tg":
                    break

            writer.write(globalAlgorithms[request] + ";" + execution + ";" + str(statistics.mean(quantityFronts)) + ";" + str(statistics.stdev(quantityFronts)) + ";" + str(pfCandidates) + ";" + str(pfWorst) + ";" + str(statistics.mean(generalFronts)) + ";" + str(statistics.stdev(generalFronts)) + ";" + str(statistics.mean(realPareto)) + ";" + str(statistics.stdev(realPareto)) + ";" + str(statistics.mean(realPareto)/pfCandidates) + ";" + str((statistics.mean(realPareto) - statistics.stdev(realPareto))/pfCandidates) + "\n")

    os.remove("parameter.csv")
    writer.close()


def relativeQuality(rep, file, confs, modes):
    
    document = open(file, 'r')
    request = yaml.safe_load(document)
    objectives = []
    for metric in request["METRICS"]["LOCAL"]:
        objectives.append(request["METRICS"]["LOCAL"][metric]["OBJECTIVE"])
    for metric in request["METRICS"]["TRANSITION"]:
        objectives.append(request["METRICS"]["TRANSITION"][metric]["OBJECTIVE"])
    document.close()

    writer = open(file.split(".")[0] + "RELQUALITY.csv", "w+")
    writer.write("ALGORITHM;CONF;TOTAL_FRONTS;MEAN_PARETO_G;STDEV_PARETO_G;TOP10_MEAN_PARETO_G;TOP10_STDEV_PARETO_G;PARETO_SIZE\n")

    if "-tg" in modes:
        confs[modes.index("-tg")].append("UNIQUE")

    allCandidates = {}
    setEvaluation = []
    for request in modes:
        
        allCandidates[request] = {}
        for execution in confs[modes.index(request)]:
            print("QUALITY TEST: " + file + " || " + str(globalAlgorithms[request]) + " (" + execution + ")")
            generalFronts = []
            realPareto = []
            quantityFronts = []
            
            allCandidates[request][execution] = [[],[]]
            for test in range(rep):
                print("ROUND #" + str(test))

                analyzerFronts = [] 
                if request == "-g":
                    subprocess.check_call("5.GeSeMa.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-ra":
                    subprocess.check_call("2.Random.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-tg":
                    subprocess.check_call("3.Greedy.py " + file + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-sg":
                    subprocess.check_call("4.SK-Greedy.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)

                analyzerFile = open("output.csv", "r")
                analyzerReader = csv.reader(analyzerFile, delimiter=';')
                analyzerHeaders = next(analyzerReader)
                analyzerColumns = [[] for l in range(len(analyzerHeaders)-1)]
                for line in analyzerReader:
                    analyzerColumns[0].append(line[0])
                    for index in range(1, len(analyzerHeaders)-1):
                        analyzerColumns[index].append(float(line[index]))
                analyzerFile.close()

                allCandidates[request][execution][0].append(analyzerColumns[0])
                allCandidates[request][execution][1].append(list(zip(*analyzerColumns[1:])))
                os.remove("output.csv")

                if request == "-tg":
                    break

            #=========================== REMOVAL OF OUTLIERS IN RESULTS =========================== 
            outliers = round(len(allCandidates[request][execution][1]) / 10) #Remove 10% if best and worst results
            if outliers > 0 and outliers and len(allCandidates[request][execution][1]) > 2*outliers:
                analysis = sum(allCandidates[request][execution][1], [])
                analysis = paretoFrontiers(analysis, objectives)

                begin = 0
                general = []
                for sample in allCandidates[request][execution][1]:
                    local = []
                    end = begin + len(sample)

                    for front in range(len(analysis)):
                        for candidate in analysis[front]:
                            if candidate >= begin and candidate < end:
                                local.append(front)
                    general.append(local)   
                    begin = end

                general = [statistics.mean(g) for g in general]
                for index in range(outliers):
                    minimum = general.index(min(general))
                    general.pop(minimum)
                    allCandidates[request][execution][0].pop(minimum)
                    allCandidates[request][execution][1].pop(minimum)
                    maximum = general.index(max(general))
                    general.pop(maximum)
                    allCandidates[request][execution][0].pop(maximum)
                    allCandidates[request][execution][1].pop(maximum)
            #======================================================================================

            allCandidates[request][execution][0] = sum(allCandidates[request][execution][0], [])
            allCandidates[request][execution][1] = sum(allCandidates[request][execution][1], [])
            allCandidates[request][execution].append(len(setEvaluation))
            setEvaluation = setEvaluation + allCandidates[request][execution][1]

    frontsCandidates = paretoFrontiers(setEvaluation, objectives)
    for request in allCandidates:
        for execution in allCandidates[request]:
            frontsLocal = []
            frontsBegin = allCandidates[request][execution][2]
            frontsEnd = frontsBegin + len(allCandidates[request][execution][1])
            
            for front in range(len(frontsCandidates)):
                for candidate in frontsCandidates[front]:
                    if candidate >= frontsBegin and candidate < frontsEnd:
                        frontsLocal.append(front)

            frontsLocal.sort()
            writer.write(globalAlgorithms[request] + ";" + execution + ";" + str(len(frontsCandidates)) + ";" + str(statistics.mean(frontsLocal)) + ";" + str(statistics.stdev(frontsLocal)) + ";" + str(statistics.mean(frontsLocal[:10])) + ";" + str(statistics.stdev(frontsLocal[:10])) + ";" + str(len(frontsLocal)) + "\n")
    
    writer.close()


if len(sys.argv) < 7:
    print("USAGE [TIMING TEST]: *.py -t [-ex] [-tg] [-ra {LIST OF CONFIGURATIONS}] [-sg {LIST OF CONFIGURATIONS}] [-g {LIST OF CONFIGURATIONS}] -r ROUNDS -f FILE")
    print("\t-t: Timing test flag")
    print("\t-ex: Exhaustive timing")
    print("\t-tg: Traditional greedy")
    print("\t-ra: Random timing (SEQUENCE OF STRINGS BETWEEN \" OF CONFIGURATIONS)")
    print("\t-sg: SK-Greedy timing (SEQUENCE OF STRINGS BETWEEN \" OF CONFIGURATIONS)")
    print("\t-g: GeSeMa timing (SEQUENCE OF STRINGS BETWEEN \" OF CONFIGURATIONS)")
    print("\t-r: Number of timing rounds (INT)")
    print("\t-f: File path and name (STRING)")
    print("")
    print("USAGE [QUALITY TEST]: *.py -dq|rq [-tg] [-ra {LIST OF CONFIGURATIONS}] [-sg {LIST OF CONFIGURATIONS}] [-g {LIST OF CONFIGURATIONS}] -r ROUNDS -f FILE")
    print("\t-dq: Definitive quality test flag -- based on exhaustive results")
    print("\t-rq: Relative quality test flag -- based on heuristics results only")
    print("\t-tg: Traditional greedy")
    print("\t-ra: Random quality (SEQUENCE OF STRINGS BETWEEN \" OF CONFIGURATIONS)")
    print("\t-sg: SK-Greedy quality (SEQUENCE OF STRINGS BETWEEN \" OF CONFIGURATIONS)")
    print("\t-g: GeSeMa quality (SEQUENCE OF STRINGS BETWEEN \" OF CONFIGURATIONS)")
    print("\t-r: Number of quality rounds (INT)")
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
    if not cMode in ["-g", "-ex", "-sg", "-ra", "-tg"]:
        print("ERROR: INVALID FLAG OF ALGORITHM")
        exit()
    for index in range(3, len(sys.argv)):
        if sys.argv[index] == "-r":
            confs.append(cConf)
            modes.append(cMode)
            break
        if sys.argv[index] in ["-g", "-ex", "-sg", "-ra", "-tg"]:
            confs.append(cConf)
            modes.append(cMode)
            cConf = []
            cMode = sys.argv[index]
            continue
        else:
            cConf.append(sys.argv[index])
    timing(rep, file, confs, modes)

elif sys.argv[1] == "-dq" or sys.argv[1] == "-rq":
    cConf = []
    cMode = sys.argv[2]
    if not cMode in ["-g", "-sg", "-ra", "-tg"]:
        print("ERROR: INVALID FLAG OF ALGORITHM")
        exit()
    for index in range(3, len(sys.argv)):
        if sys.argv[index] == "-r":
            confs.append(cConf)
            modes.append(cMode)
            break
        if sys.argv[index] in ["-g", "-sg", "-ra", "-tg"]:
            confs.append(cConf)
            modes.append(cMode)
            cConf = []
            cMode = sys.argv[index]
            continue
        else:
            cConf.append(sys.argv[index])
    if sys.argv[1] == "dq":
        definitiveQuality(rep, file, conf, modes)
    else:
        relativeQuality(rep, file, confs, modes)