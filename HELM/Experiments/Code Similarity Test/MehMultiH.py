######## HEURISTIC CLASS BEGIN ########

class Heuristic:
	__status = None

	__mGrammar = None
	__mElements = None
	__mHELM = None
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
		self.__mHELM = HELM.HELM(copy.copy(metrics))
		metrics.pop('TR', None)
		self.__mMetrics = metrics

	######## PRIVATE METHODS ########

	def __mExpand(self, possibilities):
		suitability = self.__mHELM.hEvaluate({candidate:self.__mElements[candidate] for candidate in possibilities})

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
