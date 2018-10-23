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

#################################################

from SFCRequest import SFCRequest
from DomainsData import DomainsData

class SFCSplitAndMap:
	__status = None

	__sfcRequest = None
	__domData = None

	__domMatrix = None
	__domTopologies = None

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

	######## PUBLIC METHODS ########

	def ssamStatus(self):

		return self.__status

	def ssamSetup(self, sfcRequest, domData):

		self.__sfcRequest = sfcRequest
		self.__domData = domData

		self.__domMatrix = self.__ssamCreateMatrix()
		if self.__ssamCheckDomains():
			self.__status = 1


######## SFC SPLIT MAP CLASS END ########

# TESTS -> PARTIALLY IMPLEMENTED (ON DEVELOPMENT)
# domains = DomainsData("Example/DomExample01.yaml")
# request = SFCRequest('Example/ReqExample03.yaml', domains.ddDomains().copy())
# mapping = SFCSplitAndMap(request, domains)
# print(mapping.ssamStatus())