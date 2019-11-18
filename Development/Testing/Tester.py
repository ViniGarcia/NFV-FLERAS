#!/usr/bin/python
import sys
import os
import subprocess
import time
import statistics
import yaml

def experiment(rep, files):

    results = {}
    for index in range(len(files)):
        subprocess.check_call("RequestTranslate.py " + files[index], shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
        
        subprocess.check_call("SFCSplitMap.py " + files[index].split(".")[0] + "SERVICE.yaml " + files[index].split(".")[0] + "DOMAIN.yaml -o" , shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
        subprocess.check_call("GeneticMapping.py " + files[index] + " -o " + files[index].split(".")[0] + "GESEMA.csv", shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)

        results[files[index]] = {"CUSMAP": {}, "GESEMA": {}}

        timeResults = []
        for test in range(rep):
            start = time.time()
            subprocess.check_call("SFCSplitMap.py " + files[index].split(".")[0] + "SERVICE.yaml " + files[index].split(".")[0] + "DOMAIN.yaml" , shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
            timeResults.append(time.time() - start) 
        results[files[index]]["CUSMAP"]["TIME"] = statistics.mean(timeResults)
        results[files[index]]["CUSMAP"]["STDEV"] = statistics.stdev(timeResults)

        timeResults = []
        for test in range(rep):
            start = time.time()
            subprocess.check_call("GeneticMapping.py " + files[index], shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
            timeResults.append(time.time() - start) 
        results[files[index]]["GESEMA"]["TIME"] = statistics.mean(timeResults)
        results[files[index]]["GESEMA"]["STDEV"] = statistics.stdev(timeResults)

        os.remove(files[index].split(".")[0] + "SERVICE.yaml")
        os.remove(files[index].split(".")[0] + "DOMAIN.yaml") 
        
        writer = open(files[index].split(".")[0] + "TIMING.csv", "w+")
        writer.write(yaml.dump(results))
        writer.close()


if len(sys.argv) < 3:
    print("USAGE: *.py ROUNDS [LIST OF FILES]")
    exit()

if not sys.argv[1].isdigit():
    print("ERROR: INVALID NUMBER OF ROUNDS")
    exit()

for file in sys.argv[2:]:
    if not os.path.isfile(file):
        print("ERROR: INVALID FILE (" + file + ")")
        exit()

experiment(int(sys.argv[1]), sys.argv[2:])
