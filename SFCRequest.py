######## SFC REQUEST CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service) 
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A YAML REQUEST FILE WITH THE SFC 
#DESCRIPTION AND THE REQUESTED OPERATIONS
#FOR THE NFV RESOURCE ALLOCATION EXECUTION.

#THE STATUS CLASS ATTRIBUTE INDICATE ITS 
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: NO REQUEST VALIDATED
#1: VALID REQUEST

#ERROR CODES ->
#-1  -> REQUEST METADA WAS SNOT INFORMED
#-2  -> REQUEST TOPOLOGY WAS NOT INFORMED
#-3  -> REQUEST GOAL FUNCTION WAS NOT INFORMED
#-4  -> INVALID ID (METADATA)
#-5  -> INVALID TOPOLOGY (TOPOLOGY)
#-6  -> INVALID OPERATIONAL ELEMENTS (TOPOLOGY)
#-7  -> INVALID END POINTS (TOPOLOGY)
#-8  -> INVALID TOPOLOGY ELEMENTS (TOPOLOGY)
#-9  -> INVALID GOAL (GOAL FUNCTION)
#-10 -> INVALID METRIC (GOAL FUNCTION)
#-11 -> INVALID METRIC EVALUATION (GOAL FUNCTION)
#-12 -> METRIC NOT INFORMED IN SOME OPERATIONAL ELEMENT (GOAL FUNCTIO/TOPOLOGY)
#-13 -> SOME BRANCH METRIC IS NOT PRESENT (TOPOLOGY)
#-14 -> INVALID BRANCH ELEMENTS (TOPOLOGY)
#-15 -> INVALID BRANCH UPDATE OPERATION (TOPOLOGY)
#-16 -> SOME BRANCH IS NOT INFORMED (TOPOLOGY)
#-17 -> SOME BRANCH IS NOT WELL FORMED (TOPOLOGY)
#-18 -> NO BRANCH IN TOPOLOGY, BUT SOME BRANCH INFORMED IN REQUEST (TOPOLOGY)

###############################################

######## SFC REQUEST CLASS BEGIN ########

import os
import yaml
import re

class SFCRequest:

	__status = None

	__metadata = None
	__topology = None
	__objFunctions = None

	__domainsList = None

	######## CONSTRUCTOR ########

	def __init__(self):

		self.__status = 0

	def __init__(self, requestFile, domainsList):

		self.srRequest(requestFile, domainsList)

	######## PRIVATE METHODS ########

	def __srBranch(self, elementsList, start):

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


	def __srValidate(self):

		if self.__metadata == None:
			self.__status = -1
			return
		if self.__topology == None:
			self.__status = -2
			return
		if self.__objFunctions == None:
			self.__status = -3
			return

		if len(self.__metadata["ID"]) == 0:
			self.__status = -4
			return

		if len(self.__topology["TOPOLOGY"]) == 0:
			self.__status = -5
			return
		if len(self.__topology["OPELEMENTS"]) == 0:
			self.__status = -6
			return
		if len(self.__topology["EPS"]) == 0:
			self.__status = -7
			return

		topoSymbols = ['<', '>', '{', '}', '(', ')', '[', ']', '/', '*', 'IP']
		topoOElemenets = [element["ID"] for element in self.__topology["OPELEMENTS"]]
		topoEPoints = [point["ID"] for point in self.__topology["EPS"]]
		splittedTopo = self.__topology["TOPOLOGY"].split()

		branchSegments = []
		for index in range(len(splittedTopo)):
			if splittedTopo[index] == '{':
				branchSegments.append(self.__srBranch(splittedTopo, index))
			if splittedTopo[index] in topoSymbols:
				continue
			if splittedTopo[index] in topoOElemenets:
				continue
			if splittedTopo[index] in topoEPoints:
				continue
			if splittedTopo[index] in self.__domainsList:
				continue
			self.__status = -8
			return

		functionMetrics = []
		for metric in self.__objFunctions["FUNCTION"]:
			if metric["GOAL"] != "MIN" and metric["GOAL"] != "MAX":
				self.__status = -9
				return
			if not "METRIC" in metric or not "WEIGHT" in metric or not "INPUT" in metric or not "EVALUATION" in metric:
				self.__status = -10
				return
			if metric["EVALUATION"] != "MULT" and metric["EVALUATION"] != "DIV" and metric["EVALUATION"] != "SUB" and metric["EVALUATION"] != "SUM":
				self.__status = -11
				return 
			functionMetrics.append(metric["METRIC"])

		for element in self.__topology["OPELEMENTS"]:
			for metric in functionMetrics:
				if not metric in element:
					self.__status = -12
					return

		if '{' in splittedTopo:
	
			for metric in functionMetrics:
				if not metric in self.__topology["BRANCHINGS"]:
					self.__status = -13
					return

				if not "UPDATE" in self.__topology["BRANCHINGS"][metric] or not "FACTORS" in self.__topology["BRANCHINGS"][metric]:
					self.__status = -14
					return

				updateOperation = self.__topology["BRANCHINGS"][metric]["UPDATE"]
				if updateOperation != "MULT" and updateOperation != "DIV" and updateOperation != "SUB" and updateOperation != "SUM":
					self.__status = -15
					return

				if splittedTopo.count('{') != len(self.__topology["BRANCHINGS"][metric]["FACTORS"]):
					self.__status = -16
					return

				for index in range(len(self.__topology["BRANCHINGS"][metric]["FACTORS"])):
					if len(self.__topology["BRANCHINGS"][metric]["FACTORS"][index]) != branchSegments[index]:
						self.__status = -17
						return

		else:

			if len(self.__topology["BRANCHINGS"]) != 0:
				self.__status = -18
				return 

		self.__status = 1

	######## PUBLIC METHODS ########

	def srRequest(self, requestFile, domainsList):

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
			yamlParsed = yaml.load(fileData)
		except:
			return
		
		if "ID" in yamlParsed and "DESCRIPTION" in yamlParsed:
			self.__metadata = {"ID":yamlParsed["ID"], "DESCRIPTION":yamlParsed["DESCRIPTION"]}
		if "TOPOLOGY" in yamlParsed and "BRANCHINGS" in yamlParsed and "OPELEMENTS" in yamlParsed and "EPS" in yamlParsed:
			self.__topology = {"TOPOLOGY":yamlParsed["TOPOLOGY"], "BRANCHINGS":yamlParsed["BRANCHINGS"], "OPELEMENTS":yamlParsed["OPELEMENTS"], "EPS":yamlParsed["EPS"]}
		if "FUNCTION" in yamlParsed:
			self.__objFunctions = {"FUNCTION":yamlParsed["FUNCTION"]}
		self.__srValidate()

	def srStatus(self):

		return self.__status

	def srDomains(self):

		if self.__status != 1:
			return None

		return self.__domainsList

	def srEPs(self):
		
		if self.__status != 1:
			return None

		listEPs = []
		for EP in self.__topology["EPS"]:
			listEPs.append(EP["ID"])

		return listEPs

	def srOPEs(self):

		if self.__status != 1:
			return None
		
		listOPEs = []
		for OPEs in self.__topology["OPELEMENTS"]:
			listOPEs.append(OPEs["ID"])

		return listOPEs

	def srFullOPEs(self):

		if self.__status != 1:
			return None
		
		return self.__topology["OPELEMENTS"]

	def srTopology(self):

		if self.__status != 1:
			return None

		return self.__topology["TOPOLOGY"]

	def srGoal(self):

		if self.__status != 1:
			return None

		goals = {}
		for function in self.__objFunctions["FUNCTION"]:
			goals[function["METRIC"]] = function["GOAL"]

		return goals

	def srFunction(self):

		if self.__status != 1:
			return None

		return self.__objFunctions["FUNCTION"]

	def srWeights(self):

		if self.__status != 1:
			return None

		weights = {}
		for function in self.__objFunctions["FUNCTION"]:
			weights[function["METRIC"]] = function["WEIGHT"]

		return weights

	def srBranches(self):

		if self.__status != 1:
			return None

		return self.__topology["BRANCHINGS"]
		
######## SFC REQUEST CLASS END ########