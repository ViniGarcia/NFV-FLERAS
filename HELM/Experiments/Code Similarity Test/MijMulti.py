######## HEURISTIC CLASS BEGIN ########

class Heuristic:
	__status = None

	__hNetwork = None
	__hTime = None
	__hLimit = None
	__hMetrics = None
	__hHELM = None

	__hSuggestion = None

	######## CONSTRUCTOR ########

	def __init__(self, network):

		self.__hSetup(network)
		self.__status = 0

	######## PRIVATE METHODS ########

	def __hSlot(self, time, size, node):

		delay = 0
		counter = 0
		current = time % self.__hNetwork[node]['BT']

		if self.__hNetwork[node]['BF'] < size:
			return (-1, -1)

		for index in range(self.__hNetwork[node]['BT'] + 1):
			check = (current + index) % self.__hNetwork[node]['BT']
			if not self.__hNetwork[node]['BD'][check]:
				counter += 1
				if counter == 1:
					init = check
				if counter == size:
					return (time + delay, init, delay)
			else:
				if counter != 0:
					delay += counter
					counter = 0
				delay += 1

		return (-1, -1)

	def __hEvaluate(self, request, function, nodes):

		partialResults = {}
		for processor in nodes:
			partialResults[processor] = {}

			if "FT" in self.__hMetrics:
				partialResults[processor]['FT'] = request['ELEMENTS'][function]['BT'] + nodes[processor][2]

			if "RV" in self.__hMetrics:
				partialResults[processor]['RV'] = request['ELEMENTS'][function]['BT'] / self.__hNetwork[processor]['BF']

			if "C" in self.__hMetrics:
				partialResults[processor]['C'] = request['ELEMENTS'][function]['BT'] * self.__hNetwork[processor]['C']

			for metric in (self.__hMetrics.keys() - set(["FT", "RV", "C"])):
				partialResults[processor][metric] = request['ELEMENTS'][function]['BT'] * request["METRICS"][metric]["DATA"][processor]

		partialResults = self.__hHELM.hEvaluate(partialResults)
		return min([candidate for candidate in partialResults.items() if candidate[1] == max(partialResults.items(), key=lambda x: x[1])[1]])[0]

	def __hSetup(self, network):

		for node in network:
			network[node]['BF'] = network[node]['BT']
			network[node]['BD'] = []
			for index in range(network[node]['BT']):
				network[node]['BD'].append(False)

		self.__hNetwork = network
		self.__hTime = 0
		self.__hLimit = 0.5

	#Limited to linear chains only (Mehraghdam notation)
	def __hExecute (self, request):

		self.__hMetrics = {}
		for metric in request["METRICS"]:
			self.__hMetrics[metric] = request["METRICS"][metric]["SPEC"]
		self.__hHELM = HELM.HELM(self.__hMetrics)

		backup = copy.deepcopy(self.__hNetwork)
		topology = request['TOPOLOGY'].replace(' ', '').split('-')
		tLast = self.__hTime
		mapping = []

		for index in range(len(topology)):
			candidates = {}

			for node in self.__hNetwork:
				slot = self.__hSlot(tLast, request['ELEMENTS'][topology[index]]['BT'], node)
				if slot[0] == -1:
					continue
				tElapsed = request['ELEMENTS'][topology[index]]['BT'] + max(slot[0], tLast)
				tLimit = tLast + request['ELEMENTS'][topology[index]]['BT'] + request['ELEMENTS'][topology[index]]['BT'] * self.__hLimit
				if (tElapsed > tLimit):
					continue
				candidates[node] = slot

			if len(candidates) == 0:
				self.__hNetwork = backup
				return False

			key = self.__hEvaluate(request, topology[index], candidates)
			chosen = (key, candidates[key])

			for jndex in range(chosen[1][1], chosen[1][1] + request['ELEMENTS'][topology[index]]['BT']):
				self.__hNetwork[chosen[0]]['BD'][jndex % self.__hNetwork[chosen[0]]['BT']] = True
			tLast = chosen[1][1] + request['ELEMENTS'][topology[index]]['BT']
			self.__hNetwork[chosen[0]]['BF'] -= request['ELEMENTS'][topology[index]]['BT']

			mapping.append((topology[index], chosen[0]))

		return mapping

	######## PUBLIC METHODS ########

	def hProcess(self, request):

		if self.__status < 0:
			return self.__status

		self.__hSuggestion = self.__hExecute(request)
		self.__status = 1

	def hStatus(self):

		return self.__status

	def hSuggestion(self):

		if self.__status != 1:
			return None

		return self.__hSuggestion

######### HEURISTIC CLASS END #########
