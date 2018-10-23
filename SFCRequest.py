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
#-1   -> REQUEST METADATA WAS NOT INFORMED
#-2   -> REQUEST SERVICE WAS NOT INFORMED
#-3   -> REQUEST GOAL FUNCTION WAS NOT INFORMED
#-4   -> REQUEST POLICIES WAS NOT INFORMED
#-5	  -> REQUEST DEPLOYMENT DATA WAS NOT INFORMED
#-6   -> INVALID ID (METADATA)
#-7   -> INVALID TOPOLOGY (TOPOLOGY)
#-8   -> INVALID OPERATIONAL ELEMENTS (TOPOLOGY)
#-9   -> INVALID END POINTS (TOPOLOGY)
#-10  -> INVALID TOPOLOGY ELEMENTS (TOPOLOGY)
#-11  -> INVALID GOAL (GOAL FUNCTION)
#-12  -> INVALID METRIC (GOAL FUNCTION)
#-13  -> INVALID METRIC EVALUATION (GOAL FUNCTION)
#-14  -> MISSING ELEMENT ON DEPLOYMENT DATA (DPELOYMENT)
#-15  -> INVALID DEPLOYMENT DATA OBJECT (DEPLOYMENT)
#-16  -> INVALID DEPLOYMENT FLAVOUR OBJECT (DEPLOYMENT)
#-17  -> SOME METRIC WAS NOT INFORMED FOR A DPELOYMENT ELEMENT (DEPLOYMENT)
#-18  -> SOME BRANCH METRIC IS NOT PRESENT (TOPOLOGY/GOAL FUNCTION)
#-19  -> INVALID BRANCH ELEMENTS (TOPOLOGY/GOAL FUNCTION)
#-20  -> INVALID BRANCH UPDATE OPERATION (TOPOLOGY/GOAL FUNCTION)
#-21  -> SOME BRANCH IS NOT INFORMED (TOPOLOGY/GOAL FUNCTION)
#-22  -> SOME BRANCH IS NOT WELL FORMED (TOPOLOGY/GOAL FUNCTION)
#-23  -> NO BRANCH IN TOPOLOGY, BUT SOME BRANCH INFORMED IN REQUEST (TOPOLOGY/GOAL FUNCTION)
#-24  -> INVALID POLICY (POLICIES)
#-25  -> INVALID POLICY TYPE (POLICIES)
#-26  -> INVALID POLICY GOAL (POLICIES)
#-27  -> INVALID DATA TYPE IN METADATA BLOCK
#-28  -> INVALID DATA TYPE IN SERVICE BLOCK 
#-29  -> INVALID DATA TYPE IN GOAL FUNCTION BLOCK 
#-30  -> INVALID METRIC WEIGHT IN FUNCTION BLOCK
#-31  -> INVALID METRICS WEIGHT SUMMARY
#-32  -> INVALID DATA TYPE IN POLICIES BLOCK
#-33  -> A POLICY HAS MINIMUM VALIUE GREATER THAN MAXIMUM VALUE
#-34  -> INVALID POLICY WEIGHT
#-35  -> INVALID IMMEDIATE POLICIES WEIGHT SUMMARY
#-36  -> INVALID AGGREGATE POLICIES WEIGHT SUMMARY
#-37  -> INVALID DATA TYPE IN DEPLOYMENT BLOCK

###############################################

######## SFC REQUEST CLASS BEGIN ########

import os
import yaml
import re

class SFCRequest:

	__status = None

	__metadata = None
	__service = None
	__function = None
	__policies = None
	__deployment = None

	__domainsList = None

	######## CONSTRUCTOR ########

	def __init__(self, requestFile, domainsList):

		self.__status = 0
		if requestFile != None and domainsList != None:
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

	def __srData(self):

		if not isinstance(self.__metadata["ID"], str):
			self.__status = -27
			return False

		if not isinstance(self.__service["TOPOLOGY"], str): 
			self.__status = -28
			return False
		for element in self.__service["OELEMENTS"]:
			if not isinstance(element, str):
				self.__status = -28
				return False
		for outnode in self.__service["OUTNODES"]:
			if not isinstance(outnode, str):
				self.__status = -28
				return False

		funcWeights = 0
		for metric in self.__function["METRICS"]:
			if not isinstance(metric["ID"], str):
				self.__status = -29
				return False
			if not isinstance(metric["WEIGHT"], int) and not isinstance(metric["WEIGHT"], float):
				self.__status = -29
				return False
			if not isinstance(metric["INPUT"], int) and not isinstance(metric["INPUT"], float):
				self.__status = -29
				return False
			if metric["WEIGHT"] < 0 or metric["WEIGHT"] > 1:
				self.__status = -30
				return False
			funcWeights += metric["WEIGHT"]
		if funcWeights != 1:
			self.__status = -31
			return False

		immWeights = 0
		aggWeights = 0
		for policy in self.__policies["IMMEDIATE"] + self.__policies["AGGREGATE"]:
			if not isinstance(policy["ID"], str):
				self.__status = -32
				return False
			if not isinstance(policy["MIN"], int) and not isinstance(policy["MIN"], float):
				self.__status = -32
				return False
			if not isinstance(policy["MAX"], int) and not isinstance(policy["MAX"], float):
				self.__status = -32
				return False
			if not isinstance(policy["WEIGHT"], int) and not isinstance(policy["WEIGHT"], float):
				self.__status = -32
				return False
			if policy["MIN"] > policy["MAX"]:
				self.__status = -33
				return False
			if policy["WEIGHT"] <= 0 or policy["WEIGHT"] > 1:
				self.__status = -34
				return False
			if policy in self.__policies["IMMEDIATE"]:
				immWeights += policy["WEIGHT"]
			else:
				aggWeights += policy["WEIGHT"]
		if immWeights != 1:
			self.__status = -35
			return False
		if aggWeights != 1:
			self.__status = -36
			return False

		for data in self.__deployment:
			if not isinstance(self.__deployment[data]["FLAVOUR"]["MEMORY"], int):
				self.__status = -37
				return False
			if not isinstance(self.__deployment[data]["FLAVOUR"]["NET_IFACES"], int):
				self.__status = -37
				return False
			if not isinstance(self.__deployment[data]["FLAVOUR"]["CPUS"], int):
				self.__status = -37
				return False
			for metric in self.__deployment[data]["BENCHMARK"]:
				if not isinstance(self.__deployment[data]["BENCHMARK"][metric], int) and not isinstance(self.__deployment[data]["BENCHMARK"][metric], float):
					self.__status = -37
					return False

		return True

	def __srValidate(self):

		if self.__metadata == None:
			self.__status = -1
			return
		if self.__service == None:
			self.__status = -2
			return
		if self.__function == None:
			self.__status = -3
			return
		if self.__policies == None:
			self.__status = -4
			return
		if self.__deployment == None:
			self.__status = -5
			return

		if len(self.__metadata["ID"]) == 0:
			self.__status = -6
			return
		if len(self.__service["TOPOLOGY"]) == 0:
			self.__status = -7
			return
		if len(self.__service["OELEMENTS"]) == 0:
			self.__status = -8
			return
		if len(self.__service["OUTNODES"]) == 0:
			self.__status = -9
			return

		topoSymbols = ['<', '>', '{', '}', '(', ')', '[', ']', '/', '*', 'IP']
		topoOElemenets = self.__service["OELEMENTS"]
		topoEPoints = self.__service["OUTNODES"]
		splittedTopo = self.__service["TOPOLOGY"].split()

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
			self.__status = -10
			return

		functionMetrics = []
		for metric in self.__function["METRICS"]:
			if metric["GOAL"] != "MIN" and metric["GOAL"] != "MAX":
				self.__status = -11
				return
			if not "ID" in metric or not "WEIGHT" in metric or not "INPUT" in metric or not "EVALUATION" in metric or not "UPDATE" in metric:
				self.__status = -12
				return
			if metric["EVALUATION"] != "MULT" and metric["EVALUATION"] != "DIV" and metric["EVALUATION"] != "SUB" and metric["EVALUATION"] != "SUM":
				self.__status = -13
				return 
			functionMetrics.append(metric["ID"])

		for element in self.__service["OELEMENTS"]:
			if not element in self.__deployment:
				self.__status = -14
				return
			if not "FLAVOUR" in self.__deployment[element] or not "BENCHMARK" in self.__deployment[element]:
				self.__status = -15
				return
			if not "MEMORY" in self.__deployment[element]["FLAVOUR"] or not "NET_IFACES" in self.__deployment[element]["FLAVOUR"] or not "CPUS" in self.__deployment[element]["FLAVOUR"]:
				self.__status = -16
				return
			for metric in functionMetrics:
				if not metric in self.__deployment[element]["BENCHMARK"]:
					self.__status = -17
					return 

		if '{' in splittedTopo:
	
			for metric in functionMetrics:
				if not metric in self.__function["BRANCHINGS"]:
					self.__status = -18
					return

				if not "UPDATE" in self.__function["BRANCHINGS"][metric] or not "FACTORS" in self.__function["BRANCHINGS"][metric]:
					self.__status = -19
					return

				updateOperation = self.__function["BRANCHINGS"][metric]["UPDATE"]
				if updateOperation != "MULT" and updateOperation != "DIV" and updateOperation != "SUB" and updateOperation != "SUM":
					self.__status = -20
					return

				if splittedTopo.count('{') != len(self.__function["BRANCHINGS"][metric]["FACTORS"]):
					self.__status = -21
					return

				for index in range(len(self.__function["BRANCHINGS"][metric]["FACTORS"])):
					if len(self.__function["BRANCHINGS"][metric]["FACTORS"][index]) != branchSegments[index]:
						self.__status = -22
						return

		else:

			if len(self.__function["BRANCHINGS"]) != 0:
				self.__status = -23
				return

		if self.__policies != None:

			for policy in self.__policies["IMMEDIATE"] + self.__policies["AGGREGATE"]:
				if not "ID" in policy or not "MIN" in policy or not "MAX" in policy or not "TYPE" in policy or not "GOAL" in policy or not "WEIGHT" in policy:
					self.__status = -24
					return
				if policy["TYPE"] != "TRANSITION" and policy["TYPE"] != "DOMAIN":
					self.__status = -25
					return
				if policy["GOAL"] != "MIN" and policy["GOAL"] != "MAX":
					self.__status = -26
					return

		if self.__srData():
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
		
		if "METADATA" in yamlParsed:
			if "ID" in yamlParsed["METADATA"] and "DESCRIPTION" in yamlParsed["METADATA"]:
				self.__metadata = yamlParsed["METADATA"]

		if "SERVICE" in yamlParsed:
			if "TOPOLOGY" in yamlParsed["SERVICE"]  and "OELEMENTS" in yamlParsed["SERVICE"] and "OUTNODES" in yamlParsed["SERVICE"]:
				self.__service = yamlParsed["SERVICE"]

		if "GOAL_FUNCTION" in yamlParsed:
			if "METRICS" in yamlParsed["GOAL_FUNCTION"] and "BRANCHINGS" in yamlParsed["GOAL_FUNCTION"]:
				self.__function = yamlParsed["GOAL_FUNCTION"]

		if "POLICIES" in yamlParsed:
			if "IMMEDIATE" in yamlParsed["POLICIES"] and "AGGREGATE" in yamlParsed["POLICIES"]:
				self.__policies = yamlParsed["POLICIES"]

		if "DEPLOYMENT" in yamlParsed:
			self.__deployment = yamlParsed["DEPLOYMENT"]

		self.__srValidate()

	def srStatus(self):

		return self.__status

	def srDomains(self):

		if self.__status != 1:
			return None

		return self.__domainsList

	def srMetadata(self):

		if self.__status != 1:
			return None

		return self.__metadata

	def srService(self):

		if self.__status != 1:
			return None

		return self.__service

	def srFunction(self):

		if self.__status != 1:
			return None

		return self.__function

	def srServiceON(self):
		
		if self.__status != 1:
			return None

		return self.__service["OUTNODES"]

	def srServiceOE(self):

		if self.__status != 1:
			return None

		return self.__service["OELEMENTS"]

	def srServiceBechmark(self):

		if self.__status != 1:
			return None
		
		serviceBecnhmark = []
		for metric in self.__deployment:
			metricBenchmark = self.__deployment[metric]["BENCHMARK"].copy()
			metricBenchmark["ID"] = metric
			serviceBecnhmark.append(metricBenchmark)

		return serviceBecnhmark

	def srServiceTopology(self):

		if self.__status != 1:
			return None

		return self.__service["TOPOLOGY"]

	def srFunctionBranches(self):

		if self.__status != 1:
			return None

		return self.__function["BRANCHINGS"]

	def srFunctionGoals(self):

		if self.__status != 1:
			return None

		goals = {}
		for metric in self.__function["METRICS"]:
			goals[metric["ID"]] = metric["GOAL"]

		return goals

	def srFunctionWeights(self):

		if self.__status != 1:
			return None

		weights = {}
		for metric in self.__function["METRICS"]:
			weights[metric["ID"]] = metric["WEIGHT"]

		return weights

######## SFC REQUEST CLASS END ########