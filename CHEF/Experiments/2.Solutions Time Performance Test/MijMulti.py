############## IMPORTS ##############

import yaml
import copy
import os
import CHEF

######## HEURISTIC CLASS BEGIN ########

class Heuristic:
	__status = None

	__hNetwork = None
	__hTime = None
	__hLimit = None
	__hMetrics = None
	__hCHEF = None

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

		partialResults = self.__hCHEF.cEvaluate(partialResults)
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
		self.__hCHEF = CHEF.CHEF(self.__hMetrics)

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

######## PROCESSOR CLASS BEGIN ########

class Processor:
	__status = None

	__pHeuristic = None

	######## CONSTRUCTOR ########

	def __init__(self):

		self.__status = 0

	######## PRIVATE METHODS ########

	def __pValidate(self, document):

		file = open(document, "r")
		data = file.read()
		file.close()

		try:
			yamlData = yaml.load(data, Loader=yaml.FullLoader)
		except:
			self.__status = -2
			return -2

		if not "REQUEST" in yamlData or not "INFRA" in yamlData:
			self.__status = -3
			return -3

		if not isinstance(yamlData["REQUEST"], dict) or not isinstance(yamlData["INFRA"], dict):
			self.__status = -4
			return -4

		if not "TOPOLOGY" in yamlData["REQUEST"] or not "ELEMENTS" in yamlData["REQUEST"] or not "METRICS" in yamlData["REQUEST"]:
			self.__status = -5
			return -5

		if not isinstance(yamlData["REQUEST"]["TOPOLOGY"], str) or not isinstance(yamlData["REQUEST"]["ELEMENTS"], dict) or not isinstance(yamlData["REQUEST"]["METRICS"], dict):
			self.__status = -6
			return -6

		for i in yamlData["INFRA"]:
			if not isinstance(yamlData["INFRA"][i], dict):
				self.__status = -7
				return -7

			for j in yamlData["INFRA"][i]:
				if not isinstance(yamlData["INFRA"][i][j], int):
					if j == 'BT':
						self.__status = -8
						return -8
					else:
						if not isinstance(yamlData["INFRA"][i][j], float):
							self.__status = -8
							return -8

		for i in yamlData["REQUEST"]["ELEMENTS"]:
			if not isinstance(yamlData["REQUEST"]["ELEMENTS"][i], dict):
				self.__status = -9
				return -9

			for j in yamlData["REQUEST"]["ELEMENTS"][i]:
				if not isinstance(yamlData["REQUEST"]["ELEMENTS"][i][j], int):
					if j == 'BT':
						self.__status = -10
						return -10
					else:
						if not isinstance(yamlData["REQUEST"]["ELEMENTS"][i][j], float):
							self.__status = -10
							return -10

		for metric in yamlData["REQUEST"]["METRICS"]:
			if not isinstance(yamlData["REQUEST"]["METRICS"][metric], dict):
				self.__status = -12
				return -12
			if not "TYPE" in yamlData["REQUEST"]["METRICS"][metric] or not "SPEC" in yamlData["REQUEST"]["METRICS"][metric]:
				self.__status = -13
				return -13
			if not isinstance(yamlData["REQUEST"]["METRICS"][metric]["TYPE"], str) or not isinstance(yamlData["REQUEST"]["METRICS"][metric]["SPEC"], tuple):
				self.__status = -14
				return -14
			if yamlData["REQUEST"]["METRICS"][metric]["TYPE"] != "CATALOG" and yamlData["REQUEST"]["METRICS"][metric]["TYPE"] != "PERSONAL":
				self.__status = -15
				return -15
			if len(yamlData["REQUEST"]["METRICS"][metric]["SPEC"]) != 2:
				self.__status = -16
				return -16
			if not isinstance(yamlData["REQUEST"]["METRICS"][metric]["SPEC"][1], float) or not isinstance(yamlData["REQUEST"]["METRICS"][metric]["SPEC"][0], str):
				self.__status = -17
				return -17
			if yamlData["REQUEST"]["METRICS"][metric]["SPEC"][1] <= 0:
				self.__status = -18
				return -18
			if yamlData["REQUEST"]["METRICS"][metric]["SPEC"][0] != "MIN" and yamlData["REQUEST"]["METRICS"][metric]["SPEC"][0] != "MAX":
				self.__status = -19
				return -19
			if yamlData["REQUEST"]["METRICS"][metric]["TYPE"] == "PERSONAL":
				if not "DATA" in yamlData["REQUEST"]["METRICS"][metric]:
					self.__status = -20
					return -20
				if not isinstance(yamlData["REQUEST"]["METRICS"][metric]["DATA"], dict):
					self.__status = -21
					return -21
				if yamlData["REQUEST"]["METRICS"][metric]["DATA"].keys() != yamlData["INFRA"].keys():
					self.__status = -22
					return -22

		return yamlData

	######## PUBLIC METHODS ########

	def pProcess(self, document):

		if not os.path.isfile(document):
			self.__status = -1
			return -1

		data = self.__pValidate(document)
		if self.__status < 0:
			return self.__status

		self.__pHeuristic = Heuristic(data['INFRA'])
		self.__pHeuristic.hProcess(data['REQUEST'])

		self.__status = 1
		return 1

	def pSuggestion(self):

		if self.__status != 1:
			return None

		return self.__pHeuristic.hSuggestion()

######### PROCESSOR CLASS END #########

#mijumbi = Processor()
#mijumbi.pProcess("MijMulti.yaml")
#print(mijumbi.pSuggestion())
