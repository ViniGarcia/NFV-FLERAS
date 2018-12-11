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

from itertools import islice

from SFCRequest import SFCRequest
from DomainsData import DomainsData
from OptimalSM import OptimalSM

class SFCSplitAndMap:
	__status = None

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

		if set(self.__sfcRequest.srDomains()) <= set(self.__domData.ddDomains()):
			return True
		else:
			self.__status = -1
			return False

	def __ssamCheckPolicies(self):

		requestPolicies = self.__sfcRequest.srPoliciesMetrics()
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

		validSymbols = self.__sfcRequest.srServiceOE() + self.__sfcRequest.srServiceON() + self.__sfcRequest.srDomains() + ['<', '>', '{', '}', '/', 'IP']
		splittedTopo = topology.split()
		
		for symbol in splittedTopo:
			if not symbol in validSymbols:
				return False

		return True

	def __ssamOrganizeData(self):

		immPolicies = {"LOCAL": {}, "TRANSITION":{}}
		aggPolicies = {"LOCAL": {}, "TRANSITION":{}}
		rawPolicies = self.__sfcRequest.srPolicies()

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
		self.__flavoursDictionary = self.__sfcRequest.srServiceFlavours()

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

		evaluations['DAI'] = indexes
		return indexes

	def __ssamHarmonizeIndexes(self, topologiesList, TAI, DAI):

		UI = {}
		for topology in topologiesList:
			UI[topology] = []

			for evaluation in DAI[topology]:
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
				processor.osmProcess(self.__sfcRequest.srServiceOE(), arguments[0], arguments[1])
				evaluations[topology] = processor.osmEvaluation()
			else:
				self.__status = -4
				return

		normalizations = self.__ssamNormalizeEvaluations(evaluations)
		DAI = self.__ssamGenerateIndex(evaluations, normalizations)

		if topoligiesTAI != None:
			
			TAI = {}
			for index in range(len(topologiesList)):
				TAI[topologiesList[index]] = topoligiesTAI[index]
			UI = self.__ssamHarmonizeIndexes(topologiesList, TAI, DAI)
			print(UI)

		self.__status = 2

	def ssamStatus(self):

		return self.__status

######## SFC SPLIT MAP CLASS END ########

#TESTS -> PARTIALLY IMPLEMENTED (ON DEVELOPMENT)
#domains = DomainsData("Example/DomExample03.yaml")
#request = SFCRequest('Example/ReqExample15.yaml', domains.ddDomains().copy())
#mapping = SFCSplitAndMap(request, domains)
#mapping.ssamOptimalRequest(["IP EO2 EO1 < DOM3 > { EO3 NS1 / EO4 NS2 }","IP EO1 < DOM3 > { EO2 EO3 NS1 / EO2 EO4 NS2 }"], [0.5, 0.8])