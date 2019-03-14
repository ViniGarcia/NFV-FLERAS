######## SFC COMPOSITION CLASS DESCRIPTION ########

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

from YAMLR.SFCRequest import SFCRequest
from STOG.SFCTopology import SFCTopology
from CUSCO.SFCExpansion import SFCExpansion
from CUSCO.GoalFunction import GoalFunction

class SFCComposition:
	__status = None

	__sfcRequest = None
	__sfcOriginal = None
	__sfcDictionary = None

	__oElementsData = None
	__branchesData = None

	__aggregateDictionary = None
	__normalizedDicitionary = None
	__indexesDictionary = None

	######## CONSTRUCTOR ########

	def __init__(self, sfcRequest, sfcList):

		if sfcRequest != None and sfcList != None:
			self.scSetup(sfcRequest, sfcList)
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

		sfcBranches = self.__sfcRequest.srFunctionBranches()
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

		sfcOElements = self.__sfcRequest.srServiceBechmark()
		self.__oElementsData = {}

		for OE in sfcOElements:
			self.__oElementsData[OE["ID"]] = OE

	def __scEvaluateSingle(self, index):

		activeInstance = GoalFunction(self.__sfcRequest)
		funcInstances = [activeInstance]
		funcSaves = []
		actualBranch = 0
		actualSegment = 0
		nextBranch = 1

		sfcElements = self.__sfcDictionary[index].split()
		boundaryEPs = self.__sfcRequest.srServiceON()

		for eIndex in range(1, len(sfcElements)):

			if sfcElements[eIndex] == '{':
				funcSaves.append((actualBranch, actualSegment))
				actualBranch = nextBranch
				actualSegment = 0
				nextBranch += 1

				newInstance = GoalFunction(None)
				newInstance.gfBranchSetup(activeInstance.gfFunction(), self.__branchesData[0], self.__branchesData[1][actualBranch-1][actualSegment])
				funcInstances.append(newInstance)
				activeInstance = newInstance
				continue

			if sfcElements[eIndex] == '}':
				segmentsList = []
				for turn in range(actualSegment+1):
					segmentsList.insert(0, funcInstances.pop())

				activeInstance = funcInstances[-1]
				activeInstance.gfBranchUnify(segmentsList)

				save = funcSaves.pop()
				actualBranch = save[0]
				actualSegment = save[1]
				continue

			if sfcElements[eIndex] == '/':
				actualSegment += 1

				newInstance = GoalFunction(None)
				newInstance.gfBranchSetup(funcInstances[(actualSegment+1)*-1].gfFunction(), self.__branchesData[0], self.__branchesData[1][actualBranch-1][actualSegment])
				funcInstances.append(newInstance)
				activeInstance = newInstance
				continue

			if not sfcElements[eIndex] in boundaryEPs:
				activeInstance.gfProcess(self.__oElementsData[sfcElements[eIndex]])

		self.__aggregateDictionary[index] = activeInstance.gfAggregation()

	def __scBoundaryFactor(self):

		factorList = {}
		maximum = copy.deepcopy(self.__aggregateDictionary[0])
		minimum = copy.deepcopy(self.__aggregateDictionary[0])

		for index in range(1, len(self.__aggregateDictionary)):
			for metric in self.__aggregateDictionary[index]:
				if maximum[metric] < self.__aggregateDictionary[index][metric]:
					maximum[metric] = self.__aggregateDictionary[index][metric]
					continue
				if minimum[metric] > self.__aggregateDictionary[index][metric]:
					minimum[metric] = self.__aggregateDictionary[index][metric]

		for metric in maximum:
			factorList[metric] = maximum[metric] - minimum[metric]

		return (factorList, maximum, minimum)

	def __scNormalizeAggregations(self):

		boundaryData = self.__scBoundaryFactor()
		boundaryFactor = boundaryData[0]
		boundaryMin = boundaryData[2]

		for index in self.__normalizedDicitionary:
			for metric in boundaryFactor:
				if boundaryFactor[metric] != 0:
					self.__normalizedDicitionary[index][metric] = (self.__normalizedDicitionary[index][metric] - boundaryMin[metric]) / boundaryFactor[metric]
				else:
					self.__normalizedDicitionary[index][metric] = 0

	def __scWeightNormalizations(self):

		weights = self.__sfcRequest.srFunctionWeights()
		goals = self.__sfcRequest.srFunctionGoals()

		for index in self.__normalizedDicitionary:
			sfcIndex = 0
			for metric in weights:
				if goals[metric] == "MIN":
					sfcIndex += (1 - self.__normalizedDicitionary[index][metric]) * weights[metric]
					continue
				if goals[metric] == "MAX":
					sfcIndex += self.__normalizedDicitionary[index][metric] * weights[metric]
			self.__indexesDictionary[index] = sfcIndex

	######## PUBLIC METHODS ########

	def scSetup(self, sfcRequest, sfcList):

		self.__sfcRequest = sfcRequest
		self.__sfcOriginal = {}
		self.__sfcDictionary = {}
		for index in range(len(sfcList)):
			self.__sfcOriginal[index] = sfcList[index]
			self.__sfcDictionary[index] = sfcList[index]
		self.__scDependenciesRemove()
		self.__scBranchesPrepare()
		self.__scOElementsPrepare()

		self.__status = 1

	def scEvaluate(self):

		if self.__status != 1:
			return

		self.__aggregateDictionary = {}
		for index in self.__sfcDictionary:
			self.__scEvaluateSingle(index)

		self.__normalizedDicitionary = copy.deepcopy(self.__aggregateDictionary)
		self.__indexesDictionary = {}

		self.__scNormalizeAggregations()
		self.__scWeightNormalizations()

		self.__status = 2

	def scBestTopology(self):

		if self.__status != 2:
			return None

		key = max(self.__indexesDictionary, key = self.__indexesDictionary.get)

		return self.__sfcOriginal[key]

	def scSFCIndexes(self):

		if self.__status != 2:
			return None

		resultList = []
		for key in self.__sfcDictionary:
			resultList.append((self.__sfcOriginal[key], self.__indexesDictionary[key]))

		return resultList

	def scStatus(self):

		return self.__status

	def scSFCKeys(self):

		if self.__status != 1:
			return None

		return self.__sfcOriginal

	def scAggregation(self):

		if self.__status != 2:
			return None

		return self.__aggregateDictionary

	def scNormalizations(self):

		if self.__status != 2:
			return None

		return self.__normalizedDicitionary

	def scIndexes(self):

		if self.__status != 2:
			return None

		return self.__indexesDictionary

######## SFC COMPOSITION CLASS END ########
