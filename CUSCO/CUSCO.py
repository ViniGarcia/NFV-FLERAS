######## CUSCO CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service)
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A VALID SFC REQUEST AND EXECUTES A FULL
#COMPOSITION EVALUATION (MADE WITH THE GOAL FUNCTION
#CLASS), CREATING INDEXES FOR EVERY AVAILABLE SFC
#TOPOLOGY (RETRIVED FROM THE SFC TOPOLOGY CLASS).

#THE CLASS STATUS ATTRIBUTE INDICATE ITS
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: NO TOPOLOGY EXPANDED
#1: SFC TOPOLOGIES READY TO BE ANALYZED
#2: SFC TOPOLOGIES ALREADY ANALYZED

#################################################

import copy

from CUSCO.CUSCOExpansion import CUSCOExpansion
from CUSCO.CUSCOFunction import CUSCOFunction
from CHEF.CHEF import CHEF

class CUSCO:
	__status = None

	__sfcRequest = None
	__sfcOriginal = None
	__sfcDictionary = None

	__oElementsData = None
	__branchesData = None

	__aggregateDictionary = None
	__indexesDictionary = None

	__chef = None

	######## CONSTRUCTOR ########

	def __init__(self, sfcRequest, sfcTopology):

		if sfcRequest != None and sfcTopology != None:
			self.scSetup(sfcRequest, sfcTopology)
		else:
			self.__status = 0

	######## PRIVATE METHODS ########

	def __scDependenciesRemove(self):

		for key in self.__sfcDictionary:

			while '<' in self.__sfcDictionary[key]:
				iIndex = self.__sfcDictionary[key].index('<')
				fIndex = self.__sfcDictionary[key].index('>')
				self.__sfcDictionary[key] = self.__sfcDictionary[key][0:iIndex] + self.__sfcDictionary[key][fIndex+2:len(self.__sfcDictionary[key])]

	def __scBranchesPrepare(self):

		sfcBranches = self.__sfcRequest.ycFunctionBranches()
		branchUpdate = {}
		branchFactors = []

		if len(sfcBranches) > 0:

			metricKeys = list(sfcBranches.keys())
			for metric in metricKeys:
				branchUpdate[metric] = sfcBranches[metric]["UPDATE"]

			for branchIndex in range(len(sfcBranches[metricKeys[0]]["FACTORS"])):
				branchStructure = []
				for factorIndex in range(len(sfcBranches[metricKeys[0]]["FACTORS"][branchIndex])):
					segmentDict = {}
					for metric in metricKeys:
						segmentDict[metric] = sfcBranches[metric]["FACTORS"][branchIndex][factorIndex]
					branchStructure.append(segmentDict)
				branchFactors.append(branchStructure)

		self.__branchesData = (branchUpdate, branchFactors)

	def __scOElementsPrepare(self):

		sfcOElements = self.__sfcRequest.ycServiceBechmark()
		self.__oElementsData = {}

		for OE in sfcOElements:
			self.__oElementsData[OE["ID"]] = OE

	def __scCHEFPrepare(self):

		cuscoMetrics = self.__sfcRequest.ycFunction()["METRICS"]
		chefMetrics = {}
		for metric in cuscoMetrics:
			chefMetrics[metric["ID"]] = (metric["GOAL"], metric["WEIGHT"])
		self.__chef = CHEF(chefMetrics)

	def __scEvaluateSingle(self, index):

		activeInstance = CUSCOFunction(self.__sfcRequest)
		funcInstances = [activeInstance]
		funcSaves = []
		actualBranch = 0
		actualSegment = 0
		nextBranch = 1

		sfcElements = self.__sfcDictionary[index].split()
		boundaryEPs = self.__sfcRequest.ycServiceON()

		for eIndex in range(1, len(sfcElements)):

			if sfcElements[eIndex] == '{':
				funcSaves.append((actualBranch, actualSegment))
				actualBranch = nextBranch
				actualSegment = 0
				nextBranch += 1

				newInstance = CUSCOFunction(None)
				newInstance.cfBranchSetup(activeInstance.cfFunction(), self.__branchesData[0], self.__branchesData[1][actualBranch-1][actualSegment])
				funcInstances.append(newInstance)
				activeInstance = newInstance
				continue

			if sfcElements[eIndex] == '}':
				segmentsList = []
				for turn in range(actualSegment+1):
					segmentsList.insert(0, funcInstances.pop())

				activeInstance = funcInstances[-1]
				activeInstance.cfBranchUnify(segmentsList)

				save = funcSaves.pop()
				actualBranch = save[0]
				actualSegment = save[1]
				continue

			if sfcElements[eIndex] == '/':
				actualSegment += 1

				newInstance = CUSCOFunction(None)
				newInstance.cfBranchSetup(funcInstances[(actualSegment+1)*-1].cfFunction(), self.__branchesData[0], self.__branchesData[1][actualBranch-1][actualSegment])
				funcInstances.append(newInstance)
				activeInstance = newInstance
				continue

			if not sfcElements[eIndex] in boundaryEPs:
				activeInstance.cfProcess(self.__oElementsData[sfcElements[eIndex]])

		self.__aggregateDictionary[index] = activeInstance.cfAggregation()

	######## PUBLIC METHODS ########

	def scSetup(self, sfcRequest, sfcTopology):

		self.__sfcRequest = sfcRequest
		self.__sfcOriginal = {}
		self.__sfcDictionary = {}

		sfcList = CUSCOExpansion(sfcTopology).ceBranches()
		for index in range(len(sfcList)):
			self.__sfcOriginal[index] = sfcList[index]
			self.__sfcDictionary[index] = sfcList[index]

		self.__scDependenciesRemove()
		self.__scBranchesPrepare()
		self.__scOElementsPrepare()
		self.__scCHEFPrepare()

		self.__status = 1

	def scEvaluate(self):

		if self.__status != 1:
			return

		self.__aggregateDictionary = {}
		for index in self.__sfcDictionary:
			self.__scEvaluateSingle(index)

		self.__indexesDictionary = self.__chef.cEvaluate(self.__aggregateDictionary)

		self.__status = 2

	def scSFCKeys(self):

		if self.__status != 1:
			return None

		return self.__sfcOriginal

	def scSFCIndexes(self):

		if self.__status != 2:
			return None

		resultList = []
		for key in self.__sfcDictionary:
			resultList.append((self.__sfcOriginal[key], self.__indexesDictionary[key]))

		return resultList

	def scSFCBest(self):

		if self.__status != 2:
			return None

		key = max(self.__indexesDictionary, key = self.__indexesDictionary.get)
		return self.__sfcOriginal[key]

	def scAggregation(self):

		if self.__status != 2:
			return None

		return self.__aggregateDictionary

	def scIndexes(self):

		if self.__status != 2:
			return None

		return self.__indexesDictionary

	def scStatus(self):

		return self.__status

######## CUSCO CLASS END ########
