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

########### cuSTOM CLASS DESCRIPTION ############

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

############## cuSTOM CLASS BEGIN ###############

import nltk

class cuSTOM:
	__status = None

	__topologyEPs = None
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

	def __stPorders(self):

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

	def stValidate(self, serviceTopology):

		self.__serviceTopology = None
		self.__servicePorders = None

		if next(self.__mainParser.parse(serviceTopology.split()), None) == None:
			self.__status = -1
			return False

		self.__serviceTopology = serviceTopology
		self.__stPorders()

		for porder in self.__servicePorders:
			if not porder.poValid():
				self.__status = -2 + porder.poStatus()
				return False

		self.__status = 1
		return True

	def stStatus(self):

		return self.__status

	def stTopology(self):

		if self.__status != 1:
			return None

		return self.__serviceTopology

	def stVNFs(self):

		if self.__status != 1:
			return None

		return self.__topologyVNFs

	def stPNFs(self):

		if self.__status != 1:
			return None

		return self.__topologyPNFs

	def stDomains(self):

		if self.__status != 1:
			return None

		return self.__topologyDomains

	def stMachines(self):

		if self.__status != 1:
			return None

		return self.__topologyMachines

	def stEPs(self):

		if self.__status != 1:
			return None

		return self.__topologyEPs

	def stPOrder(self):

		if self.__status != 1:
			return None

		return self.__servicePorders

############### cuSTOM CLASS END ################

################## TEST AREA ####################

grammar = cuSTOM(["PE1", "PE2", "PE3", "PE4", "PE5", "PE6", "PE7", "PE8", "PE9", "PE10", "PE11"], [], [], [], ["EP1", "EP2", "EP3", "EP4"], )
sfcDefinition1 = "IN PE1 PE2 PE3 PE4 EP1"
sfcDefinition2 = "IN [ PE1 PE2 PE3 ] ( PE2 PE1 ) ( PE2 PE3 ) PE4 EP1"
sfcDefinition3 = "IN [ PE1 PE2 PE3 ] ( PE2 PE1 ) ( PE2 PE3 ) PE4 [ PE5 PE6 ] EP1"
sfcDefinition4 = "IN [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE7 PE1 ) ( PE3 PE7 ) PE4 [ PE5 PE6 ] EP1"
sfcDefinition5 = "IN [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE7 PE1 * ) ( PE3 PE7 ) PE4 [ PE5 PE6 ] EP1"
sfcDefinition6 = "IN [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE7 PE1 * ) ( PE3 PE7 * ) PE4 [ PE5 PE6 ] EP1"
sfcDefinition7 = "IN [ PE1 PE2 PE3 PE4 ] ( PE1 PE2 * ) ( PE2 PE3 * ) ( PE3 PE4 ) PE5 [ PE6 PE7 ] EP1"
sfcDefinition8 = "IN [ PE1 PE2 PE3 PE4 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE3 PE4 ) PE5 [ PE6 PE7 ] EP1"
sfcDefinition9 = "IN [ PE1 PE2 PE3 PE4 ] ( PE1 PE2 * ) ( PE3 PE4 * ) ( PE2 PE3 * ) PE5 [ PE6 PE7 ] EP1"
sfcDefinition10 = "IN [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE5 PE2 ) EP1"
sfcDefinition11 = "IN [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE3 PE4 * ) EP1"
sfcDefinition12 = "IN [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE5 PE2 ) EP1"
sfcDefinition13 = "IN [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE7 PE2 ) ( PE5 PE7 ) EP1"
sfcDefinition14 = "IN [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { PE4 / PE5 } PE6 EP1"
sfcDefinition15 = "IN [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] / PE6 / PE8 } PE9 EP1"
sfcDefinition16 = "IN [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] / PE6 { PE7 / PE8 } PE9 / PE10 } PE11 EP1"
sfcDefinition17 = "IN [ PE1 PE2 PE3 ] ( PE2 PE3 ) { [ PE4 PE5 ] EP1 / PE6 { PE7 / PE8 } PE9 EP2 / PE10 EP3 }"
sfcDefinition18 = "IN [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE3 PE5 ) EP1"
sfcDefinition19 = "IN [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE1 PE3 ) EP1"
sfcError1 = "IN PE1 PE2 PE3 EP1 PE4 EP1"
sfcError2 = "IN [ PE1 PE2 PE3 EP2 ] ( PE2 PE1 ) ( PE2 PE3 ) PE4 EP1"
sfcError3 = "IN [ PE1 PE2 PE3 ] ( PE2 PE1 ) PE4 ( PE2 PE3 ) EP1"
sfcError4 = "IN [ PE1 PE2 PE3 ] ( PE2 PE1 ) ( PE2 EP1 ) PE4 EP1"
sfcError5 = "IN [ PE1 PE2 PE3 ] ( PE2 PE1 ) ( PE1 PE2 ) PE4 [ PE5 PE6 ] EP1"
sfcError6 = "IN [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE7 PE1 ) ( PE2 PE7 ) PE4 [ PE5 PE6 ] EP1"
sfcError7 = "IN [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE2 PE7 ) ( PE7 PE1 ) PE4 [ PE5 PE6 ] EP1"
sfcError8 = "IN [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE3 PE2 * ) ( PE3 PE7 * ) PE4 [ PE5 PE6 ] EP1"
sfcError9 = "IN [ PE1 PE2 PE3 PE7 ] ( PE1 PE3 ) ( PE7 PE1 ) ( PE3 PE7 * ) PE4 [ PE5 PE6 ] EP1"
sfcError10 = "IN [ PE1 PE2 PE3 PE7 ] ( PE3 PE1 ) ( PE1 PE7 ) ( PE3 PE7 * ) PE4 [ PE5 PE6 ] EP1"
sfcError11 = "IN [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE5 PE2 ) ( PE1 PE4 ) EP1"
sfcError12 = "IN [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE3 PE5 * ) EP1"
sfcError13 = "IN [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE7 PE1 ) ( PE2 PE7 ) EP1"
sfcError14 = "IN [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { PE4 / PE5 EP2 } PE6 EP1"
sfcError15 = "IN [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] } PE9 EP1"
sfcError16 = "IN [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] / PE6 { PE7 / PE8 EP2 } PE9 / PE10 } PE11 EP1"
sfcError17 = "IN [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] / PE6 { PE7 / PE8 EP2 } EP2 / PE10 } PE11 EP1"
sfcError18 = "IN [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] / PE6 { PE7 EP2 / PE8 EP3 } / PE10 } PE11 EP1"
sfcError19 = "IN [ PE1 PE2 PE3 ] ( PE2 PE3 ) { [ PE4 PE5 ] EP1 / PE6 { PE7 / PE8 } EP2 / PE10 EP3 }"
sfcError20 = "IN [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE3 PE2 ) EP1"
sfcBranch1 = "IN [ PE1 PE2 ] ( PE2 PE1 ) PE3 { PE4 EP1 / PE4 EP2 }"
sfcBranch2 = "IN [ PE1 PE2 ] ( PE2 PE1 ) PE3 { [ PE4 PE5 ] EP1 / PE4 EP2 }"
sfcBranch3 = "IN [ PE1 PE2 ] ( PE2 PE1 ) PE3 { [ PE4 PE5 ] EP1 / PE4 PE5 EP2 }"

print ("T1:" + str(grammar.stValidate(sfcDefinition1)))
print ("T2:" + str(grammar.stValidate(sfcDefinition2)))
print ("T3:" + str(grammar.stValidate(sfcDefinition3)))
print ("T4:" + str(grammar.stValidate(sfcDefinition4)))
print ("T5:" + str(grammar.stValidate(sfcDefinition5)))
print ("T6:" + str(grammar.stValidate(sfcDefinition6)))
print ("T7:" + str(grammar.stValidate(sfcDefinition7)))
print ("T8:" + str(grammar.stValidate(sfcDefinition8)))
print ("T9:" + str(grammar.stValidate(sfcDefinition9)))
print ("T10:" + str(grammar.stValidate(sfcDefinition10)))
print ("T11:" + str(grammar.stValidate(sfcDefinition11)))
print ("T12:" + str(grammar.stValidate(sfcDefinition12)))
print ("T13:" + str(grammar.stValidate(sfcDefinition13)))
print ("T14:" + str(grammar.stValidate(sfcDefinition14)))
print ("T15:" + str(grammar.stValidate(sfcDefinition15)))
print ("T16:" + str(grammar.stValidate(sfcDefinition16)))
print ("T17:" + str(grammar.stValidate(sfcDefinition17)))
print ("T18:" + str(grammar.stValidate(sfcDefinition18)))
print ("T19:" + str(grammar.stValidate(sfcDefinition19)))
print (" ")
print ("E1:" + str(grammar.stValidate(sfcError1)))
print ("E2:" + str(grammar.stValidate(sfcError2)))
print ("E3:" + str(grammar.stValidate(sfcError3)))
print ("E4:" + str(grammar.stValidate(sfcError4)))
print ("E5:" + str(grammar.stValidate(sfcError5)))
print ("E6:" + str(grammar.stValidate(sfcError6)))
print ("E7:" + str(grammar.stValidate(sfcError7)))
print ("E8:" + str(grammar.stValidate(sfcError8)))
print ("E9:" + str(grammar.stValidate(sfcError9)))
print ("E10:" + str(grammar.stValidate(sfcError10)))
print ("E11:" + str(grammar.stValidate(sfcError11)))
print ("E12:" + str(grammar.stValidate(sfcError12)))
print ("E13:" + str(grammar.stValidate(sfcError13)))
print ("E14:" + str(grammar.stValidate(sfcError14)))
print ("E15:" + str(grammar.stValidate(sfcError15)))
print ("E16:" + str(grammar.stValidate(sfcError16)))
print ("E17:" + str(grammar.stValidate(sfcError17)))
print ("E18:" + str(grammar.stValidate(sfcError18)))
print ("E19:" + str(grammar.stValidate(sfcError19)))
print ("E20:" + str(grammar.stValidate(sfcError20)))
print (" ")
print ("B1:" + str(grammar.stValidate(sfcBranch1)))
print ("B2:" + str(grammar.stValidate(sfcBranch2)))
print ("B3:" + str(grammar.stValidate(sfcBranch3)))

#grammar = cuSTOM(["VNF1", "VNF2", "VNF3", "VNF4", "VNF5", "VNF6", "VNF7"], ["PNF1", "PNF2"], ["DOM1", "DOM2"], ["PHY1", "PHY2"], ["EN1", "EN2"])
#print(grammar.stValidate("IN VNF1 EN1"))
#print(grammar.stValidate("IN VNF1 VNF2 EN1"))
#print(grammar.stValidate("IN VNF1 < DOM1 > VNF2 EN1"))
#print(grammar.stValidate("IN [ VNF1 < PHY1 | DOM1 > VNF2 < DOM2 > ] EN1"))
#print(grammar.stValidate("IN [ VNF1 < PHY1 | DOM1 > VNF2 ] { VNF3 < DOM1 > VNF2 EN1 / VNF3 < DOM1 > VNF4 { VNF5 / VNF6 } VNF7 EN2 }"))

#################################################
