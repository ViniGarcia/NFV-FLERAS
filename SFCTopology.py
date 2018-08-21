import nltk

class PartialOrder:
	__valid = False
	
	__elements = None
	__oDependencies = None
	__cDependencies = None

	def __init__(self, porderPEs, porderODs, porderCDs):
		
		self.__elements = porderPEs
		self.__oDependencies = porderODs
		self.__cDependencies = porderCDs

	def __dependenciesElementsValidate(self):
		for cDependency in self.__cDependencies + self.__oDependencies:
			if not cDependency[0] in self.__elements or not cDependency[1] in self.__elements:
				return False
		return True

	def __couplingDepenciesProcess(self):

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
						return False

				if beforeCoupling[-1] == cDependency[0] and afterCoupling[0] == cDependency[1]:
					for element in afterCoupling:
						elementsHash[element] = beforeKey
					elementsCouplings[beforeKey] += elementsCouplings[afterKey]
					elementsCouplings.pop(afterKey)
					continue
				else:
					return False

			if beforeKey.startswith('%') and not afterKey.startswith('%'):
				if elementsCouplings[beforeKey][-1] != cDependency[0]:
					return False
				elementsCouplings[beforeKey].append(afterKey)
				elementsHash[afterKey] = beforeKey
				continue

			if not beforeKey.startswith('%') and afterKey.startswith('%'):
				if elementsCouplings[afterKey][0] != cDependency[1]:
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

	def __orderDepenciesProcess(self, couplingGroups):

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
						return False
				else:
					return False
			if beforeGroup in beforeElements[afterGroup]:
				return False
			if afterGroup in afterElements[beforeGroup]:
				return False

			beforeElements[beforeGroup].append(afterGroup)
			beforeElements[beforeGroup] += beforeElements[afterGroup]
			afterElements[afterGroup].append(beforeGroup)
			afterElements[afterGroup] += afterElements[beforeGroup]

		return True 

	def validate(self):

		if self.__dependenciesElementsValidate():
			couplingGroups = self.__couplingDepenciesProcess()
			if isinstance(couplingGroups, tuple):
				if self.__orderDepenciesProcess(couplingGroups):
					self.__valid = True
					return True
		return False


class SFCTopology:
	__valid = False

	__sfcParser = None
	__boundaryEPs = None
	__operationalPEs = None
	
	__sfcTopology = None
	__sfcPorders = None

	def __init__(self, boundaryEPs, operationalPEs):

		kernelGrammar = """
			S 			 -> "IP" OPBLOCK

			OPBLOCK 	 -> TBRANCH | NTBRANCH | TPBLOCK OPBLOCK | TPBLOCK EP
			ROPBLOCK	 -> INTBRANCH | TPBLOCK ROPBLOCK | TPBLOCK
			TPBLOCK  	 -> PORDER | PELEM
			
			PORDER 		 -> "[" PELEM NPELEM "]" POEXCEPTION | "[" PELEM NPELEM "]"
			POEXCEPTION  -> "(" PELEM PELEM ")" POEXCEPTION | "(" PELEM PELEM ")" | "(" PELEM PELEM "*" ")" POEXCEPTION | "(" PELEM PELEM "*" ")"
			
			TBRANCH 	 -> TPBLOCK "{" OPBLOCK NEXTTBRANCH "}" 
			NEXTTBRANCH  -> "/" OPBLOCK NEXTTBRANCH | "/" OPBLOCK

			NTBRANCH	 -> TPBLOCK "{" ROPBLOCK NEXTNTBRANCH "}" OPBLOCK
			INTBRANCH	 -> TPBLOCK "{" ROPBLOCK NEXTNTBRANCH "}" ROPBLOCK
			NEXTNTBRANCH -> "/" ROPBLOCK NEXTNTBRANCH | "/" ROPBLOCK

			NPELEM 		 -> PELEM NPELEM | PELEM
		"""

		grammarPELEM = 'PELEM ->'
		for PE in operationalPEs:
			grammarPELEM += ' "' + PE + '" |'
		grammarPELEM = grammarPELEM[:len(grammarPELEM)-1] + '\n'

		grammarEP = 'EP ->'
		for EP in boundaryEPs:
			grammarEP += ' "' + EP + '" |'
		grammarEP = grammarEP[:len(grammarEP)-1]

		self.__boundaryEPs = boundaryEPs
		self.__operationalPEs = operationalPEs
		self.__mainParser = nltk.ChartParser(nltk.CFG.fromstring(kernelGrammar + grammarPELEM + grammarEP))

	def __getPorders(self):

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

	def requestTopology(self, sfcTopology):

		self.__valid = False
		
		if next(self.__mainParser.parse(sfcTopology.split()), None) == None:
			return False
		self.__sfcTopology = sfcTopology
		
		self.__getPorders()
		for porder in self.__sfcPorders:
			if not porder.validate():
				return False

		return True


'''topoOpt = SFCTopology(["EP1", "EP2", "EP3", "EP4"], ["PE1", "PE2", "PE3", "PE4", "PE5", "PE6", "PE7", "PE8", "PE9", "PE10", "PE11"])

sfcDefinition1 = "IP PE1 PE2 PE3 PE4 EP1"
sfcDefinition2 = "IP [ PE1 PE2 PE3 ] ( PE2 PE1 ) ( PE2 PE3 ) PE4 EP1"
sfcDefinition3 = "IP [ PE1 PE2 PE3 ] ( PE2 PE1 ) ( PE2 PE3 ) PE4 [ PE5 PE6 ] EP1"
sfcDefinition4 = "IP [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE7 PE1 ) ( PE3 PE7 ) PE4 [ PE5 PE6 ] EP1"
sfcDefinition5 = "IP [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE7 PE1 * ) ( PE3 PE7 ) PE4 [ PE5 PE6 ] EP1"
sfcDefinition6 = "IP [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE7 PE1 * ) ( PE3 PE7 * ) PE4 [ PE5 PE6 ] EP1"
sfcDefinition7 = "IP [ PE1 PE2 PE3 PE4 ] ( PE1 PE2 * ) ( PE2 PE3 * ) ( PE3 PE4 ) PE5 [ PE6 PE7 ] EP1"
sfcDefinition8 = "IP [ PE1 PE2 PE3 PE4 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE3 PE4 ) PE5 [ PE6 PE7 ] EP1"
sfcDefinition9 = "IP [ PE1 PE2 PE3 PE4 ] ( PE1 PE2 * ) ( PE3 PE4 * ) ( PE2 PE3 * ) PE5 [ PE6 PE7 ] EP1"
sfcDefinition10 = "IP [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE5 PE2 ) EP1"
sfcDefinition11 = "IP [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE3 PE4 * ) EP1"
sfcDefinition12 = "IP [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE5 PE2 ) EP1"
sfcDefinition13 = "IP [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE7 PE2 ) ( PE5 PE7 ) EP1"
sfcDefinition14 = "IP [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { PE4 / PE5 } PE6 EP1"
sfcDefinition15 = "IP [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] / PE6 / PE8 } PE9 EP1"
sfcDefinition16 = "IP [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] / PE6 { PE7 / PE8 } PE9 / PE10 } PE11 EP1"
sfcDefinition17 = "IP [ PE1 PE2 PE3 ] ( PE2 PE3 ) { [ PE4 PE5 ] EP1 / PE6 { PE7 / PE8 } PE9 EP2 / PE10 EP3 }"
sfcDefinition18 = "IP [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE3 PE5 ) EP1"
sfcDefinition19 = "IP [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE1 PE3 ) EP1"

sfcError1 = "IP PE1 PE2 PE3 EP1 PE4 EP1"
sfcError2 = "IP [ PE1 PE2 PE3 EP2 ] ( PE2 PE1 ) ( PE2 PE3 ) PE4 EP1"
sfcError3 = "IP [ PE1 PE2 PE3 ] ( PE2 PE1 ) PE4 ( PE2 PE3 ) EP1"
sfcError4 = "IP [ PE1 PE2 PE3 ] ( PE2 PE1 ) ( PE2 EP1 ) PE4 EP1"
sfcError5 = "IP [ PE1 PE2 PE3 ] ( PE2 PE1 ) ( PE1 PE2 ) PE4 [ PE5 PE6 ] EP1"
sfcError6 = "IP [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE7 PE1 ) ( PE2 PE7 ) PE4 [ PE5 PE6 ] EP1"
sfcError7 = "IP [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE2 PE7 ) ( PE7 PE1 ) PE4 [ PE5 PE6 ] EP1"
sfcError8 = "IP [ PE1 PE2 PE3 PE7 ] ( PE1 PE2 ) ( PE3 PE2 * ) ( PE3 PE7 * ) PE4 [ PE5 PE6 ] EP1"
sfcError9 = "IP [ PE1 PE2 PE3 PE7 ] ( PE1 PE3 ) ( PE7 PE1 ) ( PE3 PE7 * ) PE4 [ PE5 PE6 ] EP1"
sfcError10 = "IP [ PE1 PE2 PE3 PE7 ] ( PE3 PE1 ) ( PE1 PE7 ) ( PE3 PE7 * ) PE4 [ PE5 PE6 ] EP1"
sfcError11 = "IP [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE5 PE2 ) ( PE1 PE4 ) EP1"
sfcError12 = "IP [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE3 PE5 * ) EP1"
sfcError13 = "IP [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE7 PE1 ) ( PE2 PE7 ) EP1"
sfcError14 = "IP [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { PE4 / PE5 EP2 } PE6 EP1"
sfcError15 = "IP [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] } PE9 EP1"
sfcError16 = "IP [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] / PE6 { PE7 / PE8 EP2 } PE9 / PE10 } PE11 EP1"
sfcError17 = "IP [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] / PE6 { PE7 / PE8 EP2 } EP2 / PE10 } PE11 EP1"
sfcError18 = "IP [ PE1 PE2 PE3 ] ( PE2 PE3 * ) { [ PE4 PE5 ] / PE6 { PE7 EP2 / PE8 EP3 } / PE10 } PE11 EP1"
sfcError19 = "IP [ PE1 PE2 PE3 ] ( PE2 PE3 ) { [ PE4 PE5 ] EP1 / PE6 { PE7 / PE8 } EP2 / PE10 EP3 }"
sfcError20 = "IP [ PE1 PE2 PE3 PE4 PE5 PE6 PE7 ] ( PE2 PE3 * ) ( PE1 PE2 * ) ( PE4 PE5 * ) ( PE5 PE6 * ) ( PE3 PE2 ) EP1"

sfcBranch1 = "IP [ PE1 PE2 ] ( PE2 PE1 ) PE3 { PE4 EP1 / PE4 EP2 }"
sfcBranch2 = "IP [ PE1 PE2 ] ( PE2 PE1 ) PE3 { [ PE4 PE5 ] EP1 / PE4 EP2 }"
sfcBranch3 = "IP [ PE1 PE2 ] ( PE2 PE1 ) PE3 { [ PE4 PE5 ] EP1 / PE4 PE5 EP2 }"

print "T1:" + str(topoOpt.requestTopology(sfcDefinition1))
print "T2:" + str(topoOpt.requestTopology(sfcDefinition2))
print "T3:" + str(topoOpt.requestTopology(sfcDefinition3))
print "T4:" + str(topoOpt.requestTopology(sfcDefinition4))
print "T5:" + str(topoOpt.requestTopology(sfcDefinition5))
print "T6:" + str(topoOpt.requestTopology(sfcDefinition6))
print "T7:" + str(topoOpt.requestTopology(sfcDefinition7))
print "T8:" + str(topoOpt.requestTopology(sfcDefinition8))
print "T9:" + str(topoOpt.requestTopology(sfcDefinition9))
print "T10:" + str(topoOpt.requestTopology(sfcDefinition10))
print "T11:" + str(topoOpt.requestTopology(sfcDefinition11))
print "T12:" + str(topoOpt.requestTopology(sfcDefinition12))
print "T13:" + str(topoOpt.requestTopology(sfcDefinition13))
print "T14:" + str(topoOpt.requestTopology(sfcDefinition14))
print "T15:" + str(topoOpt.requestTopology(sfcDefinition15))
print "T16:" + str(topoOpt.requestTopology(sfcDefinition16))
print "T17:" + str(topoOpt.requestTopology(sfcDefinition17))
print "T18:" + str(topoOpt.requestTopology(sfcDefinition18))
print "T19:" + str(topoOpt.requestTopology(sfcDefinition19))
print " "

print "E1:" + str(topoOpt.requestTopology(sfcError1))
print "E2:" + str(topoOpt.requestTopology(sfcError2))
print "E3:" + str(topoOpt.requestTopology(sfcError3))
print "E4:" + str(topoOpt.requestTopology(sfcError4))
print "E5:" + str(topoOpt.requestTopology(sfcError5))
print "E6:" + str(topoOpt.requestTopology(sfcError6))
print "E7:" + str(topoOpt.requestTopology(sfcError7))
print "E8:" + str(topoOpt.requestTopology(sfcError8))
print "E9:" + str(topoOpt.requestTopology(sfcError9))
print "E10:" + str(topoOpt.requestTopology(sfcError10))
print "E11:" + str(topoOpt.requestTopology(sfcError11))
print "E12:" + str(topoOpt.requestTopology(sfcError12))
print "E13:" + str(topoOpt.requestTopology(sfcError13))
print "E14:" + str(topoOpt.requestTopology(sfcError14))
print "E15:" + str(topoOpt.requestTopology(sfcError15))
print "E16:" + str(topoOpt.requestTopology(sfcError16))
print "E17:" + str(topoOpt.requestTopology(sfcError17))
print "E18:" + str(topoOpt.requestTopology(sfcError18))
print "E19:" + str(topoOpt.requestTopology(sfcError19))
print "E20:" + str(topoOpt.requestTopology(sfcError20))
print " "

print "B1:" + str(topoOpt.requestTopology(sfcBranch1))
print "B2:" + str(topoOpt.requestTopology(sfcBranch2))
print "B3:" + str(topoOpt.requestTopology(sfcBranch3))'''