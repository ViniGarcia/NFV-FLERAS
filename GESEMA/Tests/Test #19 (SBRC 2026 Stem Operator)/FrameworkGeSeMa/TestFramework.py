#!/usr/bin/python
import sys
import os
import subprocess
import time
import statistics
import yaml
import csv
import math

globalAlgorithms = {"-g":"GeSeMa", "-ex":"Exhaustive", "-sg":"StochasticKGreedy", "-ra":"Random", "-tg":"TraditionalGreedy", "-gl":"GA+LCB"}


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
                    subprocess.check_call("python3 5.GeSeMa.py " + file + " " + execution, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-ex":
                    subprocess.check_call("python3 1.Exhaustive.py " + file, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-ra":
                    subprocess.check_call("python3 2.Random.py " + file + " " + execution, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-tg":
                    subprocess.check_call("python3 3.Greedy.py " + file, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-sg":
                    subprocess.check_call("python3 4.SK-Greedy.py " + file + " " + execution, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-gl":
                    subprocess.check_call("python3 6.GA+LCB.py " + file + " " + execution, shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
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
    writer.write("ALGORITHM;CONF;MEAN_RESULTS;STDEV_RESULTS;EXH_PARETO;EXH_WORST;MEAN_PARETO_G;STDEV_PARETO_G;MEAN_PARETO_G_TOP10;STDEV_PARETO_G_TOP10;PARETO_G_TOP1;MEAN_PARETO_F;STDEV_PARETO_F;REL_PARETO_F;REL_PARETO_WC_F;\n")

    subprocess.check_call("python3 1.Exhaustive.py " + file + " -o parameter.csv ", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
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
                analyzerTiming = []
                startTime = time.time()
                if request == "-g":
                    subprocess.check_call("python3 5.GeSeMa.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-ra":
                    subprocess.check_call("python3 2.Random.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-tg":
                    subprocess.check_call("python3 3.Greedy.py " + file + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-sg":
                    subprocess.check_call("python3 4.SK-Greedy.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-gl":
                    subprocess.check_call("python3 6.GA+LCB.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                analyzerTiming.append(time.time() - startTime)

                analyzerFile = open("output.csv", "r")
                analyzerReader = csv.reader(analyzerFile, delimiter=';')
                analyzerData = [distribution[0] for distribution in analyzerReader]
                analyzerData.remove('MAPPING')
                analyzerFile.close()

                for distribution in analyzerData:
                    analyzerFronts.append(exhaustiveFronts[exhaustiveDists.index(distribution[1:-1])])

                generalFronts = generalFronts + [int(f) for f in analyzerFronts]
                realPareto.append(analyzerFronts.count(0))
                quantityFronts.append(len(analyzerFronts))
                os.remove("output.csv")

                if request == "-tg":
                    break

            try:
                m_quantityFronts = statistics.mean(quantityFronts)
                s_quantityFronts = statistics.stdev(quantityFronts)
            except:
                m_quantityFronts = quantityFronts[0]
                s_quantityFronts = 0
            
            generalFronts.sort()
            try:
                m_generalFronts = statistics.mean(generalFronts)
                s_generalFronts = statistics.stdev(generalFronts)
                m_top10Fronts = statistics.mean(generalFronts[:10])
                s_top10Fronts = statistics.stdev(generalFronts[:10])
            except:
                m_generalFronts = generalFronts[0]
                s_generalFronts = 0
                m_top10Fronts = generalFronts[0]
                s_top10Fronts = 0

            try:
                m_realPareto = statistics.mean(realPareto)
                s_realPareto = statistics.stdev(realPareto)
            except:
                m_realPareto = realPareto[0]
                s_realPareto = 0


            writer.write(globalAlgorithms[request] + ";" + execution + ";" + str(m_quantityFronts) + ";" + str(s_quantityFronts) + ";" + str(pfCandidates) + ";" + str(pfWorst) + ";" + str(m_generalFronts) + ";" + str(s_generalFronts) + ";" + str(m_top10Fronts) + ";" + str(s_top10Fronts) + ";" + str(generalFronts[0]) + ";" + str(m_realPareto) + ";" + str(s_realPareto) + ";" + str(m_realPareto/pfCandidates) + ";" + str((m_realPareto - s_realPareto)/pfCandidates) + "\n")

    os.remove("parameter.csv")
    writer.close()

def progressiveQuality(rep, file, confs, modes):

    writer = open(file.split(".")[0] + "QUALITY.csv", "w+")
    writer.write("ALGORITHM;CONF;STEP;MEAN_RESULTS;STDEV_RESULTS;EXH_PARETO;EXH_WORST;MEAN_PARETO_G;STDEV_PARETO_G;MIN_PARETO_G;MAX_PARETO_G\n")

    subprocess.check_call("python3 1.Exhaustive.py " + file + " -o parameter.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
    exhaustiveFile = open("parameter.csv", "r")
    exhaustiveReader = csv.reader(exhaustiveFile, delimiter=';')
    exhaustiveHeader = next(exhaustiveReader)
    exhaustiveData = [distribution for distribution in exhaustiveReader]
    exhaustiveFile.close()
    exhaustiveDists = [distribution[0] for distribution in exhaustiveData]
    exhaustiveDists.pop()
    pfCandidates = int(exhaustiveData[-1][1])
    exhaustiveFronts = [int(distribution[-1]) for distribution in exhaustiveData]
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
                analyzerTiming = []
                startTime = time.time()
                if request == "-g":
                    subprocess.check_call("python3 5.GeSeMa.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-ra":
                    print("NOT SUPPORTED ALGORITHM!")
                elif request == "-tg":
                    print("NOT SUPPORTED ALGORITHM!")
                elif request == "-sg":
                    print("NOT SUPPORTED ALGORITHM!")
                elif request == "-gl":
                    print("NOT SUPPORTED ALGORITHM!")
                analyzerTiming.append(time.time() - startTime)

                analyzerFile = open("output.csv", "r")
                analyzerReader = csv.reader(analyzerFile, delimiter=';')
                analyzerHeader = next(analyzerReader)
                if not "STEP" in analyzerHeader:
                    print("NOT SUPPORTED EXECUTION!")
                    break
                analyzerData = [(distribution[0][1:-1], int(distribution[-2]))for distribution in analyzerReader]
                analyzerFile.close()

                for distribution in analyzerData:
                    while len(analyzerFronts) < distribution[1] + 1:
                        analyzerFronts.append([])
                    analyzerFronts[distribution[1]].append(exhaustiveFronts[exhaustiveDists.index(distribution[0])])

                generalFronts.append(analyzerFronts)
                realPareto.append([step.count(0) for step in analyzerFronts])
                quantityFronts.append([len(step) for step in analyzerFronts])
                os.remove("output.csv")

                if request == "-tg":
                    break

            try:
                m_quantityFronts = []
                s_quantityFronts = []
                for step in range(len(quantityFronts[0])):
                    stepQuantity = [executionResults[step] for executionResults in quantityFronts]
                    m_quantityFronts.append(statistics.mean(stepQuantity))
                    s_quantityFronts.append(statistics.stdev(stepQuantity))
                
            except:
                m_quantityFronts = quantityFronts[0]
                s_quantityFronts = [0 for step in range(len(quantityFronts[0]))]
            
            min_generalFronts = []
            max_generalFronts = []
            m_generalFronts = []
            s_generalFronts = []
            
            for step in range(len(generalFronts[0])):
                stepFronts = []
                for executionResults in generalFronts:
                    stepFronts.extend(executionResults[step])
                try:
                    m_generalFronts.append(statistics.mean(stepFronts))
                    s_generalFronts.append(statistics.stdev(stepFronts))
                except:
                    m_generalFronts.append(stepFronts[0])
                    s_generalFronts.append(0)

                min_generalFronts.append(min(stepFronts))
                max_generalFronts.append(max(stepFronts))

            for step in range(len(m_quantityFronts)):
                writer.write(globalAlgorithms[request] + ";" + execution + ";" + str(step) + ";" + str(m_quantityFronts[step]) + ";" + str(s_quantityFronts[step]) + ";" + str(pfCandidates) + ";" + str(pfWorst) + ";" + str(m_generalFronts[step]) + ";" + str(s_generalFronts[step]) + ";" + str(min_generalFronts[step]) + ";" + str(max_generalFronts[step]) + "\n")                

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
    writer.write("ALGORITHM;CONF;TOTAL_FRONTS;MEAN_PARETO_G;STDEV_PARETO_G;TOP10_MEAN_PARETO_G;TOP10_STDEV_PARETO_G;PARETO_SIZE;MEAN_TIME;STDEV_TIME\n")

    if "-tg" in modes:
        confs[modes.index("-tg")].append("UNIQUE")

    allCandidates = {}
    setEvaluation = []
    allTiming = {}
    for request in modes:
        
        allCandidates[request] = {}
        allTiming[request] = {}
        for execution in confs[modes.index(request)]:
            print("QUALITY TEST: " + file + " || " + str(globalAlgorithms[request]) + " (" + execution + ")")
            generalFronts = []
            realPareto = []
            quantityFronts = []
            
            allCandidates[request][execution] = [[],[]]
            allTiming[request][execution] = []
            for test in range(rep):
                print("ROUND #" + str(test))

                analyzerFronts = []
                startTime = time.time()
                if request == "-g":
                    subprocess.check_call("python3 5.GeSeMa.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-ra":
                    subprocess.check_call("python3 2.Random.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-tg":
                    subprocess.check_call("python3 3.Greedy.py " + file + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-sg":
                    subprocess.check_call("python3 4.SK-Greedy.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                elif request == "-gl":
                    subprocess.check_call("python3 6.GA+LCB.py " + file + " " + execution + " -o output.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                allTiming[request][execution].append(time.time() - startTime)

                analyzerFile = open("output.csv", "r")
                analyzerReader = csv.reader(analyzerFile, delimiter=';')
                analyzerHeaders = next(analyzerReader)
                analyzerColumns = [[] for l in range(len(analyzerHeaders)-1)]
                for line in analyzerReader:
                    analyzerColumns[0].append(line[0])
                    for index in range(1, len(analyzerHeaders)-1):
                        line[index] = str(line[index])
                        line[index] = line[index].replace(',', '.')
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
            writer.write(globalAlgorithms[request] + ";" + execution + ";" + str(len(frontsCandidates)) + ";" + str(statistics.mean(frontsLocal)) + ";" + str(statistics.stdev(frontsLocal)) + ";" + str(statistics.mean(frontsLocal[:10])) + ";" + str(statistics.stdev(frontsLocal[:10])) + ";" + str(len(frontsLocal)) + ";" + str(statistics.mean(allTiming[request][execution])) + ";" + str(statistics.stdev(allTiming[request][execution])) + "\n")
    
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
    if not cMode in ["-g", "-ex", "-sg", "-ra", "-tg", "-gl"]:
        print("ERROR: INVALID FLAG OF ALGORITHM")
        exit()
    for index in range(3, len(sys.argv)):
        if sys.argv[index] == "-r":
            confs.append(cConf)
            modes.append(cMode)
            break
        if sys.argv[index] in ["-g", "-ex", "-sg", "-ra", "-tg", "-gl"]:
            confs.append(cConf)
            modes.append(cMode)
            cConf = []
            cMode = sys.argv[index]
            continue
        else:
            cConf.append(sys.argv[index])
    timing(rep, file, confs, modes)

elif sys.argv[1] == "-dq" or sys.argv[1] == "-pq" or sys.argv[1] == "-rq":
    cConf = []
    cMode = sys.argv[2]
    if not cMode in ["-g", "-sg", "-ra", "-tg", "-gl"]:
        print("ERROR: INVALID FLAG OF ALGORITHM")
        exit()
    for index in range(3, len(sys.argv)):
        if sys.argv[index] == "-r":
            confs.append(cConf)
            modes.append(cMode)
            break
        if sys.argv[index] in ["-g", "-sg", "-ra", "-tg", "-gl"]:
            confs.append(cConf)
            modes.append(cMode)
            cConf = []
            cMode = sys.argv[index]
            continue
        else:
            cConf.append(sys.argv[index])
    if sys.argv[1] == "-dq":
        definitiveQuality(rep, file, confs, modes)
    elif sys.argv[1] == "-pq":
        progressiveQuality(rep, file, confs, modes)
    else:
        relativeQuality(rep, file, confs, modes)