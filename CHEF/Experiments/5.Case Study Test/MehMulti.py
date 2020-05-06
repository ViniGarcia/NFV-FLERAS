############## IMPORTS ##############

import nltk
import itertools
import yaml
import os
import copy
import CHEF

######## GREMMAR CLASS BEGIN ########

class Grammar:
	__status = None

	__gParser = None
	__gElements = None

	__gTopology = None
	__gOptOrder = None
	__gSplit = None
	__gParallel = None

	######## CONSTRUCTOR ########

	def __init__(self, gElements):

		kernelGrammar = """
			START 		 -> MODULES
			MODULES		 -> ORDER MODULES | MOD
			ORDER		 -> MOD "-"
			MOD			 -> OPTORDER | SPLIT | PARALLEL | TERM
			OPTORDER	 -> "(" TERM MORETERM ")" | "(" TERM ")"
			SPLIT		 -> TERM "[" MODULES MOREMOD "]"
			PARALLEL	 -> TERM "{" TERM MORETERM ";" MODULES ";" NUM "}" | TERM "{" TERM ";" MODULES ";" NUM "}"
			MORETERM	 -> TERM MORETERM | TERM
			MOREMOD		 -> "," MODULES MOREMOD | "," MODULES
			NUM			 -> "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
		"""

		termString = "TERM ->"
		for element in gElements:
			termString += ' "' + element + '" |'
		termString = termString[:-2]

		self.__gElements = gElements
		self.__gParser = nltk.ChartParser(nltk.CFG.fromstring(kernelGrammar + termString))
		self.__status = 0

	######## PRIVATE METHODS ########

	def __gOptionalOrder(self):

		self.__gOptOrder = []
		gSplitted = self.__gTopology.split()

		for index in range(0, len(gSplitted)):

			if gSplitted[index] == '(':
				gElements = []

				index += 1
				while gSplitted[index] != ')':
					gElements.append(gSplitted[index])
					index += 1

				self.__gOptOrder.append(gElements)

	#Does not support nested splits (used for tests only)
	def __gSplitSegments(self):

		self.__gSplit = []
		gSplitted = self.__gTopology.split()

		for index in range(0, len(gSplitted)):

			if gSplitted[index] == '[':
				gDictionary = {'T':gSplitted[index-1], 'M':[]}
				gElements = []

				while gSplitted[index] != ']':
					index += 1
					while gSplitted[index] != ',' and gSplitted[index] != ']':
						gElements.append(gSplitted[index])
						index += 1
					gDictionary['M'].append(gElements)

				self.__gSplit.append(gDictionary)

	#Does not support nested parallels (used for tests only)
	def __gParallelSegments(self):

		self.__gParallel = []
		gSplitted = self.__gTopology.split()

		for index in range(0, len(gSplitted)):

			if gSplitted[index] == '{':
				gDictionary = {'T':gSplitted[index-1], 'P':[], 'M':[], 'N':0}
				gElements = []

				while gSplitted[index] != '}':
					index += 1

					while gSplitted[index] != ';':
						gDictionary['P'].append(gSplitted[index])
						index += 1
					if not gDictionary['T'] in gDictionary['P']:
						self.__status = -2
						return
					gDictionary['P'].remove(gDictionary['T'])

					index += 1
					while gSplitted[index] != ';':
						while gSplitted[index] != '-' and gSplitted[index] != ';':
							gElements.append(gSplitted[index])
							index += 1
						gDictionary['M'].append(gElements)
						gElements = []
						if gSplitted[index] == '-':
							index += 1

					index += 1
					gDictionary['N'] = int(gSplitted[index])
					break

				self.__gParallel.append(gDictionary)

	######## PUBLIC METHODS ########

	def gValidate(self, gTopology):

		self.__gTopology = None
		self.__gOptOrder = None

		if next(self.__gParser.parse(gTopology.split()), None) == None:
			self.__status = -1
			return False

		self.__gTopology = gTopology
		self.__gOptionalOrder()
		self.__gSplitSegments()
		self.__gParallelSegments()

		if self.__status == 0:
			self.__status = 1
			return True

	def gStatus(self):

		return self.__status

	def gElements(self):

		if self.__status != 1:
			return None

		return self.__gElements

	def gTopology(self):

		if self.__status != 1:
			return None

		return self.__gTopology

	def gOptOrder(self):

		if self.__status != 1:
			return None

		return self.__gOptOrder

	def gSplit(self):

		if self.__status != 1:
			return None

		return self.__gSplit

	def gParallel(self):

		if self.__status != 1:
			return None

		return self.__gParallel

######## GRAMMAR CLASS END ########

######## EXHAUSTIVE CLASS BEGIN ########

class Exhaustive:
	__status = None

	__mGrammar = None
	__mElements = None
	__mMetrics = None
	__mCHEF = None

	__mCandidates = None
	__mPartialResults = None
	__mSuggestion = None
	__mSI = None

	######## CONSTRUCTOR ########

	def __init__(self, grammar, elements, metrics):

		if grammar.gStatus() != 1:
			self.__status = -1
			return

		self.__status = 0
		self.__mElements = elements
		self.__mGrammar = grammar
		self.__mCHEF = CHEF.CHEF(copy.copy(metrics))
		metrics.pop('TR', None)
		self.__mMetrics = metrics

	######## PRIVATE METHODS ########

	def __mExpand(self):

		optOrder = []
		parallel = []

		for opt in self.__mGrammar.gOptOrder():
			permutation = list(itertools.permutations(opt))
			optOrder.append(permutation)
		optOrder = list(itertools.product(*optOrder))

		for par in self.__mGrammar.gParallel():
			permutation = list(itertools.permutations(par['P']))
			parallel.append(permutation)
		parallel = list(itertools.product(*parallel))

		firmOrder = list(itertools.product(optOrder, parallel))
		topology = self.__mGrammar.gTopology().split()
		elements = self.__mGrammar.gElements()
		self.__mCandidates = []

		for ordering in firmOrder:
			structure = []
			optCounter = 0
			parCounter = 0
			index = 0

			while index < len(topology):

				if index < len(topology) - 1:
					if topology[index + 1] == '{':
						for parElement in ordering[1][parCounter]:
							structure.append(parElement)
						structure.append(topology[index])
						structure.append('[')
						while topology[index] != ';':
							index += 1
						index += 1
						init = len(structure)
						continue

				if topology[index] == ';':
					end = len(structure)
					for replicate in range(self.__mGrammar.gParallel()[parCounter]['N'] - 1):
						structure.append(',')
						structure.extend(structure[init:end])
					index += 1
					continue

				if topology[index] == '}':
					structure.append(']')
					parCounter += 1
					index += 1
					continue

				if topology[index] == '(':
					for optElement in ordering[0][optCounter]:
						structure.append(optElement)
					optCounter += 1
					while topology[index] != ')':
						index += 1
					index += 1
					continue

				if topology[index] == '[' or topology[index] == ',' or topology[index] == ']':
					structure.append(topology[index])
					index += 1
					continue

				if topology[index] in elements:
					structure.append(topology[index])
					index += 1
					continue

				index += 1

			self.__mCandidates.append(structure)
			self.__status = 1

	def __mProcess(self):

		self.__mPartialResults = {}

		for index in range(len(self.__mCandidates)):
			self.__mPartialResults[index] = {}
			for metric in self.__mMetrics:
				self.__mPartialResults[index][metric] = 0
			self.__mPartialResults[index]['TR'] = 0
			ratio = [1]
			context = 0

			for element in self.__mCandidates[index]:

				if element in self.__mElements:
					for metric in self.__mMetrics:
						self.__mPartialResults[index][metric] += ratio[context] * self.__mElements[element][metric]
					ratio[context] *= self.__mElements[element]['TR']
					self.__mPartialResults[index]['TR'] += ratio[context]
					continue

				if element == '[' or element == ',':
					context += 1
					ratio.append(ratio[0])

				if element == ']':
					update = 0
					for jndex in range(1, len(ratio)):
						update += ratio[jndex] / (len(ratio) - 1)
					ratio = ratio[:1]
					ratio[0] = update
					context = 0

	def __mEvaluate(self):
		self.__mPartialResults = self.__mCHEF.cEvaluate(self.__mPartialResults)

		self.__mSuggestion = [0]
		compare = self.__mPartialResults[0]

		for index in range(1, len(self.__mPartialResults)):

			if self.__mPartialResults[index] > compare:
				self.__mSuggestion = [index]
				compare = self.__mPartialResults[index]
				continue

			if self.__mPartialResults[index] == compare:
				self.__mSuggestion.append(index)

		self.__mSI = compare

	######## PUBLIC METHODS ########

	def mCompose(self):

		if self.__status != 0:
			return

		self.__mExpand()
		self.__mProcess()
		self.__mEvaluate()
		self.__status = 1

	def mStatus(self):

		return self.__status

	def mCandidates(self):

		if self.__status != 1:
			return None

		return self.__mCandidates

	def mPartialResults(self):

		if self.__status != 1:
			return None

		return self.__mPartialResults

	def mSuggestion(self):

		if self.__status != 1:
			return None

		return self.__mSuggestion

	def mFirmSuggestion(self):

		if self.__status != 1:
			return None

		return self.__mSuggestion[0]

	def mSI(self):

		if self.__status != 1:
			return None

		return self.__mSI

######### EXHAUSTIVE CLASS END #########

######## HEURISTIC CLASS BEGIN ########

class Heuristic:
	__status = None

	__mGrammar = None
	__mElements = None
	__mCHEF = None
	__mMetrics = None

	__mCandidates = None
	__mSuggestion = None

	######## CONSTRUCTOR ########

	def __init__(self, grammar, elements, metrics):

		if grammar.gStatus() != 1:
			self.__status = -1
			return

		self.__status = 0
		self.__mElements = elements
		self.__mGrammar = grammar
		self.__mCHEF = CHEF.CHEF(copy.copy(metrics))
		metrics.pop('TR', None)
		self.__mMetrics = metrics

	######## PRIVATE METHODS ########

	def __mExpand(self, possibilities):
		suitability = self.__mCHEF.cEvaluate({candidate:self.__mElements[candidate] for candidate in possibilities})

		compare = suitability[possibilities[0]]
		chosen = 0

		for index in range(1, len(possibilities)):
			if suitability[possibilities[index]] > compare:
				chosen = index

		return possibilities.pop(chosen)

	def __mProcess(self):
		optOrder = self.__mGrammar.gOptOrder()
		parallel = self.__mGrammar.gParallel()
		topology = self.__mGrammar.gTopology().split()
		elements = self.__mGrammar.gElements()
		self.__mCandidates = []

		optCounter = 0
		parCounter = 0
		index = 0
		while index < len(topology):

			if index < len(topology) - 1:
				if topology[index + 1] == '{':
					parElements = parallel[parCounter]['P']
					while len(parElements) > 0:
						self.__mCandidates.append(self.__mExpand(parElements))
					self.__mCandidates.append(topology[index])
					self.__mCandidates.append('[')
					while topology[index] != ';':
						index += 1
					index += 1
					init = len(self.__mCandidates)
					continue

			if topology[index] == ';':
				end = len(self.__mCandidates)
				for replicate in range(parallel[parCounter]['N'] - 1):
					self.__mCandidates.append(',')
					self.__mCandidates.extend(self.__mCandidates[init:end])
				index += 1
				continue

			if topology[index] == '}':
				self.__mCandidates.append(']')
				parCounter += 1
				index += 1
				continue

			if topology[index] == '(':
				optElements = optOrder[optCounter]
				while len(optElements) > 0:
					self.__mCandidates.append(self.__mExpand(optElements))
				optCounter += 1
				while topology[index] != ')':
					index += 1
				index += 1
				continue

			if topology[index] == '[' or topology[index] == ',' or topology[index] == ']':
				self.__mCandidates.append(topology[index])
				index += 1
				continue

			if topology[index] in elements:
				self.__mCandidates.append(topology[index])
				index += 1
				continue

			index += 1

		self.__mCandidates = [self.__mCandidates]

	def __mEvaluate(self):

		self.__mSuggestion = [0]

	######## PUBLIC METHODS ########

	def mCompose(self):

		if self.__status != 0:
			return

		self.__mProcess()
		self.__mEvaluate()
		self.__status = 1

	def mStatus(self):

		return self.__status

	def mCandidates(self):

		if self.__status != 1:
			return None

		return self.__mCandidates

	def mSuggestion(self):

		if self.__status != 1:
			return None

		return self.__mSuggestion

	def mFirmSuggestion(self):

		if self.__status != 1:
			return None

		return self.__mSuggestion[0]

######### HEURISTIC CLASS END #########

######## COMPOSER CLASS BEGIN ########

class Composer:
	__status = None

	__cMethod = None
	__cGrammar = None
	__cComposer = None

	######## CONSTRUCTOR ########

	def __init__(self, method):
		if method != 1 and method != 2:
			return
		self.__cMethod = method
		self.__status = 0

	######## PRIVATE METHODS ########

	def __cValidate(self, request):

		file = open(request, "r")
		data = file.read()
		file.close()

		try:
			yamlData = yaml.load(data, Loader=yaml.FullLoader)
		except:
			self.__status = -2
			return -2

		if not "TOPOLOGY" in yamlData or not "METRICS" in yamlData or not "ELEMENTS" in yamlData:
			self.__status = -3
			return -3

		if not isinstance(yamlData["TOPOLOGY"], str) or not isinstance(yamlData["METRICS"], dict) or not isinstance(yamlData["ELEMENTS"], dict):
			self.__status = -4
			return -4

		for element in yamlData["ELEMENTS"]:
			if not isinstance(yamlData["ELEMENTS"][element], dict):
				self.__status = -5
				return -5
			for metric in yamlData["ELEMENTS"][element]:
				if not isinstance(yamlData["ELEMENTS"][element][metric], float) and not isinstance(yamlData["ELEMENTS"][element][metric], int):
					self.__status = -6
					return -6

		if not "TR" in yamlData["METRICS"]:
			self.__status = -7
			return -7

		for metric in yamlData["METRICS"]:
			if not isinstance(yamlData["METRICS"][metric], tuple):
				self.__status = -8
				return -8
			if len(yamlData["METRICS"][metric]) != 2:
				self.__status = -9
				return -9
			if not isinstance(yamlData["METRICS"][metric][1], float) or not isinstance(yamlData["METRICS"][metric][0], str):
				self.__status = -10
				return -10
			if yamlData["METRICS"][metric][1] <= 0:
				self.__status = -11
				return -11
			if yamlData["METRICS"][metric][0] != "MIN" and yamlData["METRICS"][metric][0] != "MAX":
				self.__status = -12
				return -12

		return yamlData

	######## PUBLIC METHODS ########

	def cCompose(self, request):

		if not os.path.isfile(request):
			self.__status = -1
			return -1

		data = self.__cValidate(request)
		if self.__status < 0:
			return self.__status

		self.__cGrammar = Grammar(list(data["ELEMENTS"].keys()))
		self.__cGrammar.gValidate(data["TOPOLOGY"])
		if self.__cGrammar.gStatus() < 0:
			self.__status = -13
			return -13

		if self.__cMethod == 1:
			self.__cComposer = Exhaustive(self.__cGrammar, data["ELEMENTS"], data["METRICS"])
		else:
			self.__cComposer = Heuristic(self.__cGrammar, data["ELEMENTS"], data["METRICS"])
		self.__cComposer.mCompose()
		if self.__cComposer.mStatus() < 0:
			self.__status = -14
			return -14

		self.__status = 1

	def cSuggestion(self):

		if self.__status != 1:
			return None

		ids = self.__cComposer.mSuggestion()
		candidates = self.__cComposer.mCandidates()

		result = []
		for index in ids:
			result.append(candidates[index])

		return result

	def cFirmSuggestion(self):

		if self.__status != 1:
			return None

		return self.__cComposer.mCandidates()[self.__cComposer.mFirmSuggestion()]

	def cSI(self):
		
		#Exhaustive only
		if self.__status != 1:
			return None

		return self.__cComposer.mSI()

	def cStatus(self):
		
		return self.__status		

######### COMPOSER CLASS END #########

