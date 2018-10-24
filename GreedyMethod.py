######## GREEDY METHOD CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service) 
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A VALID TOPOLOGY, ITS REQUEST
#AND DOMAINS MATRIX, ALL PREVIOUSLY VALIDATED
#BY THE SFC SLIPT MAP CLASS, AND EXECUTES
#A GREEDY METHOD TO DISTRIBUTE THE OPERATIONAL
#ON MULTIPLE DOMAINS.

#THE CLASS STATUS ATTRIBUTE INDICATE ITS 
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: DOMAINS MATRIX AND REQUEST MUST BE INFORMED
#1: 

#################################################

from SFCRequest import SFCRequest

class GreedyMethod:
	__status = None

	__sfcImmPolicies = None
	__sfcAggPolicies = None
	__sfcFlavours = None
	__domMatrix = None

	__currentTopology = None
	__currentDepencencies = None

	######## CONSTRUCTOR ########

	def __init__(self, sfcImmPolicies, sfcAggPolicies, sfcFlavours, domMatrix):

		if sfcImmPolicies != None and sfcAggPolicies != None and sfcFlavours != None and domMatrix != None:
			self.gmSetup(sfcImmPolicies, sfcAggPolicies, sfcFlavours, domMatrix)
		else:
			self.__status = 0

	######## PRIVATE METHODS ########

	def __gmEvaluate(self, current, excepts, position):
		#TO DO
		pass

	######## PUBLIC METHODS ########

	def gmSetup(self, sfcImmPolicies, sfcAggPolicies, sfcFlavours, domMatrix):

		self.__sfcImmPolicies = sfcImmPolicies
		self.__sfcAggPolicies = sfcAggPolicies
		self.__sfcFlavours = sfcFlavours
		self.__domMatrix = domMatrix
		self.__status = 1

	def gmProcess(self, topology, dependencies):
		#TO DO
		print(topology)
		print(dependencies)

######## GREEDY METHOD CLASS END ########