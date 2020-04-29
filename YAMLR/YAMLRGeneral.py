######## YAMLR GENERAL CLASS DESCRIPTION ########

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
#-36  -> INVALID DATA TYPE IN DEPLOYMENT BLOCK

###############################################

######## YAMLR GENERAL CLASS BEGIN ########

import os
import yaml
import re

class YAMLRGeneral:

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
			self.ygRequest(requestFile, domainsList)

	######## PRIVATE METHODS ########

	def __ygBranch(self, elementsList, start):

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

	def __ygData(self):

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
			if policy["MIN"] > policy["MAX"]:
				self.__status = -33
				return False

		for policy in self.__policies["AGGREGATE"]:
			if not isinstance(policy["WEIGHT"], int) and not isinstance(policy["WEIGHT"], float):
				self.__status = -32
				return False
			if policy["WEIGHT"] <= 0 or policy["WEIGHT"] > 1:
				self.__status = -34
				return False
			aggWeights += policy["WEIGHT"]

		if aggWeights != 1:
			self.__status = -35
			return False

		for data in list(set(self.__deployment.keys()) - {"BRANCHINGS"}):
			if not isinstance(self.__deployment[data]["FLAVOUR"]["MEMORY"], int):
				self.__status = -36
				return False
			if not isinstance(self.__deployment[data]["FLAVOUR"]["NET_IFACES"], int):
				self.__status = -36
				return False
			if not isinstance(self.__deployment[data]["FLAVOUR"]["CPUS"], int):
				self.__status = -36
				return False
			for metric in self.__deployment[data]["BENCHMARK"]:
				if not isinstance(self.__deployment[data]["BENCHMARK"][metric], int) and not isinstance(self.__deployment[data]["BENCHMARK"][metric], float):
					self.__status = -36
					return False

		return True

	def __ygValidate(self):

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

		topoSymbols = ['<', '>', '{', '}', '(', ')', '[', ']', '/', '*', 'IN']
		topoOElemenets = self.__service["OELEMENTS"]
		topoEPoints = self.__service["OUTNODES"]
		splittedTopo = self.__service["TOPOLOGY"].split()

		branchSegments = []
		for index in range(len(splittedTopo)):
			if splittedTopo[index] == '{':
				branchSegments.append(self.__ygBranch(splittedTopo, index))
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
				if not metric in self.__deployment["BRANCHINGS"]:
					self.__status = -18
					return

				if not "UPDATE" in self.__deployment["BRANCHINGS"][metric] or not "FACTORS" in self.__deployment["BRANCHINGS"][metric]:
					self.__status = -19
					return

				updateOperation = self.__deployment["BRANCHINGS"][metric]["UPDATE"]
				if updateOperation != "MULT" and updateOperation != "DIV" and updateOperation != "SUB" and updateOperation != "SUM":
					self.__status = -20
					return

				if splittedTopo.count('{') != len(self.__deployment["BRANCHINGS"][metric]["FACTORS"]):
					self.__status = -21
					return

				for index in range(len(self.__deployment["BRANCHINGS"][metric]["FACTORS"])):
					if len(self.__deployment["BRANCHINGS"][metric]["FACTORS"][index]) != branchSegments[index]:
						self.__status = -22
						return

		else:

			if len(self.__deployment["BRANCHINGS"]) != 0:
				self.__status = -23
				return

		if self.__policies != None:

			for policy in self.__policies["AGGREGATE"] + self.__policies["IMMEDIATE"]:
				if not "ID" in policy or not "MIN" in policy or not "MAX" in policy or not "TYPE" in policy:
					self.__status = -24
					return
				if policy["TYPE"] != "TRANSITION" and policy["TYPE"] != "DOMAIN":
					self.__status = -25
					return
			for policy in self.__policies["AGGREGATE"]:
				if not "GOAL" in policy or not "WEIGHT" in policy:
					self.__status = -24
					return
				if policy["GOAL"] != "MIN" and policy["GOAL"] != "MAX":
					self.__status = -26
					return

		if self.__ygData():
			self.__status = 1

	######## PUBLIC METHODS ########

	def ygRequest(self, requestFile, domainsList):

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

		if "COMP_OBJECTIVE_FUNCTION" in yamlParsed:
			if "METRICS" in yamlParsed["COMP_OBJECTIVE_FUNCTION"]:
				self.__function = yamlParsed["COMP_OBJECTIVE_FUNCTION"]

		if "EMB_OBJECTIVE_FUNCTION" in yamlParsed:
			if "IMMEDIATE" in yamlParsed["EMB_OBJECTIVE_FUNCTION"] and "AGGREGATE" in yamlParsed["EMB_OBJECTIVE_FUNCTION"]:
				self.__policies = yamlParsed["EMB_OBJECTIVE_FUNCTION"]

		if "DEPLOYMENT" in yamlParsed:
			if "BRANCHINGS" in yamlParsed["DEPLOYMENT"]:
				self.__deployment = yamlParsed["DEPLOYMENT"]

		self.__ygValidate()

	def ygStatus(self):

		return self.__status

	def ygDomains(self):

		if self.__status != 1:
			return None

		return self.__domainsList

	def ygMetadata(self):

		if self.__status != 1:
			return None

		return self.__metadata

	def ygService(self):

		if self.__status != 1:
			return None

		return self.__service

	def ygFunction(self):

		if self.__status != 1:
			return None

		return self.__function

	def ygPolicies(self):

		if self.__status != 1:
			return None

		return self.__policies

	def ygServiceON(self):

		if self.__status != 1:
			return None

		return self.__service["OUTNODES"]

	def ygServiceOE(self):

		if self.__status != 1:
			return None

		return self.__service["OELEMENTS"]

	def ygServiceBechmark(self):

		if self.__status != 1:
			return None

		serviceBecnhmark = []
		for metric in list(set(self.__deployment.keys()) - {"BRANCHINGS"}):
			metricBenchmark = self.__deployment[metric]["BENCHMARK"].copy()
			metricBenchmark["ID"] = metric
			serviceBecnhmark.append(metricBenchmark)

		return serviceBecnhmark

	def ygServiceFlavours(self):

		if self.__status != 1:
			return None

		serviceFlavous = {}
		for symbol in self.__deployment:
			serviceFlavous[symbol] = self.__deployment[symbol]["FLAVOUR"]

		return serviceFlavous

	def ygServiceTopology(self):

		if self.__status != 1:
			return None

		return self.__service["TOPOLOGY"]

	def ygFunctionBranches(self):

		if self.__status != 1:
			return None

		return self.__deployment["BRANCHINGS"]

	def ygFunctionGoals(self):

		if self.__status != 1:
			return None

		goals = {}
		for metric in self.__function["METRICS"]:
			goals[metric["ID"]] = metric["GOAL"]

		return goals

	def ygFunctionWeights(self):

		if self.__status != 1:
			return None

		weights = {}
		for metric in self.__function["METRICS"]:
			weights[metric["ID"]] = metric["WEIGHT"]

		return weights

	def ygPoliciesMetrics(self):

		if self.__status != 1:
			return None

		metrics = {"DOMAIN":[], "TRANSITION":[]}
		for policy in self.__policies["IMMEDIATE"] + self.__policies["AGGREGATE"]:
			if not policy["ID"] in metrics[policy["TYPE"]]:
				metrics[policy["TYPE"]].append(policy["ID"])

		return metrics

######## YALMR GENERAL CLASS END ########