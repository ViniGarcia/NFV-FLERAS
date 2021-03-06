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
	__iDependencies = None

	__combinations = None

	######## CONSTRUCTOR ########

	def __init__(self, porderPEs, porderODs, porderCDs):
		
		self.poValidate(porderPEs, porderODs, porderCDs)

	######## PRIVATE METHODS ########

	def __poInfraDependenciesRemove(self):
		
		while '<' in self.__elements:
			index = self.__elements.index('<')
			self.__iDependencies.append((self.__elements[index-1], self.__elements[index+1]))
			self.__elements = self.__elements[0:index] + self.__elements[index+3:len(self.__elements)]
	
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

		for dependency in self.__iDependencies:
			for combination in combinations:
				index = combination.index(dependency[0])
				combination.insert(index + 1, '< ' + dependency[1] + ' >')

		self.__combinations = combinations

	def poValid(self):

		if self.__status == 1:
			return True
		else:
			return False

	def poStatus(self):
		
		return self.__status

	def poOPEs(self):
		
		if self.__status != 1:
			return None

		return self.__elements

	def poOD(self):
		
		if self.__status != 1:
			return None

		return self.__oDependencies

	def poCD(self):
		
		if self.__status != 1:
			return None

		return self.__cDependencies

	def poID(self):

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

######## SCAG CLASS DESCRIPTION ########

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
#-1 -> SYNTAX ERROR IN THE SFC TOPOLOGY
#-2 (+ PARTIAL ORDER ERROR CODE) -> PARTIAL ORDER ERROR
#	THIS CODE ERROR IS ALWAYS LESS THAN -2
#		SUM 2 TO GET THE PARTIAL ORDER ERROR CODE
#		SUBTRACT THE PARTIAL ORDER CODE TO GET THE SFC TOPOLOGY ERROR (-2)

#################################################

######## SCAG CLASS BEGIN ########

import nltk

class SCAG:
	__status = None

	__sfcParser = None
	__boundaryEPs = None
	__operationalPEs = None
	
	__sfcTopology = None
	__sfcPorders = None

	######## CONSTRUCTOR ########

	def __init__(self, boundaryEPs, operationalPEs, availableDomains):

		kernelGrammar = """
			S 			 -> "IN" OPBLOCK

			OPBLOCK 	 -> TBRANCH | NTBRANCH | TPBLOCK OPBLOCK | TPBLOCK EN
			ROPBLOCK	 -> INTBRANCH | TPBLOCK ROPBLOCK | TPBLOCK
			TPBLOCK  	 -> PORDER | MASKPELEM
			
			PORDER 		 -> "[" MASKPELEM NPELEM "]" POEXCEPTION | "[" MASKPELEM NPELEM "]"
			POEXCEPTION  -> "(" PELEM PELEM ")" POEXCEPTION | "(" PELEM PELEM ")" | "(" PELEM PELEM "*" ")" POEXCEPTION | "(" PELEM PELEM "*" ")"
			
			TBRANCH 	 -> TPBLOCK "{" OPBLOCK NEXTTBRANCH "}" 
			NEXTTBRANCH  -> "/" OPBLOCK NEXTTBRANCH | "/" OPBLOCK

			NTBRANCH	 -> TPBLOCK "{" ROPBLOCK NEXTNTBRANCH "}" OPBLOCK
			INTBRANCH	 -> TPBLOCK "{" ROPBLOCK NEXTNTBRANCH "}" ROPBLOCK
			NEXTNTBRANCH -> "/" ROPBLOCK NEXTNTBRANCH | "/" ROPBLOCK

			NPELEM 		 -> MASKPELEM NPELEM | MASKPELEM
			MASKPELEM	 -> PELEM | PELEM "<" DOMAIN ">"
		"""

		grammarPELEM = 'PELEM ->'
		for PE in operationalPEs:
			grammarPELEM += ' "' + PE + '" |'
		grammarPELEM = grammarPELEM[:len(grammarPELEM)-1] + '\n'

		grammarEP = 'EN ->'
		for EN in boundaryEPs:
			grammarEP += ' "' + EN + '" |'
		grammarEP = grammarEP[:len(grammarEP)-1] + '\n'

		grammarDomain = 'DOMAIN ->'
		if len(availableDomains) != 0:
			for domain in availableDomains:
				grammarDomain += ' "' + domain + '" |'
			grammarDomain = grammarDomain[:len(grammarDomain)-1]

		self.__boundaryEPs = boundaryEPs
		self.__operationalPEs = operationalPEs
		self.__mainParser = nltk.ChartParser(nltk.CFG.fromstring(kernelGrammar + grammarPELEM + grammarEP + grammarDomain))
		self.__status = 0

	######## PRIVATE METHODS ########

	def __sPorders(self):

		self.__sfcPorders = []
		splittedSFC = self.__sfcTopology.split()

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

				self.__sfcPorders.append(PartialOrder(porderPEs, porderODs, porderCDs))

	######## PUBLIC METHODS ######## 

	def sValidate(self, sfcTopology):
		
		self.__sfcTopology = None
		self.__sfcPorders = None

		if next(self.__mainParser.parse(sfcTopology.split()), None) == None:
			self.__status = -1
			return False

		self.__sfcTopology = sfcTopology
		self.__sPorders()

		for porder in self.__sfcPorders:
			if not porder.poValid():
				self.__status = -2 + porder.poStatus()
				return False

		self.__status = 1
		return True

	def sStatus(self):

		return self.__status

	def sTopology(self):
		
		if self.__status != 1:
			return None

		return self.__sfcTopology

	def sBoundaryEPs(self):

		if self.__status != 1:
			return None

		return self.__boundaryEPs

	def sPOrder(self):

		if self.__status != 1:
			return None

		return self.__sfcPorders

######## SCAG CLASS END ########