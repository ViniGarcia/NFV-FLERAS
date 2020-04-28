######## YAMLR EMBEDDING CLASS DESCRIPTION ########

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
#-3   -> REQUEST POLICIES WAS NOT INFORMED
#-4	  -> REQUEST DEPLOYMENT DATA WAS NOT INFORMED
#-5   -> INVALID ID (METADATA)
#-6   -> INVALID TOPOLOGY (TOPOLOGY)
#-7   -> INVALID OPERATIONAL ELEMENTS (TOPOLOGY)
#-8   -> INVALID END POINTS (TOPOLOGY)
#-9  -> INVALID TOPOLOGY ELEMENTS (TOPOLOGY)
#-10  -> MISSING ELEMENT ON DEPLOYMENT DATA (DPELOYMENT)
#-11  -> INVALID DEPLOYMENT DATA OBJECT (DEPLOYMENT)
#-12  -> INVALID DEPLOYMENT FLAVOUR OBJECT (DEPLOYMENT)
#-13  -> INVALID POLICY (POLICIES)
#-14  -> INVALID POLICY TYPE (POLICIES)
#-15  -> INVALID POLICY GOAL (POLICIES)
#-16  -> INVALID DATA TYPE IN METADATA BLOCK
#-17  -> INVALID DATA TYPE IN SERVICE BLOCK
#-18  -> INVALID DATA TYPE IN POLICIES BLOCK
#-19  -> A POLICY HAS MINIMUM VALIUE GREATER THAN MAXIMUM VALUE
#-20  -> INVALID POLICY WEIGHT
#-21  -> INVALID IMMEDIATE POLICIES WEIGHT SUMMARY
#-22  -> INVALID DATA TYPE IN DEPLOYMENT BLOCK

###############################################

######## YAMLR EMBEDDING CLASS BEGIN ########

import os
import yaml
import re

class YAMLREmbedding:

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
			self.yeRequest(requestFile, domainsList)

	######## PRIVATE METHODS ########

	def __yeBranch(self, elementsList, start):

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

	def __yeData(self):

		if not isinstance(self.__metadata["ID"], str):
			self.__status = -16
			return False

		if not isinstance(self.__service["TOPOLOGY"], str):
			self.__status = -17
			return False
		for element in self.__service["OELEMENTS"]:
			if not isinstance(element, str):
				self.__status = -17
				return False
		for outnode in self.__service["OUTNODES"]:
			if not isinstance(outnode, str):
				self.__status = -17
				return False

		immWeights = 0
		aggWeights = 0
		for policy in self.__policies["IMMEDIATE"] + self.__policies["AGGREGATE"]:
			if not isinstance(policy["ID"], str):
				self.__status = -18
				return False
			if not isinstance(policy["MIN"], int) and not isinstance(policy["MIN"], float):
				self.__status = -18
				return False
			if not isinstance(policy["MAX"], int) and not isinstance(policy["MAX"], float):
				self.__status = -18
				return False
			if not isinstance(policy["WEIGHT"], int) and not isinstance(policy["WEIGHT"], float):
				self.__status = -18
				return False
			if policy["MIN"] > policy["MAX"]:
				self.__status = -19
				return False
			if policy["WEIGHT"] <= 0 or policy["WEIGHT"] > 1:
				self.__status = -20
				return False
			if policy in self.__policies["IMMEDIATE"]:
				immWeights += policy["WEIGHT"]
			else:
				aggWeights += policy["WEIGHT"]
		if immWeights + aggWeights != 1:
			self.__status = -21
			return False

		for data in self.__deployment:
			if not isinstance(self.__deployment[data]["FLAVOUR"]["MEMORY"], int):
				self.__status = -22
				return False
			if not isinstance(self.__deployment[data]["FLAVOUR"]["NET_IFACES"], int):
				self.__status = -22
				return False
			if not isinstance(self.__deployment[data]["FLAVOUR"]["CPUS"], int):
				self.__status = -22
				return False

		return True

	def __yeValidate(self):

		if self.__metadata == None:
			self.__status = -1
			return
		if self.__service == None:
			self.__status = -2
			return
		if self.__policies == None:
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

		topoSymbols = ['<', '>', '{', '}', '/', 'IP']
		topoOElemenets = self.__service["OELEMENTS"]
		topoEPoints = self.__service["OUTNODES"]
		splittedTopo = self.__service["TOPOLOGY"].split()

		branchSegments = []
		for index in range(len(splittedTopo)):
			if splittedTopo[index] == '{':
				branchSegments.append(self.__yeBranch(splittedTopo, index))
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

		for element in self.__service["OELEMENTS"]:
			if not element in self.__deployment:
				self.__status = -10
				return
			if not "FLAVOUR" in self.__deployment[element]:
				self.__status = -11
				return
			if not "MEMORY" in self.__deployment[element]["FLAVOUR"] or not "NET_IFACES" in self.__deployment[element]["FLAVOUR"] or not "CPUS" in self.__deployment[element]["FLAVOUR"]:
				self.__status = -12
				return

		if self.__policies != None:

			for policy in self.__policies["IMMEDIATE"] + self.__policies["AGGREGATE"]:
				if not "ID" in policy or not "MIN" in policy or not "MAX" in policy or not "TYPE" in policy or not "GOAL" in policy or not "WEIGHT" in policy:
					self.__status = -13
					return
				if policy["TYPE"] != "TRANSITION" and policy["TYPE"] != "DOMAIN":
					self.__status = -14
					return
				if policy["GOAL"] != "MIN" and policy["GOAL"] != "MAX":
					self.__status = -15
					return

		if self.__yeData():
			self.__status = 1

	######## PUBLIC METHODS ########

	def yeRequest(self, requestFile, domainsList):

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

		if "POLICIES" in yamlParsed:
			if "IMMEDIATE" in yamlParsed["POLICIES"] and "AGGREGATE" in yamlParsed["POLICIES"]:
				self.__policies = yamlParsed["POLICIES"]

		if "DEPLOYMENT" in yamlParsed:
			self.__deployment = yamlParsed["DEPLOYMENT"]

		self.__yeValidate()

	def yeStatus(self):

		return self.__status

	def yeDomains(self):

		if self.__status != 1:
			return None

		return self.__domainsList

	def yeMetadata(self):

		if self.__status != 1:
			return None

		return self.__metadata

	def yeService(self):

		if self.__status != 1:
			return None

		return self.__service

	def yeFunction(self):

		if self.__status != 1:
			return None

		return self.__function

	def yePolicies(self):

		if self.__status != 1:
			return None

		return self.__policies

	def yeServiceON(self):

		if self.__status != 1:
			return None

		return self.__service["OUTNODES"]

	def yeServiceOE(self):

		if self.__status != 1:
			return None

		return self.__service["OELEMENTS"]

	def yeServiceBechmark(self):

		if self.__status != 1:
			return None

		serviceBecnhmark = []
		for metric in self.__deployment:
			metricBenchmark = self.__deployment[metric]["BENCHMARK"].copy()
			metricBenchmark["ID"] = metric
			serviceBecnhmark.append(metricBenchmark)

		return serviceBecnhmark

	def yeServiceFlavours(self):

		if self.__status != 1:
			return None

		serviceFlavous = {}
		for symbol in self.__deployment:
			serviceFlavous[symbol] = self.__deployment[symbol]["FLAVOUR"]

		return serviceFlavous

	def yeServiceTopology(self):

		if self.__status != 1:
			return None

		return self.__service["TOPOLOGY"]

	def yeFunctionBranches(self):

		if self.__status != 1:
			return None

		return self.__function["BRANCHINGS"]

	def yeFunctionGoals(self):

		if self.__status != 1:
			return None

		goals = {}
		for metric in self.__function["METRICS"]:
			goals[metric["ID"]] = metric["GOAL"]

		return goals

	def yeFunctionWeights(self):

		if self.__status != 1:
			return None

		weights = {}
		for metric in self.__function["METRICS"]:
			weights[metric["ID"]] = metric["WEIGHT"]

		return weights

	def yePoliciesMetrics(self):

		if self.__status != 1:
			return None

		metrics = {"DOMAIN":[], "TRANSITION":[]}
		for policy in self.__policies["IMMEDIATE"] + self.__policies["AGGREGATE"]:
			if not policy["ID"] in metrics[policy["TYPE"]]:
				metrics[policy["TYPE"]].append(policy["ID"])

		return metrics

######## YAMLR EMBEDDING CLASS END ########
