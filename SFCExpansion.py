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

#################################################

######## SFC EXPANSION CLASS BEGIN ########

from SFCTopology import SFCTopology, PartialOrder
from SFCRequest import SFCRequest
import itertools

class SFCExpansion:
	__status = None
	
	__sfcTopology = None
	__sfcPOrder = None

	######## CONSTRUCTOR ########

	def __init__(self):

		self.__status = 0

	def __init__(self, sfcTopology):
		
		self.seExpand(sfcTopology)

	######## PRIVATE METHODS ########

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
			sfcTopology = sfcTopology[0:index+1] + sfcTopology[sfcTopology.index(']')+1:-1]
			key += 1
		while '(' in sfcTopology:
			sfcTopology = sfcTopology[0:sfcTopology.index('(')] + sfcTopology[sfcTopology.index(')')+1:-1]

		allCombinations = []
		for hardOrdering in pOrderProduct:
			sfcAdapted = sfcTopology
			for index in range(key):
				sfcAdapted = sfcAdapted[0:sfcAdapted.index(index)] + list(hardOrdering[index]) + sfcAdapted[sfcAdapted.index(index)+1:-1]
			allCombinations.append(sfcAdapted)
		
		return allCombinations

	def __sePartialOrder(self):

		pOrderSegments = self.__sfcTopology.stPOrder()
		for segment in pOrderSegments:
			availablePermutations = list(itertools.permutations(segment.poOPEs()))
			acceptedPermutations = []

			for permutation in availablePermutations:
				if self.__seValidatePermutation(permutation, segment.poOD(), segment.poCD()):
					acceptedPermutations.append(permutation)

			if len(acceptedPermutations) == 0:
				self.__status = -2
				return None

			segment.poSetupCombinations(acceptedPermutations)

		return self.__seCombinePermutations(pOrderSegments, self.__sfcTopology.stTopology())

	def __seBranches(self):
		pass

	######## PUBLIC METHODS ######## 

	def seExpand(self, sfcTopology):

		self.__sfcTopology = sfcTopology
		if self.__sfcTopology.stStatus() != 1:
			self.__status = -1

		self.__sfcPOrder = self.__sePartialOrder()
		if self.__status == -2:
			return

		#BRANCH ANALYSIS - CONTINUE HERE!!

		self.__status = 1

	def sePOrder(self):

		if self.__status != 1:
			return None

		return self.__sfcPOrder

######## SFC EXPANSION CLASS END ########

request = SFCRequest('Example/ReqExample.yaml')
topology = SFCTopology(request.srEPs(), request.srOPEs())
topology.stValidate(request.srTopology())
expand = SFCExpansion(topology)
print(expand.sePOrder())