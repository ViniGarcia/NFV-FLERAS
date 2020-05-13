########### CHEF CLASS DESCRIPTION ############

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

#-7 -> CHEF is not configured
#-8 -> Wrong argument for evaluation
#-9 -> Wrong argument for partial result
#-10 -> Partial results does not match with evaluation metrics
#-11 -> invalid value for partial result

#################################################

from itertools import combinations
from statistics import mean
from numpy import array
from scipy import stats
from copy import deepcopy

############### CHEF CLASS BEGIN ################

class CHEF:
    __status = None

    __evalMetrics = None
    __partialResults = None
    __lastIndexing = None

    ######## CONSTRUCTOR ########

    def __init__(self, evalMetrics):

        if evalMetrics == None:
            self.__status = 0
        else:
            self.cConfigure(evalMetrics)

    ######## PRIVATE METHODS ########

    def __cSI(self):

        partialResults = {}
        weightSum = 0
        for metric in self.__evalMetrics:
            partialResults[metric] = [candidate[metric] for candidate in self.__partialResults.values()]
            weightSum += self.__evalMetrics[metric][1]

        for metric in partialResults:
            partialResults[metric] = array(partialResults[metric])
            if self.__evalMetrics[metric][0] == "MAX":
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

    def __cPearson(self, samples):
        #samples: {cKey:{mKey:$float ...}...}

        mKeys = list(self.__evalMetrics.keys())
        mValues = [[] for key in mKeys]
        mCoefficients = {}

        for cKey in samples:
            for index in range(len(mKeys)):
                mValues[index].append(samples[cKey][mKeys[index]])

        mCombinations = combinations(range(len(mKeys)), 2)
        for combination in mCombinations:
            mPearson = stats.pearsonr(mValues[combination[0]], mValues[combination[1]])
            if self.__evalMetrics[mKeys[combination[0]]][0] == self.__evalMetrics[mKeys[combination[1]]][0]:
                mCoefficients[mKeys[combination[0]], mKeys[combination[1]]] = (mPearson[0], mPearson[1])
            else:
                mCoefficients[mKeys[combination[0]], mKeys[combination[1]]] = (mPearson[0] * -1, mPearson[1])

        return mCoefficients

    def __cBias(self, correlatedBiases):

        def cRecursiveBias(metric, checked, aggregation, weights):
            for bias in correlatedBiases[metric]:
                if bias in checked:
                    continue
                checked.append(bias)
                aggregation.append(bias)
                weights.append(self.__evalMetrics[bias][1])
                cRecursiveBias(bias, checked, aggregation, weights)

        nonBiasesMetrics = {}
        checkedMetrics = []
        reallocWeight = 0
        for metric in correlatedBiases:
            
            if metric in checkedMetrics:
                continue
            if len(correlatedBiases[metric]) == 0:
                nonBiasesMetrics[metric] = self.__evalMetrics[metric][1]
            else:
                aggregatedMetrics = []
                aggregatedWeights = []
                
                checkedMetrics.append(metric)
                aggregatedMetrics.append(metric)
                aggregatedWeights.append(self.__evalMetrics[metric][1])
                cRecursiveBias(metric, checkedMetrics, aggregatedMetrics, aggregatedWeights)

                maxWeight = max(aggregatedWeights)
                sumWeight = sum(aggregatedWeights)
                reallocWeight += sum(aggregatedWeights) - maxWeight

                for index in range(len(aggregatedMetrics)):
                    nonBiasesMetrics[aggregatedMetrics[index]] = maxWeight * (aggregatedWeights[index] / sumWeight)

        for metric in nonBiasesMetrics:
            nonBiasesMetrics[metric] = nonBiasesMetrics[metric] + (nonBiasesMetrics[metric] / (1 - reallocWeight)) * reallocWeight
        
        return nonBiasesMetrics

    ######## PUBLIC METHODS ########

    def cConfigure(self, evalMetrics):

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
            if evalMetrics[key][0] != "MAX" and evalMetrics[key][0] != "MIN":
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

    def cPreprocess(self, metricSamples, correlationLevel = 0.95):

        correlatedBiases = {key:[] for key in self.__evalMetrics.keys()}
        linearInspection = self.__cPearson(metricSamples)

        for inspection in linearInspection:
            if abs(linearInspection[inspection][0]) >= correlationLevel:
                if linearInspection[inspection][0] > 0:
                    correlatedBiases[inspection[0]].append(inspection[1])
                    correlatedBiases[inspection[1]].append(inspection[0])

        nonBiasesWeights = self.__cBias(correlatedBiases)
        for metric in nonBiasesWeights:
            self.__evalMetrics[metric] = (self.__evalMetrics[metric][0], nonBiasesWeights[metric])

    def cEvaluate(self, partialResults):

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

        return self.__cSI()

    def getStatus(self):
        return self.__status

    def getIndexing(self):
        return self.__lastIndexing

    def getPartialResults(self):
        return self.__partialResults

    def getEvalMetrics(self):
        return self.__evalMetrics

################ CHEF CLASS END #################