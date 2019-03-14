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
#2: GENERATED DISTRBUTIONS EVALUATION AVAILABLE

#################################################

import sys
sys.path.insert(0, 'YAMLR/')

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
	__currentOutNodes = None
	__currentInteractions = None
	__currentIndexes = None

	__distEvaluations = None

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
		print("PRODUTO INICIAL: ", len(fullCombinations))

		acceptedCombinations = []
		transitionPolicies = list(set(list(self.__sfcImmPolicies["TRANSITION"].keys()) + list(self.__sfcAggPolicies["TRANSITION"].keys())))

		for distribution in fullCombinations:
			accept = True
			domIndex = 0
			domLast = [0]
			domSaves = [[0]]
			lastSaves = []

			for index in self.__currentIndexes:
				for lastDomain in domLast:
					if distribution[lastDomain] != distribution[domIndex]:
						for policy in transitionPolicies:
							if self.__domMatrix[distribution[lastDomain]][distribution[domIndex]][policy] == None:
								accept = False
								break
						if not accept:
							break
				if not accept:
					break

				if self.__currentTopology[index+1] == '{':
					lastSaves.append([])
					domSaves.append(domIndex)
					domLast = [domIndex]
					domIndex += 1
					continue
				if self.__currentTopology[index+1] == '}' or (len(self.__currentTopology) >= index+3 and self.__currentTopology[index+1] in self.__currentOutNodes and self.__currentTopology[index+2] == '}'):
					domSaves.pop(-1)
					domLast = lastSaves.pop(-1)
					domIndex += 1
					continue
				if self.__currentTopology[index+1] == '/' or (len(self.__currentTopology) > index+3 and self.__currentTopology[index+1] in self.__currentOutNodes and self.__currentTopology[index+2] == '/'):
					lastSaves[-1].append(domIndex)
					domLast = [domSaves[-1]]
					domIndex += 1
					continue
				else:
					domLast = [domIndex]
					domIndex += 1

			if accept:
				acceptedCombinations.append(distribution)

		print("TRANSIÇÕES POSSIVEIS: ", len(acceptedCombinations))
		return acceptedCombinations

	def __osmCombineResources(self, domCombinations):

		printTest = {'MEMORY':0, 'NET_IFACES':0, 'CPUS':0}
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
						printTest[resource] += 1
						accept = False
						break
				if not accept:
					break
				domIndex += 1
			if accept:
				acceptedCombinations.append(distribution)

		print("RECURSOS: ", len(acceptedCombinations))
		print("DROPS RECURSOS: ", printTest)
		return acceptedCombinations

	def __osmCombinePolicies(self, resCombinations):

		printDrops = {'IMMEDIATE':0, 'AGGREGATE':0}
		acceptedCombinations = {"DIST":[], "AGG":[]}

		aggregationsBase = {"AGGREGATE":{}, "IMMEDIATE":{}}
		for key in list(self.__sfcAggPolicies['LOCAL'].keys()) + list(self.__sfcAggPolicies['TRANSITION'].keys()):
			aggregationsBase["AGGREGATE"][key] = 0
		for key in list(self.__sfcImmPolicies['LOCAL'].keys()) + list(self.__sfcImmPolicies['TRANSITION'].keys()):
			aggregationsBase["IMMEDIATE"][key] = 0

		for distribution in resCombinations:
			aggregationsAnalysis = copy.deepcopy(aggregationsBase)
			accept = True
			domIndex = 0
			domLast = [0]
			domSaves = [[0]]
			lastSaves = []

			transitionsQuantity = 0
			elementsQuantity = len(distribution)

			for index in self.__currentIndexes:

				for lastDomain in domLast:
					if distribution[lastDomain] != distribution[domIndex]:
						transitionsQuantity += 1
						for policy in self.__sfcImmPolicies['TRANSITION']:
							domValue = self.__domMatrix[distribution[lastDomain]][distribution[domIndex]][policy]
							policyMin = self.__sfcImmPolicies['TRANSITION'][policy]['MIN']
							policyMax = self.__sfcImmPolicies['TRANSITION'][policy]['MAX']

							if domValue >= policyMin and domValue <= policyMax:
								aggregationsAnalysis['IMMEDIATE'][policy] += domValue
							else:
								printDrops['IMMEDIATE'] += 1
								accept = False
								break
						if not accept:
							break

						for policy in self.__sfcAggPolicies['TRANSITION']:
							domValue = self.__domMatrix[distribution[lastDomain]][distribution[domIndex]][policy]
							policyMin = self.__sfcAggPolicies['TRANSITION'][policy]['MIN']
							policyMax = self.__sfcAggPolicies['TRANSITION'][policy]['MAX']

							aggregationsAnalysis['AGGREGATE'][policy] += domValue
							if aggregationsAnalysis['AGGREGATE'][policy] < policyMin or aggregationsAnalysis['AGGREGATE'][policy] > policyMax:
								printDrops['AGGREGATE'] += 1
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
							printDrops['IMMEDIATE'] += 1
							accept = False
							break
					if not accept:
						break
				if not accept:
					break

				for policy in self.__sfcAggPolicies['LOCAL']:
					domValue = self.__domMatrix[distribution[domIndex]][distribution[domIndex]]['LOCAL'][policy]
					policyMin = self.__sfcAggPolicies['LOCAL'][policy]['MIN']
					policyMax = self.__sfcAggPolicies['LOCAL'][policy]['MAX']

					aggregationsAnalysis['AGGREGATE'][policy] += domValue
					if aggregationsAnalysis['AGGREGATE'][policy] < policyMin or aggregationsAnalysis['AGGREGATE'][policy] > policyMax:
						printDrops['AGGREGATE'] += 1
						accept = False
						break
				if not accept:
					break

				if self.__currentTopology[index+1] == '{':
					lastSaves.append([])
					domSaves.append(domIndex)
					domLast = [domIndex]
					domIndex += 1
					continue
				if self.__currentTopology[index+1] == '}' or (len(self.__currentTopology) >= index+3 and self.__currentTopology[index+1] in self.__currentOutNodes and self.__currentTopology[index+2] == '}'):
					domSaves.pop(-1)
					domLast = lastSaves.pop(-1)
					domIndex += 1
					continue
				if self.__currentTopology[index+1] == '/' or (len(self.__currentTopology) > index+3 and self.__currentTopology[index+1] in self.__currentOutNodes and self.__currentTopology[index+2] == '/'):
					lastSaves[-1].append(domIndex)
					domLast = [domSaves[-1]]
					domIndex += 1
					continue
				else:
					domLast = [domIndex]
					domIndex += 1

			if accept:
				for policy in self.__sfcImmPolicies["LOCAL"]:
					aggregationsAnalysis["IMMEDIATE"][policy] = aggregationsAnalysis["IMMEDIATE"][policy] / elementsQuantity
				for policy in self.__sfcImmPolicies["TRANSITION"]:
					aggregationsAnalysis["IMMEDIATE"][policy] = aggregationsAnalysis["IMMEDIATE"][policy] / transitionsQuantity

				acceptedCombinations["DIST"].append(distribution)
				acceptedCombinations["AGG"].append(aggregationsAnalysis)

		print('POLITICAS: ', len(acceptedCombinations["DIST"]))
		print('DROPS POLITICAS: ', printDrops)

		return acceptedCombinations

	######## PUBLIC METHODS ########

	def osmSetup(self, sfcImmPolicies, sfcAggPolicies, sfcFlavours, domMatrix):

		self.__sfcImmPolicies = sfcImmPolicies
		self.__sfcAggPolicies = sfcAggPolicies
		self.__sfcFlavours = sfcFlavours
		self.__domMatrix = domMatrix
		self.__status = 1

	def osmProcess(self, elements, outNodes, topology, dependencies):

		self.__currentTopology = topology
		self.__currentOutNodes = outNodes
		self.__osmInteractions(elements, dependencies, list(self.__domMatrix.keys()))
		self.__distEvaluations = self.__osmCombinePolicies(self.__osmCombineResources(self.__osmCombineDomains()))
		self.__status = 2
		print("")

	def osmStatus(self):

		return self.__status

	def osmEvaluation(self):

		if self.__status != 2:
			return None

		return self.__distEvaluations

######## OPTIMAL SM CLASS END ########
