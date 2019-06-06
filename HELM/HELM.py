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
                partialResults[metric] = ((partialResults[metric] - partialResults[metric].min(axis=0)) / (partialResults[metric].max(axis=0) - partialResults[metric].min(axis=0))) * self.__evalMetrics[metric][1] / weightSum
            else:
                partialResults[metric] = (partialResults[metric].max(axis=0) - partialResults[metric]) / (partialResults[metric].max(axis=0) - partialResults[metric].min(axis=0)) * self.__evalMetrics[metric][1] / weightSum

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
            if list(partialResults[rKey]) != metricKeys:
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

#test = HELM({"A":("min", 0.5), "B":("max", 0.5)})
#print(test.hEvaluate({"C1":{"A":5, "B":10}, "C2":{"A":10, "B":5}}))
