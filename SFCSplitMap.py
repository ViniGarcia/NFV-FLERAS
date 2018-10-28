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

	__processor = None

	######## CONSTRUCTOR ########

	def __init__(self, sfcRequest, domData):
		
		if sfcRequest != None and domData != None:
			self.ssamSetup(sfcRequest, domData)
		else:
			self.__status = 0

	######## PRIVATE METHODS ########

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

	######## PUBLIC METHODS ########

	def ssamSetup(self, sfcRequest, domData):

		self.__sfcRequest = sfcRequest
		self.__domData = domData

		self.__ssamCreateMatrix()
		if self.__ssamCheckDomains():
			if self.__ssamCheckPolicies():
				self.__ssamOrganizeData() 
				self.__status = 1

	def ssamOptimalRequest(self, topologiesList):

		if self.__status < 1:
			return

		self.__processor = OptimalSM(self.__immediateDictionary, self.__aggregateDictionary, self.__flavoursDictionary, self.__domMatrix)

		for topology in topologiesList:
			if self.__ssamCheckTopology(topology):
				topoData = self.__ssamPreprocessTopology(topology)
				self.__processor.osmProcess(self.__sfcRequest.srServiceOE(), topoData[0], topoData[1])

	def ssamStatus(self):

		return self.__status


######## SFC SPLIT MAP CLASS END ########

#TESTS -> PARTIALLY IMPLEMENTED (ON DEVELOPMENT)
domains = DomainsData("Example/DomExample01.yaml")
request = SFCRequest('Example/ReqExample06.yaml', domains.ddDomains().copy())
mapping = SFCSplitAndMap(request, domains)
mapping.ssamOptimalRequest(["IP NF1 < D01 > NF2 NF3 ON1"])