######## OPTIMAL SM CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service) 
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A VALID TOPOLOGY, ITS REQUEST
#AND DOMAINS MATRIX, ALL PREVIOUSLY VALIDATED
#BY THE SFC SLIPT MAP CLASS, AND EXECUTES
#A OPTIMAL SPLIT AND MAP METHOD TO DISTRIBUTE
#THE OPERATIONAL ELEMENTS ON MULTIPLE DOMAINS.

#THE CLASS STATUS ATTRIBUTE INDICATE ITS 
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: DOMAINS MATRIX AND REQUEST MUST BE INFORMED
#1: READY TO SPLIT AND MAP TOPOLOGIES

#################################################

import copy
from itertools import product

from SFCRequest import SFCRequest

class OptimalSM:
	__status = None

	__sfcImmPolicies = None
	__sfcAggPolicies = None
	__sfcFlavours = None
	__domMatrix = None

	__currentTopology = None
	__currentInteractions = None
	__currentIndexes = None

	__absoluteValues = None
	__distributionsEval = None

	######## CONSTRUCTOR ########

	def __init__(self, sfcImmPolicies, sfcAggPolicies, sfcFlavours, domMatrix):

		if sfcImmPolicies != None and sfcAggPolicies != None and sfcFlavours != None and domMatrix != None:
			self.osmSetup(sfcImmPolicies, sfcAggPolicies, sfcFlavours, domMatrix)
		else:
			self.__status = 0

	######## PRIVATE METHODS ########

	def __osmInteractions(self, elements, dependencies, domains):

		self.__currentInteractions = dependencies
		self.__currentIndexes = []

		for index in range(len(self.__currentTopology)):
			if self.__currentTopology[index] in elements:
				if not index in dependencies:
					self.__currentInteractions[index] = domains.copy()
				self.__currentIndexes.append(index)

	def __osmCombineDomains(self):
		
		ordered = []
		for index in self.__currentIndexes:
			ordered.append(self.__currentInteractions[index])
		
		fullCombinations = list(product(*ordered))
		acceptedCombinations = []

		transitionPolicies = list(set(list(self.__sfcImmPolicies["TRANSITION"].keys()) + list(self.__sfcAggPolicies["TRANSITION"].keys())))

		for distribution in fullCombinations:
			accept = True
			for index in range(len(distribution)-1):
				if distribution[index] != distribution[index+1]:
					for policy in transitionPolicies:
						if self.__domMatrix[distribution[index]][distribution[index+1]][policy] == None:
							accept = False
							break
					if not accept:
						break
			if accept:
				acceptedCombinations.append(distribution)

		return acceptedCombinations

	def __osmCombineResources(self, domCombinations):

		acceptedCombinations = []

		resourceBase = {}
		for domain in self.__domMatrix:
			resourceBase[domain] = self.__domMatrix[domain][domain]["RESOURCES"]

		for distribution in domCombinations:
			resourceAnalysis = copy.deepcopy(resourceBase)
			domIndex = 0
			accept = True
			for index in self.__currentIndexes:
				for resource in resourceAnalysis[distribution[domIndex]]:
					if resourceAnalysis[distribution[domIndex]][resource] >= self.__sfcFlavours[self.__currentTopology[index]][resource]:
						resourceAnalysis[distribution[domIndex]][resource] -= self.__sfcFlavours[self.__currentTopology[index]][resource]
					else:
						accept = False
				if not accept:
					break
				domIndex += 1
			if accept:
				acceptedCombinations.append(distribution)

		return acceptedCombinations

	def __osmCombinePolicies(self, resCombinations):

		acceptedCombinations = {"DIST":[], "AGG":[]}

		aggregationsBase = {"AGGREGATE":{}, "IMMEDIATE":{}}
		for key in list(self.__sfcAggPolicies['LOCAL'].keys()) + list(self.__sfcAggPolicies['TRANSITION'].keys()):
			aggregationsBase["AGGREGATE"][key] = 0
		for key in list(self.__sfcImmPolicies['LOCAL'].keys()) + list(self.__sfcImmPolicies['TRANSITION'].keys()):
			aggregationsBase["IMMEDIATE"][key] = 0
		
		for distribution in resCombinations:
			aggregationsAnalysis = copy.deepcopy(aggregationsBase)
			domIndex = 0
			domLast = 0
			accept = True
			for index in self.__currentIndexes:
				if distribution[domLast] != distribution[domIndex]:
					for policy in self.__sfcImmPolicies['TRANSITION']:
						domValue = self.__domMatrix[distribution[domLast]][distribution[domIndex]][policy]
						policyMin = self.__sfcImmPolicies['TRANSITION'][policy]['MIN']
						policyMax = self.__sfcImmPolicies['TRANSITION'][policy]['MAX']

						if domValue >= policyMin and domValue <= policyMax:
							aggregationsAnalysis['IMMEDIATE'][policy] += domValue
						else:
							accept = False
							break					
					if not accept:
						break

					for policy in self.__sfcAggPolicies['TRANSITION']:
						domValue = self.__domMatrix[distribution[domLast]][distribution[domIndex]][policy]
						policyMin = self.__sfcAggPolicies['TRANSITION'][policy]['MIN']
						policyMax = self.__sfcAggPolicies['TRANSITION'][policy]['MAX']

						aggregationsAnalysis['AGGREGATE'][policy] += domValue
						if aggregationsAnalysis['AGGREGATE'][policy] < policyMin or aggregationsAnalysis['AGGREGATE'][policy] > policyMax:
							accept = False
							break
					if not accept:
						break

				for policy in self.__sfcImmPolicies['LOCAL']:
					domValue = self.__domMatrix[distribution[domIndex]][distribution[domIndex]]['LOCAL'][policy]
					policyMin = self.__sfcImmPolicies['LOCAL'][policy]['MIN']
					policyMax = self.__sfcImmPolicies['LOCAL'][policy]['MAX']

					if domValue >= policyMin and domValue <= policyMax:
						aggregationsAnalysis['IMMEDIATE'][policy] += domValue
					else:
						accept = False
						break
				if not accept:
					break

				for policy in self.__sfcAggPolicies['LOCAL']:
					domValue = self.__domMatrix[distribution[domIndex]][distribution[domIndex]]['LOCAL'][policy]
					policyMin = self.__sfcAggPolicies['LOCAL'][policy]['MIN']
					policyMax = self.__sfcAggPolicies['LOCAL'][policy]['MAX']

					aggregationsAnalysis['AGGREGATE'][policy] += domValue
					if aggregationsAnalysis['AGGREGATE'][policy] < policyMin or aggregationsAnalysis['AGGREGATE'][policy] > policyMax:
						accept = False
						break
				if not accept:
					break	

				domLast = domIndex
				domIndex += 1

			if accept:
				acceptedCombinations["DIST"].append(distribution)
				acceptedCombinations["AGG"].append(aggregationsAnalysis)

		return acceptedCombinations

	def __osmSeparePolicies(self, polCombinations):

		policies = {'AGGREGATE':{}, 'IMMEDIATE':{}}

		if len(polCombinations['AGG']) > 0:
			for policy in polCombinations['AGG'][0]['AGGREGATE'].keys():
				policies['AGGREGATE'][policy] = []
			for policy in polCombinations['AGG'][0]['IMMEDIATE'].keys():
				policies['IMMEDIATE'][policy] = []

			for combination in polCombinations['AGG']:
				for policy in combination['AGGREGATE']:
					policies['AGGREGATE'][policy].append(combination['AGGREGATE'][policy])
				for policy in combination['IMMEDIATE']:
					policies['IMMEDIATE'][policy].append(combination['IMMEDIATE'][policy])
		
		return policies

	def __osmNormalizeCombinations(self, absoluteValues):

		normCombinations = self.__osmSeparePolicies(absoluteValues)

		for type in normCombinations:
			for policy in normCombinations[type]:
				maxValue = max(normCombinations[type][policy])
				minValue = min(normCombinations[type][policy])
				gapValue = maxValue - minValue

				if gapValue != 0:
					for index in range(len(normCombinations[type][policy])):
						normCombinations[type][policy][index] = (normCombinations[type][policy][index] - minValue) / gapValue
				else:
					for index in range(len(normCombinations[type][policy])):
						normCombinations[type][policy][index] = 0

		return normCombinations

	def __osmEvaluateCombinations(self, absoluteValues, normCombinations):

		evalCombinations = [0 for i in range(len(absoluteValues['DIST']))]

		for category in self.__sfcImmPolicies:
			for policy in self.__sfcImmPolicies[category]:
				if self.__sfcImmPolicies[category][policy]['GOAL'] == 'MIN':
					for index in range(len(normCombinations["IMMEDIATE"][policy])):
						normCombinations["IMMEDIATE"][policy][index] = (1 - normCombinations["IMMEDIATE"][policy][index]) * self.__sfcImmPolicies[category][policy]['WEIGHT']
						evalCombinations[index] += normCombinations["IMMEDIATE"][policy][index]
				else:
					for index in range(len(normCombinations["IMMEDIATE"][policy])):
						normCombinations["IMMEDIATE"][policy][index] = (1 - normCombinations["IMMEDIATE"][policy][index]) * self.__sfcImmPolicies[category][policy]['WEIGHT']
						evalCombinations[index] += normCombinations["IMMEDIATE"][policy][index]

		for category in self.__sfcAggPolicies:
			for policy in self.__sfcAggPolicies[category]:
				if self.__sfcAggPolicies[category][policy]['GOAL'] == 'MIN':
					for index in range(len(normCombinations["AGGREGATE"][policy])):
						normCombinations["AGGREGATE"][policy][index] = (1 - normCombinations["AGGREGATE"][policy][index]) * self.__sfcAggPolicies[category][policy]['WEIGHT']
						evalCombinations[index] += normCombinations["AGGREGATE"][policy][index]
				else:
					for index in range(len(normCombinations["AGGREGATE"][policy])):
						normCombinations["AGGREGATE"][policy][index] = (1 - normCombinations["AGGREGATE"][policy][index]) * self.__sfcAggPolicies[category][policy]['WEIGHT']
						evalCombinations[index] += normCombinations["AGGREGATE"][policy][index]

		normCombinations['GENERAL'] = evalCombinations
		return normCombinations

	######## PUBLIC METHODS ########

	def osmSetup(self, sfcImmPolicies, sfcAggPolicies, sfcFlavours, domMatrix):

		self.__sfcImmPolicies = sfcImmPolicies
		self.__sfcAggPolicies = sfcAggPolicies
		self.__sfcFlavours = sfcFlavours
		self.__domMatrix = domMatrix
		self.__status = 1

	def osmProcess(self, elements, topology, dependencies):

		self.__currentTopology = topology
		self.__osmInteractions(elements, dependencies, list(self.__domMatrix.keys()))
		self.__absoluteValues = self.__osmCombinePolicies(self.__osmCombineResources(self.__osmCombineDomains()))
		self.__distributionsEval = self.__osmEvaluateCombinations(self.__absoluteValues, self.__osmNormalizeCombinations(self.__absoluteValues))
		self.__status = 2

	def osmEvaluateGroup(self, analysisData):

		 return self.__osmEvaluateCombinations(analysisData, self.__osmNormalizeCombinations(analysisData))['GENERAL']
	
	def osmBestDistribution(self):

		if self.__status != 2:
			return None

		key = self.__distributionsEval['GENERAL'].index(max(self.__distributionsEval['GENERAL']))

		return self.__absoluteValues['DIST'][key]

	def osmBestDistributionData(self):

		if self.__status != 2:
			return None

		key = self.__distributionsEval['GENERAL'].index(max(self.__distributionsEval['GENERAL']))

		return (self.__absoluteValues['DIST'][key], self.__absoluteValues['AGG'][key])

	def osmDistributionsIndex(self):

		if self.__status != 2:
			return None

		resultList = []
		for index in range(len(self.__absoluteValues['DIST'])):
			resultList.append((self.__absoluteValues['DIST'][index], self.__distributionsEval['GENERAL'][index]))

		return resultList

######## OPTIMAL SM CLASS END ########