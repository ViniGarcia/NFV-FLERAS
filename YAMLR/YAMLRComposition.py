######## YAMLR COMPOSITION CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service)
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A YAML REQUEST FILE WITH THE SFC
#DESCRIPTION AND THE REQUESTED OPERATIONS
#FOR THE NFV COMPOSING EXECUTION.

#THE STATUS CLASS ATTRIBUTE INDICATE ITS
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: NO REQUEST VALIDATED
#1: VALID REQUEST

#ERROR CODES ->
#-1   -> REQUEST METADATA WAS NOT INFORMED
#-2   -> REQUEST SERVICE WAS NOT INFORMED
#-3   -> REQUEST GOAL FUNCTION WAS NOT INFORMED
#-4	  -> REQUEST DEPLOYMENT DATA WAS NOT INFORMED
#-5   -> INVALID ID (METADATA)
#-6   -> INVALID TOPOLOGY (TOPOLOGY)
#-7   -> INVALID OPERATIONAL ELEMENTS (TOPOLOGY)
#-8   -> INVALID END POINTS (TOPOLOGY)
#-9   -> INVALID TOPOLOGY ELEMENTS (TOPOLOGY)
#-10  -> INVALID GOAL (GOAL FUNCTION)
#-11  -> INVALID METRIC (GOAL FUNCTION)
#-12  -> INVALID METRIC EVALUATION (GOAL FUNCTION)
#-13  -> MISSING ELEMENT ON DEPLOYMENT DATA (DPELOYMENT)
#-14  -> INVALID DEPLOYMENT DATA OBJECT (DEPLOYMENT)
#-15  -> SOME METRIC WAS NOT INFORMED FOR A DPELOYMENT ELEMENT (DEPLOYMENT)
#-16  -> SOME BRANCH METRIC IS NOT PRESENT (TOPOLOGY/GOAL FUNCTION)
#-17  -> INVALID BRANCH ELEMENTS (TOPOLOGY/GOAL FUNCTION)
#-18  -> INVALID BRANCH UPDATE OPERATION (TOPOLOGY/GOAL FUNCTION)
#-19  -> SOME BRANCH IS NOT INFORMED (TOPOLOGY/GOAL FUNCTION)
#-20  -> SOME BRANCH IS NOT WELL FORMED (TOPOLOGY/GOAL FUNCTION)
#-21  -> NO BRANCH IN TOPOLOGY, BUT SOME BRANCH INFORMED IN REQUEST (TOPOLOGY/GOAL FUNCTION)
#-22  -> INVALID DATA TYPE IN METADATA BLOCK
#-23  -> INVALID DATA TYPE IN SERVICE BLOCK
#-24  -> INVALID DATA TYPE IN GOAL FUNCTION BLOCK
#-25  -> INVALID METRIC WEIGHT IN FUNCTION BLOCK
#-26  -> INVALID METRICS WEIGHT SUMMARY
#-27  -> INVALID DATA TYPE IN DEPLOYMENT BLOCK

###############################################

######## YALMR COMPOSITION CLASS BEGIN ########

import os
import yaml
import re

class YAMLRComposition:

	__status = None

	__metadata = None
	__service = None
	__function = None
	__deployment = None

	__domainsList = None

	######## CONSTRUCTOR ########

	def __init__(self, requestFile, domainsList):

		self.__status = 0
		if requestFile != None and domainsList != None:
			self.ycRequest(requestFile, domainsList)

	######## PRIVATE METHODS ########

	def __ycBranch(self, elementsList, start):

		skipBrace = 0
		segments = 0
		for index in range(start+1, len(elementsList)):

			if elementsList[index] == "}":
				if skipBrace == 0:
					return segments + 1
				else:
					skipBrace -= 1
				continue

			if elementsList[index] == "{":
				skipBrace += 1
				continue

			if elementsList[index] == "/":
				if skipBrace == 0:
					segments += 1

	def __ycData(self):

		if not isinstance(self.__metadata["ID"], str):
			self.__status = -22
			return False

		if not isinstance(self.__service["TOPOLOGY"], str):
			self.__status = -23
			return False
		for element in self.__service["OELEMENTS"]:
			if not isinstance(element, str):
				self.__status = -23
				return False
		for outnode in self.__service["OUTNODES"]:
			if not isinstance(outnode, str):
				self.__status = -23
				return False

		funcWeights = 0
		for metric in self.__function["METRICS"]:
			if not isinstance(metric["ID"], str):
				self.__status = -24
				return False
			if not isinstance(metric["WEIGHT"], int) and not isinstance(metric["WEIGHT"], float):
				self.__status = -24
				return False
			if not isinstance(metric["INPUT"], int) and not isinstance(metric["INPUT"], float):
				self.__status = -24
				return False
			if metric["WEIGHT"] < 0 or metric["WEIGHT"] > 1:
				self.__status = -25
				return False
			funcWeights += metric["WEIGHT"]
		if funcWeights != 1:
			self.__status = -26
			return False

		for data in self.__deployment:
			for metric in self.__deployment[data]["BENCHMARK"]:
				if not isinstance(self.__deployment[data]["BENCHMARK"][metric], int) and not isinstance(self.__deployment[data]["BENCHMARK"][metric], float):
					self.__status = -27
					return False

		return True

	def __ycValidate(self):

		if self.__metadata == None:
			self.__status = -1
			return
		if self.__service == None:
			self.__status = -2
			return
		if self.__function == None:
			self.__status = -3
			return
		if self.__deployment == None:
			self.__status = -4
			return

		if len(self.__metadata["ID"]) == 0:
			self.__status = -5
			return
		if len(self.__service["TOPOLOGY"]) == 0:
			self.__status = -6
			return
		if len(self.__service["OELEMENTS"]) == 0:
			self.__status = -7
			return
		if len(self.__service["OUTNODES"]) == 0:
			self.__status = -8
			return

		topoSymbols = ['<', '>', '{', '}', '(', ')', '[', ']', '/', '*', 'IN']
		topoOElemenets = self.__service["OELEMENTS"]
		topoEPoints = self.__service["OUTNODES"]
		splittedTopo = self.__service["TOPOLOGY"].split()

		branchSegments = []
		for index in range(len(splittedTopo)):
			if splittedTopo[index] == '{':
				branchSegments.append(self.__ycBranch(splittedTopo, index))
			if splittedTopo[index] in topoSymbols:
				continue
			if splittedTopo[index] in topoOElemenets:
				continue
			if splittedTopo[index] in topoEPoints:
				continue
			if splittedTopo[index] in self.__domainsList:
				continue
			self.__status = -9
			return

		functionMetrics = []
		for metric in self.__function["METRICS"]:
			if metric["GOAL"] != "MIN" and metric["GOAL"] != "MAX":
				self.__status = -10
				return
			if not "ID" in metric or not "WEIGHT" in metric or not "INPUT" in metric or not "EVALUATION" in metric or not "UPDATE" in metric:
				self.__status = -11
				return
			if metric["EVALUATION"] != "MULT" and metric["EVALUATION"] != "DIV" and metric["EVALUATION"] != "SUB" and metric["EVALUATION"] != "SUM":
				self.__status = -12
				return
			functionMetrics.append(metric["ID"])

		for element in self.__service["OELEMENTS"]:
			if not element in self.__deployment:
				self.__status = -13
				return
			if not "BENCHMARK" in self.__deployment[element]:
				self.__status = -14
				return
			for metric in functionMetrics:
				if not metric in self.__deployment[element]["BENCHMARK"]:
					self.__status = -15
					return

		if '{' in splittedTopo:

			for metric in functionMetrics:
				if not metric in self.__function["BRANCHINGS"]:
					self.__status = -16
					return

				if not "UPDATE" in self.__function["BRANCHINGS"][metric] or not "FACTORS" in self.__function["BRANCHINGS"][metric]:
					self.__status = -17
					return

				updateOperation = self.__function["BRANCHINGS"][metric]["UPDATE"]
				if updateOperation != "MULT" and updateOperation != "DIV" and updateOperation != "SUB" and updateOperation != "SUM":
					self.__status = -18
					return

				if splittedTopo.count('{') != len(self.__function["BRANCHINGS"][metric]["FACTORS"]):
					self.__status = -19
					return

				for index in range(len(self.__function["BRANCHINGS"][metric]["FACTORS"])):
					if len(self.__function["BRANCHINGS"][metric]["FACTORS"][index]) != branchSegments[index]:
						self.__status = -20
						return

		else:

			if len(self.__function["BRANCHINGS"]) != 0:
				self.__status = -21
				return

		if self.__ycData():
			self.__status = 1

	######## PUBLIC METHODS ########

	def ycRequest(self, requestFile, domainsList):

		if not isinstance(domainsList, list):
			return
		if not all(isinstance(domain, str) for domain in domainsList):
			return
		self.__domainsList = domainsList

		if not os.path.isfile(requestFile):
			return
		openedFile = open(requestFile, "r")
		fileData = openedFile.read()
		openedFile.close()

		try:
			yamlParsed = yaml.safe_load(fileData)
		except:
			return

		if "METADATA" in yamlParsed:
			if "ID" in yamlParsed["METADATA"] and "DESCRIPTION" in yamlParsed["METADATA"]:
				self.__metadata = yamlParsed["METADATA"]

		if "SERVICE" in yamlParsed:
			if "TOPOLOGY" in yamlParsed["SERVICE"]  and "OELEMENTS" in yamlParsed["SERVICE"] and "OUTNODES" in yamlParsed["SERVICE"]:
				self.__service = yamlParsed["SERVICE"]

		if "GOAL_FUNCTION" in yamlParsed:
			if "METRICS" in yamlParsed["GOAL_FUNCTION"] and "BRANCHINGS" in yamlParsed["GOAL_FUNCTION"]:
				self.__function = yamlParsed["GOAL_FUNCTION"]

		if "DEPLOYMENT" in yamlParsed:
			self.__deployment = yamlParsed["DEPLOYMENT"]

		self.__ycValidate()

	def ycStatus(self):

		return self.__status

	def ycDomains(self):

		if self.__status != 1:
			return None

		return self.__domainsList

	def ycMetadata(self):

		if self.__status != 1:
			return None

		return self.__metadata

	def ycService(self):

		if self.__status != 1:
			return None

		return self.__service

	def ycFunction(self):

		if self.__status != 1:
			return None

		return self.__function

	def ycServiceON(self):

		if self.__status != 1:
			return None

		return self.__service["OUTNODES"]

	def ycServiceOE(self):

		if self.__status != 1:
			return None

		return self.__service["OELEMENTS"]

	def ycServiceBechmark(self):

		if self.__status != 1:
			return None

		serviceBecnhmark = []
		for metric in self.__deployment:
			metricBenchmark = self.__deployment[metric]["BENCHMARK"].copy()
			metricBenchmark["ID"] = metric
			serviceBecnhmark.append(metricBenchmark)

		return serviceBecnhmark

	def ycServiceTopology(self):

		if self.__status != 1:
			return None

		return self.__service["TOPOLOGY"]

	def ycFunctionBranches(self):

		if self.__status != 1:
			return None

		return self.__function["BRANCHINGS"]

	def ycFunctionGoals(self):

		if self.__status != 1:
			return None

		goals = {}
		for metric in self.__function["METRICS"]:
			goals[metric["ID"]] = metric["GOAL"]

		return goals

	def ycFunctionWeights(self):

		if self.__status != 1:
			return None

		weights = {}
		for metric in self.__function["METRICS"]:
			weights[metric["ID"]] = metric["WEIGHT"]

		return weights

######## YALMR COMPOSITION CLASS END ########
