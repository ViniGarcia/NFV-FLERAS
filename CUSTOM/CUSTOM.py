######## PARTIAL ORDER CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service)
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A PARTIAL ORDER SEGMENT AND ITS
#ORDER AND COUPLING DEPENDENCIES TO PROCESS
#AND VALIDATE THEM. THIS CLASS WAS DEVELOPED
#TO BE A SFC TOPOLOGY AND EXPANSION META-CLASS.

#THE CLASS STATUS ATTRIBUTE INDICATE ITS
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: NO PARTIAL ORDER SEGMENT VALIDATED
#1: VALID PARTIAL ORDER SEGMENT

#ERROR CODES ->
#-1 -> DEPENDENCY ELEMENT NOT PRESENT IN THE PARTIAL ORDER SEGMENT
#-2 -> ELEMENTS ALREADY COUPLED AND THIS COUPLING IS NOT POSSIBLE (SAME COUP. GROUP)
#-3 -> ELEMENTS ALREADY COUPLED AND THIS COUPLING IS NOT POSSIBLE (OTHER COUP. GROUP)
#-4 -> FIRST ELEMENT IN A COUPLING AND THE SECOND COUPLE IS NOT POSSIBLE
#-5 -> SECOND ELEMENT IN A COUPLING AND THE FIRST COUPLE IS NOT POSSIBLE
#-6 -> ELEMENTS ARE COUPLED IN THE SAME GROUP AND THE ORDER DEPENDENCY DO NOT MATCH
#-7 -> DUPLICATED ELEMENT IN THE DEPENDENCY
#-8 -> CROSS DEPENDENCY ERROR (PREVIOUS DEPENDENCY INDICATES THAT THE SENCOND GROUP/ELEMENT MUST BE BEFORE THE FIRST)
#-9 -> CROSS DEPENDENCY ERROR (PREVIOUS DEPENDENCY INDICATES THAT THE FIRST GROUP/ELEMENT MUST BE AFTER THE SECOND)

#################################################

######## PARTIAL ORDER CLASS BEGIN ########

class PartialOrder:
	__status = None

	__elements = None
	__oDependencies = None
	__cDependencies = None
	__dDependencies = None
	__iDependencies = None

	__combinations = None

	######## CONSTRUCTOR ########

	def __init__(self, porderPEs, porderODs, porderCDs):

		self.poValidate(porderPEs, porderODs, porderCDs)

	######## PRIVATE METHODS ########

	def __poInfraDependenciesRemove(self):

		while '<' in self.__elements:
			index = self.__elements.index('<')
			if self.__elements[index+2] == '>':
				self.__dDependencies.append((self.__elements[index-1], self.__elements[index+1]))
				self.__elements = self.__elements[0:index] + self.__elements[index+3:len(self.__elements)]
			else:
				self.__iDependencies.append((self.__elements[index-1], self.__elements[index+1], self.__elements[index+3]))
				self.__elements = self.__elements[0:index] + self.__elements[index+5:len(self.__elements)]

	def __poDependenciesElementsValidate(self):

		for cDependency in self.__cDependencies + self.__oDependencies:
			if not cDependency[0] in self.__elements or not cDependency[1] in self.__elements:
				self.__status = -1
				return False
		return True

	def __poCouplingDepenciesProcess(self):

		hashID = 1
		elementsHash = {}
		elementsCouplings = {}

		for element in self.__elements:
			elementsHash[element] = element

		for cDependency in self.__cDependencies:
			beforeKey = elementsHash[cDependency[0]]
			afterKey = elementsHash[cDependency[1]]

			if beforeKey.startswith('%') and afterKey.startswith('%'):
				beforeCoupling = elementsCouplings[beforeKey]
				afterCoupling = elementsCouplings[afterKey]

				if beforeKey == afterKey:
					if beforeCoupling.index(cDependency[0]) == afterCoupling.index(cDependency[1]) - 1:
						continue
					else:
						self.__status = -2
						return False

				if beforeCoupling[-1] == cDependency[0] and afterCoupling[0] == cDependency[1]:
					for element in afterCoupling:
						elementsHash[element] = beforeKey
					elementsCouplings[beforeKey] += elementsCouplings[afterKey]
					elementsCouplings.pop(afterKey)
					continue
				else:
					self.__status = -3
					return False

			if beforeKey.startswith('%') and not afterKey.startswith('%'):
				if elementsCouplings[beforeKey][-1] != cDependency[0]:
					self.__status = -4
					return False
				elementsCouplings[beforeKey].append(afterKey)
				elementsHash[afterKey] = beforeKey
				continue

			if not beforeKey.startswith('%') and afterKey.startswith('%'):
				if elementsCouplings[afterKey][0] != cDependency[1]:
					self.__status = -5
					return False
				elementsCouplings[afterKey].insert(0, beforeKey)
				elementsHash[beforeKey] = afterKey
			else:
				newGroup = '%' + str(hashID)
				elementsCouplings[newGroup] = [beforeKey, afterKey]
				elementsHash[beforeKey] = newGroup
				elementsHash[afterKey] = newGroup
				hashID += 1

		return (elementsHash, elementsCouplings)

	def __poOrderDepenciesProcess(self, couplingGroups):

		beforeElements = {}
		afterElements = {}

		elementsHash = couplingGroups[0]
		elementsCouplings = couplingGroups[1]

		for key in elementsHash:
			if not elementsHash[key] in beforeElements:
				beforeElements[elementsHash[key]] = []
				afterElements[elementsHash[key]] = []

		for oDependency in self.__oDependencies:
			beforeGroup = elementsHash[oDependency[0]]
			afterGroup = elementsHash[oDependency[1]]

			if beforeGroup == afterGroup:
				if beforeGroup.startswith('%'):
					if elementsCouplings[beforeGroup].index(oDependency[0]) < elementsCouplings[beforeGroup].index(oDependency[1]):
						return True
					else:
						self.__status = -6
						return False
				else:
					self.__status = -7
					return False
			if beforeGroup in beforeElements[afterGroup]:
				self.__status = -8
				return False
			if afterGroup in afterElements[beforeGroup]:
				self.__status = -9
				return False

			beforeElements[beforeGroup].append(afterGroup)
			beforeElements[beforeGroup] += beforeElements[afterGroup]
			afterElements[afterGroup].append(beforeGroup)
			afterElements[afterGroup] += afterElements[beforeGroup]

		return True

	######## PUBLIC METHODS ########

	def poValidate(self, porderPEs, porderODs, porderCDs):

		self.__elements = porderPEs
		self.__oDependencies = porderODs
		self.__cDependencies = porderCDs
		self.__dDependencies = []
		self.__iDependencies = []

		self.__poInfraDependenciesRemove()
		if self.__poDependenciesElementsValidate():
			couplingGroups = self.__poCouplingDepenciesProcess()
			if isinstance(couplingGroups, tuple):
				if self.__poOrderDepenciesProcess(couplingGroups):
					self.__status = 1


	def poSetupCombinations(self, combinations):

		if self.__status != 1:
			return None

		for dependency in self.__dDependencies:
			for combination in combinations:
				index = combination.index(dependency[0])
				combination.insert(index + 1, '< ' + dependency[1] + ' >')

		for dependency in self.__iDependencies:
			for combination in combinations:
				 index = combination.index(dependency[0])
				 combination.insert(index + 1, '< ' + dependency[1] + ' | ' + dependency[2] + ' >')

		self.__combinations = combinations

	def poValid(self):

		if self.__status == 1:
			return True
		else:
			return False

	def poStatus(self):

		return self.__status

	def poElements(self):

		if self.__status != 1:
			return None

		return self.__elements

	def poODependencies(self):

		if self.__status != 1:
			return None

		return self.__oDependencies

	def poCDependencies(self):

		if self.__status != 1:
			return None

		return self.__cDependencies

	def poDDependencies(self):

		if self.__status != 1:
			return None

		return self.__dDependencies

	def poIDependencies(self):

		if self.__status != 1:
			return None

		return self.__iDependencies

	def poCombinations(self):

		if self.__status != 1:
			return None

		if self.__combinations == None:
			return False
		else:
			return self.__combinations


######## PARTIAL ORDER CLASS END ########

#--------------------------------------------------

########### CUSTOM CLASS DESCRIPTION ############

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service)
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A SFC TOPOLOGY STRUCTURED USING THE
#GRAMMAR SYTAX, IN ADDITION TO ITS OPERATIONAL
#ELEMENTS LIST AND END POINTS LISTS. THESE DATA
#CAN BE RECOVERED FROM THE SFC REQUEST CLASS.

#THE CLASS STATUS ATTRIBUTE INDICATE ITS
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: NO TOPOLOGY VALIDATED
#1: VALID TOPOLOGY

#ERROR CODES ->
#-1 -> PHYSICAL DEPENDECY WITHOUT DOMAINS DEFINITION
#-2 -> SYNTAX ERROR IN THE SFC TOPOLOGY
#-3 (+ PARTIAL ORDER ERROR CODE) -> PARTIAL ORDER ERROR
#	THIS CODE ERROR IS ALWAYS LESS THAN -3
#		SUM 3 TO GET THE PARTIAL ORDER ERROR CODE
#		SUBTRACT THE PARTIAL ORDER CODE TO GET THE SFC TOPOLOGY ERROR (-3)

#################################################

############## CUSTOM CLASS BEGIN ###############

import nltk

class CUSTOM:
	__status = None

	__topologyENs = None
	__topologyVNFs = None
	__topologyPNFs = None
	__topologyDomains = None
	__topologyMachines = None

	__serviceTopology = None
	__servicePorders = None

	######## CONSTRUCTOR ########

	def __init__(self, topologyVNFs, topologyPNFs, topologyDomains, topologyMachines, topologyENs):

		kernelGrammar = """
			START -> "IN" MAIN

			MAIN -> TBRANCHING | NTBRANCHING | OPERATIONAL MAIN | OPERATIONAL EN
			NTBMAIN -> INTBRANCHING | OPERATIONAL NTBMAIN | OPERATIONAL

			OPERATIONAL -> PORDER | FUNCTION

			PORDER -> "[" FUNCTION NFUNCTION "]" EDEPENDENCY | "[" FUNCTION NFUNCTION "]"

			EDEPENDENCY -> EORDERING | ECOUPLING
			EORDERING -> "(" FUNCTION FUNCTION ")" EDEPENDENCY | "(" FUNCTION FUNCTION ")"
			ECOUPLING -> "(" FUNCTION FUNCTION "*" ")" EDEPENDENCY | "(" FUNCTION FUNCTION "*" ")"

			TBRANCHING -> OPERATIONAL "{" MAIN TBRANCH "}"
			TBRANCH -> "/" MAIN TBRANCH | "/" MAIN

			NTBRANCHING -> OPERATIONAL "{" NTBMAIN NTBRANCH "}" MAIN
			NTBRANCH -> "/" NTBMAIN NTBRANCH | "/" NTBMAIN
			INTBRANCHING -> OPERATIONAL "{" NTBMAIN NTBRANCH "}" NTBMAIN

			FUNCTION -> SHARABLEVNF | SHARABLEVNF ADDEPENDENCY | SHARABLEVNF PMDEPENDENCY | SHARABLEPNF ADDEPENDECY
			NFUNCTION -> FUNCTION NFUNCTION | FUNCTION

			ADDEPENDENCY -> "<" ADMDOMAIN ">"
			PMDEPENDENCY -> "<" PHYMACHINE "|" ADMDOMAIN ">"

			SHARABLEVNF -> "!" VNF | VNF
			SHARABLEPNF -> "!" PNF | PNF
		"""

		grammarVNF = 'VNF -> '
		for VNF in topologyVNFs:
			grammarVNF += ' "' + VNF + '" |'
		grammarVNF = grammarVNF[:len(grammarVNF)-1] + '\n'

		grammarPNF = 'PNF -> '
		for PNF in topologyPNFs:
			grammarPNF += ' "' + PNF + '" |'
		grammarPNF = grammarPNF[:len(grammarPNF)-1] + '\n'

		grammarADomain = 'ADMDOMAIN -> '
		if len(topologyDomains) != 0:
			for domain in topologyDomains:
				grammarADomain += ' "' + domain + '" |'
		grammarADomain = grammarADomain[:len(grammarADomain)-1] + '\n'

		grammarPMachine = 'PHYMACHINE -> '
		if len(topologyDomains) != 0 and len(topologyMachines) != 0:
			for machine in topologyMachines:
				grammarPMachine += ' "' + machine + '" |'
		else:
			if len(topologyMachines) != 0:
				self.__status = -1
				return
		grammarPMachine = grammarPMachine[:len(grammarPMachine)-1] + '\n'

		grammarEN = 'EN -> '
		for EN in topologyENs:
			grammarEN += ' "' + EN + '" |'
		grammarEN = grammarEN[:len(grammarEN)-1]

		self.__topologyVNFs = topologyVNFs
		self.__topologyPNFs = topologyPNFs
		self.__topologyDomains = topologyDomains
		self.__topologyMachines = topologyMachines
		self.__topologyENs = topologyENs

		self.__mainParser = nltk.ChartParser(nltk.CFG.fromstring(kernelGrammar + grammarVNF + grammarPNF + grammarADomain + grammarPMachine + grammarEN))
		self.__status = 0

	######## PRIVATE METHODS ########

	def __cPorders(self):

		self.__servicePorders = []
		splittedSFC = self.__serviceTopology.split()

		for index in range(0, len(splittedSFC)):

			if splittedSFC[index] == '[':
				porderPEs = []
				porderODs = []
				porderCDs = []

				index += 1
				while splittedSFC[index] != ']':
					porderPEs.append(splittedSFC[index])
					index += 1

				index += 1
				while splittedSFC[index] == '(':
					if splittedSFC[index+3] != '*':
						porderODs.append([splittedSFC[index+1], splittedSFC[index+2]])
						index += 4
					else:
						porderCDs.append([splittedSFC[index+1], splittedSFC[index+2]])
						index += 5

				self.__servicePorders.append(PartialOrder(porderPEs, porderODs, porderCDs))

	######## PUBLIC METHODS ########

	def cValidate(self, serviceTopology):

		self.__serviceTopology = None
		self.__servicePorders = None

		if next(self.__mainParser.parse(serviceTopology.split()), None) == None:
			self.__status = -2
			return False

		self.__serviceTopology = serviceTopology
		self.__cPorders()

		for porder in self.__servicePorders:
			if not porder.poValid():
				self.__status = -3 + porder.poStatus()
				return False

		self.__status = 1
		return True

	def cStatus(self):

		return self.__status

	def cTopology(self):

		if self.__status != 1:
			return None

		return self.__serviceTopology

	def cVNFs(self):

		if self.__status != 1:
			return None

		return self.__topologyVNFs

	def cPNFs(self):

		if self.__status != 1:
			return None

		return self.__topologyPNFs

	def cDomains(self):

		if self.__status != 1:
			return None

		return self.__topologyDomains

	def cMachines(self):

		if self.__status != 1:
			return None

		return self.__topologyMachines

	def cEPs(self):

		if self.__status != 1:
			return None

		return self.__topologyENs

	def cPOrder(self):

		if self.__status != 1:
			return None

		return self.__servicePorders

############### CUSTOM CLASS END ################

#import sys
#sys.path.insert(0,'..')

#from YAMLR.YAMLRDomains import YAMLRDomains
#from YAMLR.YAMLRComposition import YAMLRComposition

#dom = YAMLRDomains("1.Example/Domains[FENDE].yaml")
#req = YAMLRComposition("1.Example/Service[CUSCO].yaml", dom.ydDomains())
#print(req.ycStatus())

#test = CUSTOM(req.ycServiceOE(), [], dom.ydDomains(), [], req.ycServiceON())


#################################################
