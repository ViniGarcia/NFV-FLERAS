######## SFC SPLIT MAP CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service)
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A VALID SFC REQUEST, SFC COMPOSITIONS AND
#DOMAINS DATA TO EXECUTE A SPLITTING AND MAPPING
#TECNIQUE. THE EVALUATION CONSIDERS A SERIES OF
#POLICIES AND FLAVOURS (RETRIEVED FROM THE REQUEST)
#TO CHOOSE THE BEST INTEGRTION DOMAINS BY USING A
#CENTRALIZED ALGORITHM.

#THE CLASS STATUS ATTRIBUTE INDICATE ITS
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: DOMAINS AND REQUEST MUST BE INFORMED
#1: READY TO SPLIT AND MAP TOPOLOGIES

#ERROR CODES ->
#-1: UNKNOW DOMAINS PRESENT IN REQUEST LIST
#-2: UNKNOW DOMAIN POLICY METRIC IN REQUEST
#-3: UNKNOW TRANSITION POLICY METRIC IN REQUEST
#-4: INVALID SYMBOL IN A PROVIDED TOPOLOGY

#################################################
import numpy
from itertools import islice

from YAMLR.EmbeddingRequest import EmbeddingRequest
from YAMLR.DomainsData import DomainsData
from CUSMAP.OptimalSM import OptimalSM

class SFCSplitAndMap:
	__status = None
	__summary = None
	__evaluations = None

	__sfcRequest = None
	__domData = None

	__domMatrix = None
	__domTopologies = None

	__immediateDictionary = None
	__aggregateDictionary = None
	__flavoursDictionary = None

	######## CONSTRUCTOR ########

	def __init__(self, sfcRequest, domData):

		if sfcRequest != None and domData != None:
			self.ssamSetup(sfcRequest, domData)
		else:
			self.__status = 0

	######## PRIVATE DEBBUGING METHODS ########

	def __ssamGenerateReport(self, evaluations, normalizations, DSI):

		bestIndexes = []
		idNr = 0
		self.__summary = ""

		if evaluations != None and normalizations != None and DSI != None:
			for key in evaluations:
				if key == "DSI":
					continue

				DAIbestIndex = 0
				DAIbestIDs = []

				for dIndex in range(len(evaluations[key]["DIST"])):
					self.__summary += str(idNr) + "-" + key + "/" + str(evaluations[key]["DIST"][dIndex]) + ":\n"
					self.__summary += "  AGGREGATE(ABS) ->\n"
					for metric in evaluations[key]["AGG"][dIndex]["AGGREGATE"]:
						self.__summary += "    " + metric + ":" + str(evaluations[key]["AGG"][dIndex]["AGGREGATE"][metric]) + "\n"
					self.__summary += "  IMMEDIATE(ABS) ->\n"
					for metric in evaluations[key]["AGG"][dIndex]["IMMEDIATE"]:
						self.__summary += "    " + metric + ":" + str(evaluations[key]["AGG"][dIndex]["IMMEDIATE"][metric]) + "\n"
					self.__summary += "  AGGREGATE(NOR) ->\n"
					for metric in normalizations[key]["AGGREGATE"]:
						self.__summary += "    " + metric + ":" + str(normalizations[key]["AGGREGATE"][metric][dIndex]) + "\n"
					self.__summary += "  IMMEDIATE(NOR) ->\n"
					for metric in normalizations[key]["IMMEDIATE"]:
						self.__summary += "    " + metric + ":" + str(normalizations[key]["IMMEDIATE"][metric][dIndex]) + "\n"
					self.__summary += "  DSI -> " + str(DSI[key][dIndex]) + "\n"

					if DAIbestIndex == DSI[key][dIndex]:
						DAIbestIDs.append(idNr)
					else:
						if DAIbestIndex < DSI[key][dIndex]:
							DAIbestIndex = DSI[key][dIndex]
							DAIbestIDs = [idNr]
					idNr += 1

				bestIndexes.append({"TOPOLOGY":key, "DSI":DAIbestIndex, "DSIDIST":DAIbestIDs})

			self.__summary += "\n------ BEST INDEXES SUMMARY ------\n"
			for summary in bestIndexes:
				self.__summary += str(summary) + "\n"
			self.__summary += "-----------------------------------"

	######## PRIVATE VALIDATION METHODS ########

	def __ssamCreateMatrix(self):

		domains = self.__domData.ddDomains()
		resources = self.__domData.ddResources()
		local = self.__domData.ddLocalValues()
		transition = self.__domData.ddTransitionValues()

		baseDictionary = {}
		for key in domains:
			baseDictionary[key] = None

		self.__domMatrix = {}
		for key in domains:
			self.__domMatrix[key] = baseDictionary.copy()

		for key in domains:
			for iKey in domains:
				if key == iKey:
					selfLocal = {}
					for metric in local:
						selfLocal[metric] = local[metric][key]
					self.__domMatrix[key][key] = {"RESOURCES":resources[key], "LOCAL":selfLocal}
				else:
					selfTransition = {}
					for metric in transition:
						if iKey in transition[metric][key]:
							selfTransition[metric] = transition[metric][key][iKey]
						else:
							selfTransition[metric] = None
					self.__domMatrix[key][iKey] = selfTransition

	def __ssamCheckDomains(self):

		if set(self.__sfcRequest.erDomains()) <= set(self.__domData.ddDomains()):
			return True
		else:
			self.__status = -1
			return False

	def __ssamCheckPolicies(self):

		requestPolicies = self.__sfcRequest.erPoliciesMetrics()
		domainsLMetrics = self.__domData.ddLocalMetrics()
		domainsTMetrics = self.__domData.ddTransitionMetrics()

		if set(requestPolicies["DOMAIN"]) <= set(domainsLMetrics):
			if set(requestPolicies["TRANSITION"]) <= set(domainsTMetrics):
				return True
			else:
				self.__status = -3
				return False
		else:
			self.__status = -2
			return False

	def __ssamCheckTopology(self, topology):

		validSymbols = self.__sfcRequest.erServiceOE() + self.__sfcRequest.erServiceON() + self.__sfcRequest.erDomains() + ['<', '>', '{', '}', '/', 'IP']
		splittedTopo = topology.split()

		for symbol in splittedTopo:
			if not symbol in validSymbols:
				return False

		return True

	def __ssamOrganizeData(self):

		immPolicies = {"LOCAL": {}, "TRANSITION":{}}
		aggPolicies = {"LOCAL": {}, "TRANSITION":{}}
		rawPolicies = self.__sfcRequest.erPolicies()

		for policy in rawPolicies["IMMEDIATE"]:
			if policy["TYPE"] == "DOMAIN":
				immPolicies["LOCAL"][policy["ID"]] = policy
			if policy["TYPE"] == "TRANSITION":
				immPolicies["TRANSITION"][policy["ID"]] = policy

		for policy in rawPolicies["AGGREGATE"]:
			if policy["TYPE"] == "DOMAIN":
				aggPolicies["LOCAL"][policy["ID"]] = policy
			if policy["TYPE"] == "TRANSITION":
				aggPolicies["TRANSITION"][policy["ID"]] = policy

		self.__immediateDictionary = immPolicies
		self.__aggregateDictionary = aggPolicies
		self.__flavoursDictionary = self.__sfcRequest.erServiceFlavours()

	def __ssamPreprocessTopology(self, topology):

		dependencies = {}
		cleanedTopo = []
		splittedTopo = topology.split()

		iterator = iter(range(len(splittedTopo)))
		for index in iterator:
			if splittedTopo[index] == '<':
				dependencies[len(cleanedTopo)-1] = [splittedTopo[index+1]]
				next(islice(iterator, 2, 2), None)
			else:
				cleanedTopo.append(splittedTopo[index])

		return [cleanedTopo, dependencies]

	######## PRIVATE EVALUATION METHODS ########

	def __ssamParetoFront(self, aggregations):

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

	def __ssamPreprocessEvaluations(self, evaluations):

		preprocess = {}

		for topology in evaluations:
			policies = {'AGGREGATE':{}, 'IMMEDIATE':{}}
			if len(evaluations[topology]['AGG']) > 0:
				for policy in evaluations[topology]['AGG'][0]['AGGREGATE'].keys():
					policies['AGGREGATE'][policy] = []
				for policy in evaluations[topology]['AGG'][0]['IMMEDIATE'].keys():
					policies['IMMEDIATE'][policy] = []

				for combination in evaluations[topology]['AGG']:
					for policy in combination['AGGREGATE']:
						policies['AGGREGATE'][policy].append(combination['AGGREGATE'][policy])
					for policy in combination['IMMEDIATE']:
						policies['IMMEDIATE'][policy].append(combination['IMMEDIATE'][policy])

			preprocess[topology] = policies

		return preprocess

	def __ssamNormalizeEvaluations(self, evaluations):

		normalizations = self.__ssamPreprocessEvaluations(evaluations)
		iterations = {'AGGREGATE':list(normalizations[list(normalizations.keys())[0]]['AGGREGATE'].keys()), 'IMMEDIATE':list(normalizations[list(normalizations.keys())[0]]['IMMEDIATE'].keys())}

		for category in iterations:
			for policy in iterations[category]:
				globalMax = None
				globalMin = None

				for topology in normalizations:
					if globalMax == None:
						globalMax = max(normalizations[topology][category][policy])
						globalMin = min(normalizations[topology][category][policy])
					else:
						if max(normalizations[topology][category][policy]) > globalMax:
							globalMax = max(normalizations[topology][category][policy])
						if min(normalizations[topology][category][policy]) < globalMin:
							globalMin = min(normalizations[topology][category][policy])

				absDistance = globalMax - globalMin
				if absDistance != 0:
					for topology in normalizations:
						for index in range(len(normalizations[topology][category][policy])):
							normalizations[topology][category][policy][index] = (normalizations[topology][category][policy][index] - globalMin) / absDistance
				else:
					for topology in normalizations:
						for index in range(len(normalizations[topology][category][policy])):
							normalizations[topology][category][policy][index] = 0

		return normalizations

	def __ssamGenerateIndex(self, evaluations, normalizations):

		indexes = {}
		for topology in evaluations:

			indexes[topology] = [0 for i in range(len(evaluations[topology]['DIST']))]

			for category in self.__immediateDictionary:
				for policy in self.__immediateDictionary[category]:
					for index in range(len(normalizations[topology]["IMMEDIATE"][policy])):
						if self.__immediateDictionary[category][policy]['GOAL'] == 'MIN':
							normalizations[topology]["IMMEDIATE"][policy][index] = (1 - normalizations[topology]["IMMEDIATE"][policy][index]) * self.__immediateDictionary[category][policy]['WEIGHT']
						else:
							normalizations[topology]["IMMEDIATE"][policy][index] = normalizations[topology]["IMMEDIATE"][policy][index] * self.__immediateDictionary[category][policy]['WEIGHT']
						indexes[topology][index] += normalizations[topology]["IMMEDIATE"][policy][index]

			for category in self.__aggregateDictionary:
				for policy in self.__aggregateDictionary[category]:
					for index in range(len(normalizations[topology]["AGGREGATE"][policy])):
						if self.__aggregateDictionary[category][policy]['GOAL'] == 'MIN':
							normalizations[topology]["AGGREGATE"][policy][index] = (1 - normalizations[topology]["AGGREGATE"][policy][index]) * self.__aggregateDictionary[category][policy]['WEIGHT']
						else:
							normalizations[topology]["AGGREGATE"][policy][index] = normalizations[topology]["AGGREGATE"][policy][index] * self.__aggregateDictionary[category][policy]['WEIGHT']
						indexes[topology][index] += normalizations[topology]["AGGREGATE"][policy][index]

		evaluations['DSI'] = indexes
		return indexes

	def __ssamHarmonizeIndexes(self, topologiesList, TAI, DSI):

		UI = {}
		for topology in topologiesList:
			UI[topology] = []

			for evaluation in DSI[topology]:
				UI[topology].append((evaluation + TAI[topology])/2)

		return UI


	######## PUBLIC METHODS ########

	def ssamSetup(self, sfcRequest, domData):

		self.__sfcRequest = sfcRequest
		self.__domData = domData

		self.__ssamCreateMatrix()
		if self.__ssamCheckDomains():
			if self.__ssamCheckPolicies():
				self.__ssamOrganizeData()
				self.__status = 1

	def ssamOptimalRequest(self, topologiesList, topoligiesTAI):

		if self.__status < 1:
			return

		evaluations = {}
		processor = OptimalSM(self.__immediateDictionary, self.__aggregateDictionary, self.__flavoursDictionary, self.__domMatrix)
		for topology in topologiesList:
			if self.__ssamCheckTopology(topology):
				arguments = self.__ssamPreprocessTopology(topology)
				processor.osmProcess(self.__sfcRequest.erServiceOE(), self.__sfcRequest.erServiceON(), arguments[0], arguments[1])
				evaluations[topology] = processor.osmEvaluation()
			else:
				self.__status = -4
				return

		normalizations = self.__ssamNormalizeEvaluations(evaluations)
		DSI = self.__ssamGenerateIndex(evaluations, normalizations)

		if topoligiesTAI != None:

			TAI = {}
			for index in range(len(topologiesList)):
				TAI[topologiesList[index]] = topoligiesTAI[index]
			UI = self.__ssamHarmonizeIndexes(topologiesList, TAI, DSI)

		self.__ssamGenerateReport(evaluations, normalizations, DSI, UI)
		self.__status = 3
		self.__evaluations = evaluations

	def ssamNaturalRequest(self):

		if self.__status < 1:
			return

		evaluations = {}
		processor = OptimalSM(self.__immediateDictionary, self.__aggregateDictionary, self.__flavoursDictionary, self.__domMatrix)
		if self.__ssamCheckTopology(self.__sfcRequest.erServiceTopology()):
			arguments = self.__ssamPreprocessTopology(self.__sfcRequest.erServiceTopology())
			processor.osmProcess(self.__sfcRequest.erServiceOE(), self.__sfcRequest.erServiceON(), arguments[0], arguments[1])
			evaluations[self.__sfcRequest.erServiceTopology()] = processor.osmEvaluation()
		else:
			self.__status = -4
			return

		if len(evaluations[self.__sfcRequest.erServiceTopology()]["DIST"]) == 0:
			return

		normalizations = self.__ssamNormalizeEvaluations(evaluations)
		DSI = self.__ssamGenerateIndex(evaluations, normalizations)

		self.__ssamGenerateReport(evaluations, normalizations, DSI)
		self.__status = 2
		self.__evaluations = evaluations

	def ssamStatus(self):

		return self.__status

	def ssamKeys(self):

		if self.__status != 2:
			return None

		return self.__evaluations[self.__sfcRequest.erServiceTopology()]["DIST"]

	def ssamAggregations(self):

		if self.__status != 2:
			return None

		return self.__evaluations[self.__sfcRequest.erServiceTopology()]["AGG"]

	def ssamIndexes(self):

		if self.__status != 2:
			return None

		return self.__evaluations["DSI"][self.__sfcRequest.erServiceTopology()]

	def ssamFrontiers(self):

		if self.__status != 2:
			return None

		maps = self.ssamKeys()
		sis = self.ssamIndexes()
		agg = self.ssamAggregations()

		paretoList = []
		for index in range(len(maps)):
			candidateList = []
			for ptype in ["AGGREGATE", "IMMEDIATE"]:
				for metric in agg[index][ptype]:
					candidateList.append(agg[index][ptype][metric])
			paretoList.append(candidateList)
		
		return self.__ssamParetoFront(paretoList)

	def ssamAdvice(self):

		if self.__status != 2:
			return None

		key = self.__evaluations["DSI"][self.__sfcRequest.erServiceTopology()].index(max(self.__evaluations["DSI"][self.__sfcRequest.erServiceTopology()]))
		base = self.__sfcRequest.erServiceTopology().split()
		result = base.copy()
		offload = 0

		for index in range(len(base)):
			if base[index] in self.__sfcRequest.erServiceOE():
				if base[index + 1] != "<":
					result.insert(index + offload + 1, "<")
					result.insert(index + offload + 2, self.__evaluations[self.__sfcRequest.erServiceTopology()]["DIST"][key][int(offload/3)])
					result.insert(index + offload + 3, ">")
					offload += 3

		return " ".join(result)

	def ssamSummary(self):

		if self.__status != 2:
			return None

		return self.__summary


######## SFC SPLIT MAP CLASS END ########

#TESTS -> PARTIALLY IMPLEMENTED (ON DEVELOPMENT)
#domains = DomainsData("../Example/DomExample04.yaml")
#request = EmbeddingRequest('../Example/EmbReqExample01.yaml', domains.ddDomains().copy())
#mapping = SFCSplitAndMap(request, domains)
#mapping.ssamNaturalRequest()
#mapping.ssamOptimalRequest(["IP EO2 EO1 < DOM3 > { EO3 NS1 / EO4 NS2 }","IP EO1 < DOM3 > { EO2 EO3 NS1 / EO2 EO4 NS2 }"], [0.5, 0.8])
