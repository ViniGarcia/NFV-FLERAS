######## BRANCH CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service) 
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A BRANCH SEGMENT (LIST FORMAT) TO BE 
#PROCESSED AND SEPARETED INTO LISTS. THIS CLASS 
#ALSO DETECT AVAILABLE UNIONS ON THE BRANCHES.

#THE CLASS STATUS ATTRIBUTE INDICATE ITS 
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: NO BRANCH ANALYZED
#1: AVAILABLE ANALYZED BRANCH

#################################################

class Branch:
	__status = None

	__originalSegment = None
	__branchSegments = None
	__branchDependencies = None
	__branchMatches = None
	__branchMatchesInfra = None
	__branchMatchList = None
	__branchStringList = None

	######## CONSTRUCTOR ########

	def __init__(self):

		self.__status = 0

	def __init__(self, branchSegment):

		self.bAnalyze(branchSegment)

	######## PRIVATE METHODS ########

	def __bSepareSegments(self):

		allSegments = []
		lastSegment = 0
		skipBrace = 0
		for index in range(len(self.__originalSegment)):
			if self.__originalSegment[index] == '{':
				skipBrace += 1
			if self.__originalSegment[index] == '}':
				skipBrace -= 1
			if self.__originalSegment[index] == '/':
				if skipBrace == 0:
					allSegments.append(self.__originalSegment[lastSegment:index])
					lastSegment = index + 1
		allSegments.append(self.__originalSegment[lastSegment:len(self.__originalSegment)])

		return allSegments

	def __bSepareDependencies(self):

		branchDependencies = []
		for bIndex in range(len(self.__branchSegments)):
			segmentDependencies = {}
			while '<' in self.__branchSegments[bIndex]:
				index = self.__branchSegments[bIndex].index('<')
				segmentDependencies[index-1] = self.__branchSegments[bIndex][index+1]
				self.__branchSegments[bIndex] = self.__branchSegments[bIndex][0:index] + self.__branchSegments[bIndex][index+3:len(self.__branchSegments[bIndex])]
			branchDependencies.append(segmentDependencies)

		return branchDependencies

	def __bMatchBranches(self):

		self.__branchMatches = 0
		self.__branchMatchesInfra = []
		self.__branchSegments = self.__bSepareSegments()
		self.__branchDependencies = self.__bSepareDependencies()
		minimumSize = len(self.__branchSegments[0])	
		for segment in self.__branchSegments:
			if '{' in segment:
				size = len(segment) - (len(segment) - segment.index('{')) - 1 
			else:
				size = len(segment) - 1

			if size == 0:
				return
			if size < minimumSize:
				minimumSize = size

		for index in range(minimumSize):
			analysis = -1
			dependency = False
			for sIndex in range(len(self.__branchSegments)):
				if analysis != -1:
					if analysis != self.__branchSegments[sIndex][index]:
						return
					if index in self.__branchDependencies[sIndex]:
						if dependency:
							if dependency != self.__branchDependencies[sIndex][index]:
								return
						else:
							dependency = self.__branchDependencies[sIndex][index]
				else:	
					analysis = self.__branchSegments[sIndex][index]
					if index in self.__branchDependencies[sIndex]:
						dependency = self.__branchDependencies[sIndex][index]

			self.__branchMatches += 1
			self.__branchMatchesInfra.append(dependency)

	def __bMergeMatches(self):

		self.__branchMatchList = []
		if self.__branchMatches == 0:
			return

		for bIndex in range(1, self.__branchMatches+1):
			allSegments = self.__bSepareSegments()

			branchMatch = []
			for index in range(bIndex):
				branchMatch.append(allSegments[0][index])
				if self.__branchMatchesInfra[index]:
					branchMatch.append('<')
					branchMatch.append(self.__branchMatchesInfra[index])
					branchMatch.append('>')
			branchMatch.append('{')

			for subSegment in allSegments:
				for index in range(bIndex):
					if subSegment[1] == '<':
						subSegment = subSegment[4:]
					else:
						subSegment = subSegment[1:]
				branchMatch += subSegment
				branchMatch.append('/')

			branchMatch.pop()
			branchMatch.append('}')

			self.__branchMatchList.append(branchMatch)
	
	def __bStringMatches(self):

		self.__branchStringList = []

		originalBranch = self.__originalSegment.copy()
		originalBranch.insert(0, '{')
		originalBranch.append('}')
		self.__branchMatchList.append(originalBranch)
		for match in self.__branchMatchList:
			stringMatch = [match[0]]
			for index in range(1, len(match)):
				stringMatch.append(' ')
				stringMatch.append(match[index])
			self.__branchStringList.append(''.join(stringMatch))

	######## PUBLIC METHODS ########

	def bAnalyze(self, originalSegment):

		self.__originalSegment = originalSegment
		self.__bMatchBranches()
		self.__bMergeMatches()
		self.__bStringMatches()
		self.__status = 1

	def bStatus(self):

		return self.__status

	def bMatches(self):

		if self.__status != 1:
			return None

		return self.__branchMatches

	def bMatchList(self):

		if self.__status != 1:
			return None

		return self.__branchMatchList

	def bStringList(self):

		if self.__status != 1:
			return None

		return self.__branchStringList

######## BRANCH CLASS END ########


######## SFC EXPANSION CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service) 
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A VALID SFC TOPOLOGY AND EXPANDS
#ITS SPECIFIC STRUCTURES BY RESOLVING PARTIAL
#ORDERS AND MERGING BRANCHES. IT RETURNS ALL
#POSSIBLE COMBINATIONS.

#THE CLASS STATUS ATTRIBUTE INDICATE ITS 
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: NO TOPOLOGY EXPANDED
#1: AVAILABLE EXPANDED TOPOLOGIES

#ERROR CODES ->
#-1: RECEIVED TOPOLOGY IS NOT VALID 
#-2: NO COMBINATION IS AVAILABLE FOR THE PARTIAL ORDER

#################################################

######## SFC EXPANSION CLASS BEGIN ########

from SFCTopology import SFCTopology, PartialOrder
from SFCRequest import SFCRequest
import itertools

class SFCExpansion:
	__status = None
	
	__sfcTopology = None
	__sfcPOrder = None
	__sfcBranches = None

	######## CONSTRUCTOR ########

	def __init__(self):

		self.__status = 0

	def __init__(self, sfcTopology):
		
		self.seExpand(sfcTopology)

	######## PRIVATE METHODS ########

	def __seStringfy(self, charList):

			stringData = [charList[0]]
			for index in range(1, len(charList)):
				stringData.append(' ')
				stringData.append(charList[index])

			return ''.join(stringData)

	def __seValidatePermutation(self, permutation, oDependency, cDependency):

		for dependency in cDependency:
			if permutation.index(dependency[0]) != permutation.index(dependency[1])-1:
				return False

		for dependency in oDependency:
			if permutation.index(dependency[0]) > permutation.index(dependency[1]):
				return False

		return True

	def __seCombinePermutations(self, pOrderSegments, sfcTopology):
		
		allPermutations = []
		for segment in pOrderSegments:
			allPermutations.append(segment.poCombinations())
		pOrderProduct = list(itertools.product(*allPermutations))

		sfcTopology = sfcTopology.split()
		key = 0

		while '[' in sfcTopology:
			index = sfcTopology.index('[')
			sfcTopology[index] = key
			sfcTopology = sfcTopology[0:index+1] + sfcTopology[sfcTopology.index(']')+1:len(sfcTopology)]
			key += 1
		while '(' in sfcTopology:
			sfcTopology = sfcTopology[0:sfcTopology.index('(')] + sfcTopology[sfcTopology.index(')')+1:len(sfcTopology)]

		allCombinations = []
		for hardOrdering in pOrderProduct:
			sfcAdapted = sfcTopology
			for index in range(key):
				sfcAdapted = sfcAdapted[0:sfcAdapted.index(index)] + list(hardOrdering[index]) + sfcAdapted[sfcAdapted.index(index)+1:len(sfcAdapted)]
			allCombinations.append(sfcAdapted)
		
		return allCombinations

	def __sePartialOrder(self):

		pOrderSegments = self.__sfcTopology.stPOrder()
		for segment in pOrderSegments:
			availablePermutations = list(itertools.permutations(segment.poOPEs()))
			acceptedPermutations = []

			for permutation in availablePermutations:
				if self.__seValidatePermutation(permutation, segment.poOD(), segment.poCD()):
					acceptedPermutations.append(list(permutation))

			if len(acceptedPermutations) == 0:
				self.__status = -2
				return None

			segment.poSetupCombinations(acceptedPermutations)

		return self.__seCombinePermutations(pOrderSegments, self.__sfcTopology.stTopology())

	def __seSeparateBranches(self, splittedSFC):

		sfcBranches = []

		for index in range(0, len(splittedSFC)):

			if splittedSFC[index] == '{':
				processIndex = index + 1
				jumpBraces = 0
				while True:
					if splittedSFC[processIndex] == '}':
						if jumpBraces == 0:
							sfcBranches.append(splittedSFC[index+1:processIndex])
							break
						else:
							jumpBraces -= 1
					if splittedSFC[processIndex] == '{':
						jumpBraces += 1
					processIndex += 1

		return sfcBranches

	def __seRestructBranch(self, base, combination):

	
		for cIndex in range(len(combination)):
			
			if combination[cIndex] == None:
				continue

			actualBranch = 0
			skipBrace = 0
			start = -1

			for index in range(len(base)):
				if base[index] == '{':
					if actualBranch == cIndex:
						start = index
					else:
						if start != -1:
							skipBrace += 1
					actualBranch += 1

				if base[index] == '}':
					if start != -1:
						if skipBrace != 0:
							skipBrace -= 1
						else:
							stop = index
							break

			base = base[:start] + combination[cIndex] + base[stop+1:]

		return base

	def __seBranches(self):

		availableSFCs = []

		for pOrder in self.__sfcPOrder:
			sfcBranches = self.__seSeparateBranches(pOrder)
			allBranches = []
			for index in range(len(sfcBranches)):
				branchInstance = Branch(sfcBranches[index])
				if branchInstance.bStringList() != []:
					allBranches.append(branchInstance.bStringList()) #Adicionar o segmento original também
				else:
					allBranches.append([None])

			base = self.__seStringfy(pOrder)
			combinationList = list(itertools.product(*allBranches))
			for combination in combinationList:
				availableSFCs.append(self.__seRestructBranch(base, combination))

		return availableSFCs

	######## PUBLIC METHODS ######## 

	def seExpand(self, sfcTopology):

		self.__sfcTopology = sfcTopology
		if self.__sfcTopology.stStatus() != 1:
			self.__status = -1

		self.__sfcPOrder = self.__sePartialOrder()
		if self.__status == -2:
			return
		self.__sfcBranches = self.__seBranches()

		self.__status = 1

	def seStatus(self):

		return self.__status

	def sePOrder(self):

		if self.__status != 1:
			return None

		stringPOrders = []
		for pOrder in self.__sfcPOrder:
			stringPOrders.append(self.__seStringfy(pOrder))

		return stringPOrders

	def seBranches(self):

		if self.__status != 1:
			return None

		return self.__sfcBranches

######## SFC EXPANSION CLASS END ########