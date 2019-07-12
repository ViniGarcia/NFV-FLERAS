########### HELM CLASS DESCRIPTION ############

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service)
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A DICTIONARY OF EVALUATION METRICS (ID:(#OBJECTIVE,
#WEIGHT)) AND A DICTIONARY OF PARTIAL RESULTS (METRIC
#EVALUATIONS) FOR EACH CANDIDATE ID OF A DEPLOYMENT STAGE
#(DICTIONARY OF DICTIONARIES). IT USES THESE PARTIAL RESULTS
#TO CALCULATE THE SUITABILITY INDEXES FOR THE CANDIDATES. IT
#RETURNS A DICTIONARY WITH OF CANDIDATES ID WITH THEIR RESPEC-
#VELY SUITABILITY INDEXES (FLOAT VALUE).

#THE CLASS STATUS ATTRIBUTE INDICATE ITS
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: IDLE STATE (WAITING FOR METRICS CONF.)
#1: ACTIVE STATE (WAITING FOR PARTIAL RESULTS)
#2: EVALUATION SUCCESS

#ERROR CODES ->
#-1 -> Wrong argument for configuration
#-2 -> Wrong element in metrics dictionary
#-3 -> Wrong argument in metric obj. description
#-4 -> Invalid metric objective
#-5 -> Wrong argument in metric weight description
#-6 -> Invalid metric weight

#-7 -> HELM is not configured
#-8 -> Wrong argument for evaluation
#-9 -> Wrong argument for partial result
#-10 -> Partial results does not match with evaluation metrics
#-11 -> invalid value for partial result

#################################################

from numpy import array

############### HELM CLASS BEGIN ################

class HELM:
    __status = None

    __evalMetrics = None
    __partialResults = None
    __lastIndexing = None

    ######## CONSTRUCTOR ########

    def __init__(self, evalMetrics):

        if evalMetrics == None:
            self.__status = 0
        else:
            self.hConfigure(evalMetrics)

    ######## PRIVATE METHODS ########

    def __hSI(self):

        partialResults = {}
        weightSum = 0
        for metric in self.__evalMetrics:
            partialResults[metric] = [candidate[metric] for candidate in self.__partialResults.values()]
            weightSum += self.__evalMetrics[metric][1]

        for metric in partialResults:
            partialResults[metric] = array(partialResults[metric])
            if self.__evalMetrics[metric][0] == "max":
                if partialResults[metric].max(axis=0) != partialResults[metric].min(axis=0):
                    partialResults[metric] = ((partialResults[metric] - partialResults[metric].min(axis=0)) / (partialResults[metric].max(axis=0) - partialResults[metric].min(axis=0))) * self.__evalMetrics[metric][1] / weightSum
                else:
                    partialResults[metric] = [self.__evalMetrics[metric][1] / weightSum for candidate in self.__partialResults]
            else:
                if partialResults[metric].max(axis=0) != partialResults[metric].min(axis=0):
                    partialResults[metric] = (partialResults[metric].max(axis=0) - partialResults[metric]) / (partialResults[metric].max(axis=0) - partialResults[metric].min(axis=0)) * self.__evalMetrics[metric][1] / weightSum
                else:
                    partialResults[metric] = [self.__evalMetrics[metric][1] / weightSum for candidate in self.__partialResults]

        self.__lastIndexing = {}
        keys = list(self.__partialResults.keys())
        for index in range(len(self.__partialResults)):
            self.__lastIndexing[keys[index]] = sum([candidate[index] for candidate in partialResults.values()])

        return self.__lastIndexing

    ######## PUBLIC METHODS ########

    def hConfigure(self, evalMetrics):

        if not isinstance(evalMetrics, dict):
            self.__status = -1
            return -1

        for key in evalMetrics:
            if not isinstance(evalMetrics[key], tuple):
                self.__status = -2
                return -2
            if not isinstance(evalMetrics[key][0], str):
                self.__status = -3
                return -3
            if evalMetrics[key][0] != "max" and evalMetrics[key][0] != "min":
                self.__status = -4
                return -4
            if not isinstance(evalMetrics[key][1], float) and not isinstance(evalMetrics[key][1], int):
                self.__status = -5
                return -5
            if evalMetrics[key][1] <= 0:
                self.__status = -6
                return -6

            self.__evalMetrics = evalMetrics
            self.__partialResults = None
            self.__lastIndexing = None
            self.__status = 1
            return 1

    def hEvaluate(self, partialResults):

        if not self.__status == 1:
            return -7

        if not isinstance(partialResults, dict):
            return -8

        metricKeys = list(self.__evalMetrics.keys())
        for rKey in partialResults:
            if not isinstance(partialResults[rKey], dict):
                return -9
            if partialResults[rKey].keys() != set(metricKeys):
                return -10

            for mKey in partialResults[rKey]:
                if not isinstance(partialResults[rKey][mKey], float) and not isinstance(partialResults[rKey][mKey], int):
                    return -11

        self.__partialResults = partialResults
        self.__lastIndexing = None

        return self.__hSI()

    def getStatus(self):
        return self.__status

    def getIndexing(self):
        return self.__lastIndexing

    def getPartialResults(self):
        return self.__partialResults

    def getEvalMetrics(self):
        return self.__evalMetrics

################ HELM CLASS END #################

#################################################
#TEST SET
import random
import time
import statistics

#script = [[1,1,2,(0,50)], [1,1,4,(0,50)], [1,1,8,(0,50)], [1,1,16,(0,50)], [1,1,32,(0,50)], [1,1,64,(0,50)], [1,1,128,(0,50)], [1,1,256,(0,50)], [1,1,1024,(0,50)], [1,1,2048,(0,50)], [1,1,4096,(0,50)], [1,1,8192,(0,50)], [1,1,16384,(0,50)], [1,1,32768,(0,50)], [1,1,65536,(0,50)]]
#script = [[2,2,2,(0,50)], [2,2,4,(0,50)], [2,2,8,(0,50)], [2,2,16,(0,50)], [2,2,32,(0,50)], [2,2,64,(0,50)], [2,2,128,(0,50)], [2,2,256,(0,50)], [2,2,1024,(0,50)], [2,2,2048,(0,50)], [2,2,4096,(0,50)], [2,2,8192,(0,50)], [2,2,16384,(0,50)], [2,2,32768,(0,50)], [2,2,65536,(0,50)]]
#script = [[4,4,2,(0,50)], [4,4,4,(0,50)], [4,4,8,(0,50)], [4,4,16,(0,50)], [4,4,32,(0,50)], [4,4,64,(0,50)], [4,4,128,(0,50)], [4,4,256,(0,50)], [4,4,1024,(0,50)], [4,4,2048,(0,50)], [4,4,4096,(0,50)], [4,4,8192,(0,50)], [4,4,16384,(0,50)], [4,4,32768,(0,50)], [4,4,65536,(0,50)]]
#script = [[8,8,2,(0,50)], [8,8,4,(0,50)], [8,8,8,(0,50)], [8,8,16,(0,50)], [8,8,32,(0,50)], [8,8,64,(0,50)], [8,8,128,(0,50)], [8,8,256,(0,50)], [8,8,1024,(0,50)], [8,8,2048,(0,50)], [8,8,4096,(0,50)], [8,8,8192,(0,50)], [8,8,16384,(0,50)], [8,8,32768,(0,50)], [8,8,65536,(0,50)]]
#script = [[16,16,2,(0,50)], [16,16,4,(0,50)], [16,16,8,(0,50)], [16,16,16,(0,50)], [16,16,32,(0,50)], [16,16,64,(0,50)], [16,16,128,(0,50)], [16,16,256,(0,50)], [16,16,1024,(0,50)], [16,16,2048,(0,50)], [16,16,4096,(0,50)], [16,16,8192,(0,50)], [16,16,16384,(0,50)], [16,16,32768,(0,50)], [16,16,65536,(0,50)]]
#script = [[32,32,2,(0,50)], [32,32,4,(0,50)], [32,32,8,(0,50)], [32,32,16,(0,50)], [32,32,32,(0,50)], [32,32,64,(0,50)], [32,32,128,(0,50)], [32,32,256,(0,50)], [32,32,1024,(0,50)], [32,32,2048,(0,50)], [32,32,4096,(0,50)], [32,32,8192,(0,50)], [32,32,16384,(0,50)], [32,32,32768,(0,50)], [32,32,65536,(0,50)]]

#script = [[1,1,10,(0,50)], [1,1,100,(0,50)], [1,1,1000,(0,50)], [1,1,10000,(0,50)], [1,1,100000,(0,50)]]
#script = [[2,2,10,(0,50)], [2,2,100,(0,50)], [2,2,1000,(0,50)], [2,2,10000,(0,50)], [2,2,100000,(0,50)]]
#script = [[4,4,10,(0,50)], [4,4,100,(0,50)], [4,4,1000,(0,50)], [4,4,10000,(0,50)], [4,4,100000,(0,50)]]
#script = [[8,8,10,(0,50)], [8,8,100,(0,50)], [8,8,1000,(0,50)], [8,8,10000,(0,50)], [8,8,100000,(0,50)]]
#script = [[16,16,10,(0,50)], [16,16,100,(0,50)], [16,16,1000,(0,50)], [16,16,10000,(0,50)], [16,16,100000,(0,50)]]
#script = [[32,32,10,(0,50)], [32,32,100,(0,50)], [32,32,1000,(0,50)], [32,32,10000,(0,50)], [32,32,100000,(0,50)]]

#script = [[1,1,5,(0,50)], [1,1,25,(0,50)], [1,1,125,(0,50)], [1,1,625,(0,50)], [1,1,3125,(0,50)], [1,1,15625,(0,50)], [1,1,78125,(0,50)]]
#script = [[2,2,5,(0,50)], [2,2,25,(0,50)], [2,2,125,(0,50)], [2,2,625,(0,50)], [2,2,3125,(0,50)], [2,2,15625,(0,50)], [2,2,78125,(0,50)]]
#script = [[4,4,5,(0,50)], [4,4,25,(0,50)], [4,4,125,(0,50)], [4,4,625,(0,50)], [4,4,3125,(0,50)], [4,4,15625,(0,50)], [4,4,78125,(0,50)]]
#script = [[8,8,5,(0,50)], [8,8,25,(0,50)], [8,8,125,(0,50)], [8,8,625,(0,50)], [8,8,3125,(0,50)], [8,8,15625,(0,50)], [8,8,78125,(0,50)]]
#script = [[16,16,5,(0,50)], [16,16,25,(0,50)], [16,16,125,(0,50)], [16,16,625,(0,50)], [16,16,3125,(0,50)], [16,16,15625,(0,50)], [16,16,78125,(0,50)]]
#script = [[32,32,5,(0,50)], [32,32,25,(0,50)], [32,32,125,(0,50)], [32,32,625,(0,50)], [32,32,3125,(0,50)], [32,32,15625,(0,50)], [32,32,78125,(0,50)]]

for index in range(len(script)):
    Nmin = script[index][0]
    Nmax = script[index][1]
    M = script[index][2]
    PR = script[index][3]

    A = {}
    for i in range(Nmin):
        A["M" + str(i)] = ("min", 1)
    for i in range(Nmin, Nmin+Nmax):
        A["M" + str(i)] = ("max", 1)

    B = {}
    for i in range(M):
        B["C" + str(i)] = {}
        for j in list(A.keys()):
            B["C" + str(i)][j] = random.randint(PR[0], PR[1])

    time_keeper = []
    for i in range(30):
        start_time = time.time()
        test = HELM(A)
        test.hEvaluate(B)
        end_time = time.time()
        time_keeper.append(end_time - start_time)

    print("EVAL TIME TEST #" + str(index) + " " + str(script[index]) + ": MEAN -> " + str(statistics.mean(time_keeper)) + " STDDEV -> " + str(statistics.stdev(time_keeper)))
