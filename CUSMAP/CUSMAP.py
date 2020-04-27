######## CUSMAP CLASS DESCRIPTION ########

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

from CUSMAP.OptimalSM import OptimalSM
from CHEF.CHEF import CHEF

class CUSMAP:
	__status = None

	__sfcRequest = None
	__domRequest = None
	__domMatrix = None
	
	__chef = None
	__evaluations = None

	__immediateDictionary = None
	__aggregateDictionary = None
	__flavoursDictionary = None

	######## CONSTRUCTOR ########

	def __init__(self, sfcRequest, domRequest):

		if sfcRequest != None and domRequest != None:
			self.smSetup(sfcRequest, domRequest)
		else:
			self.__status = 0

	######## PRIVATE VALIDATION METHODS ########

	def __smCreateMatrix(self):

		domains = self.__domRequest.ddDomains()
		resources = self.__domRequest.ddResources()
		local = self.__domRequest.ddLocalValues()
		transition = self.__domRequest.ddTransitionValues()

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

	def __smCheckDomains(self):

		if set(self.__sfcRequest.erDomains()) <= set(self.__domRequest.ddDomains()):
			return True
		else:
			self.__status = -1
			return False

	def __smCheckPolicies(self):

		requestPolicies = self.__sfcRequest.erPoliciesMetrics()
		domainsLMetrics = self.__domRequest.ddLocalMetrics()
		domainsTMetrics = self.__domRequest.ddTransitionMetrics()

		if set(requestPolicies["DOMAIN"]) <= set(domainsLMetrics):
			if set(requestPolicies["TRANSITION"]) <= set(domainsTMetrics):
				return True
			else:
				self.__status = -3
				return False
		else:
			self.__status = -2
			return False

	def __smCheckTopology(self, topology):

		validSymbols = self.__sfcRequest.erServiceOE() + self.__sfcRequest.erServiceON() + self.__sfcRequest.erDomains() + ['<', '>', '{', '}', '/', 'IP']
		splittedTopo = topology.split()

		for symbol in splittedTopo:
			if not symbol in validSymbols:
				return False

		return True

	def __smPrepareData(self):

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

	def __smPrepareCHEF(self):

		cusmapMetrics = self.__sfcRequest.erPolicies()
		chefMetrics = {}
		for metric in cusmapMetrics["AGGREGATE"]:
			chefMetrics[metric["ID"]] = (metric["GOAL"], metric["WEIGHT"])
		self.__chef = CHEF(chefMetrics)

	def __smPreprocessTopology(self, topology):

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

	######## PUBLIC METHODS ########

	def smSetup(self, sfcRequest, domRequest):

		self.__sfcRequest = sfcRequest
		self.__domRequest = domRequest

		self.__smCreateMatrix()
		if self.__smCheckDomains():
			if self.__smCheckPolicies():
				self.__smPrepareCHEF()
				self.__smPrepareData()
				self.__status = 1

	def smEvaluate(self):

		if self.__status < 1:
			return

		evaluations = {}
		processor = OptimalSM(self.__immediateDictionary, self.__aggregateDictionary, self.__flavoursDictionary, self.__domMatrix)
		if self.__smCheckTopology(self.__sfcRequest.erServiceTopology()):
			arguments = self.__smPreprocessTopology(self.__sfcRequest.erServiceTopology())
			processor.osmProcess(self.__sfcRequest.erServiceOE(), self.__sfcRequest.erServiceON(), arguments[0], arguments[1])
			evaluations[self.__sfcRequest.erServiceTopology()] = processor.osmEvaluation()
		else:
			self.__status = -4
			return

		if len(evaluations[self.__sfcRequest.erServiceTopology()]["DIST"]) == 0:
			return

		partial = {}
		aggregations = evaluations[self.__sfcRequest.erServiceTopology()]
		for index in range(len(aggregations["AGG"])):
			partial[aggregations["DIST"][index]] = aggregations["AGG"][index]["AGGREGATE"]
		self.__evaluations = self.__chef.cEvaluate(partial)
		self.__status = 2

	def smKeys(self):

		if self.__status != 2:
			return None

		return list(self.__evaluations.keys())

	def smIndexes(self):

		if self.__status != 2:
			return None

		return self.__evaluations

	def smBest(self):

		if self.__status != 2:
			return None

		mapping = max(self.__evaluations.items(), key=lambda x: x[1])[0]
		base = self.__sfcRequest.erServiceTopology().split()
		result = base.copy()
		offload = 0

		for index in range(len(base)):
			if base[index] in self.__sfcRequest.erServiceOE():
				if base[index + 1] != "<":
					result.insert(index + offload + 1, "<")
					result.insert(index + offload + 2, mapping[int(offload/3)])
					result.insert(index + offload + 3, ">")
					offload += 3

		return " ".join(result)

	def smStatus(self):

		return self.__status


######## CUSMAP CLASS END ########