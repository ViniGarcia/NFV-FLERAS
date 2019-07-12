######## EXHAUSTIVE CLASS BEGIN ########

class Exhaustive:
	__status = None

	__mGrammar = None
	__mElements = None
	__mMetrics = None
	__mHELM = None

	__mCandidates = None
	__mPartialResults = None
	__mSuggestion = None

	######## CONSTRUCTOR ########

	def __init__(self, grammar, elements, metrics):

		if grammar.gStatus() != 1:
			self.__status = -1
			return

		self.__status = 0
		self.__mElements = elements
		self.__mGrammar = grammar
		self.__mHELM = HELM.HELM(copy.copy(metrics))
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
		self.__mPartialResults = self.__mHELM.hEvaluate(self.__mPartialResults)

		self.__mSuggestion = [0]
		compare = self.__mPartialResults[0]

		for index in range(1, len(self.__mPartialResults)):

			if self.__mPartialResults[index] > compare:
				self.__mSuggestion = [index]
				compare = self.__mPartialResults[index]
				continue

			if self.__mPartialResults[index] == compare:
				self.__mSuggestion.append(index)

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

######### EXHAUSTIVE CLASS END #########
