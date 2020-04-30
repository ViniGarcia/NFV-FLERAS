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
		for element in self.__service["FUNCTIONS"]:
			if not isinstance(element, str):
				self.__status = -17
				return False
		for outnode in self.__service["EGRESSNODES"]:
			if not isinstance(outnode, str):
				self.__status = -17
				return False

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
			if policy["MIN"] > policy["MAX"]:
				self.__status = -19
				return False
		for policy in self.__policies["AGGREGATE"]:
			if not isinstance(policy["WEIGHT"], int) and not isinstance(policy["WEIGHT"], float):
				self.__status = -18
				return False
			if policy["WEIGHT"] <= 0 or policy["WEIGHT"] > 1:
				self.__status = -20
				return False
			aggWeights += policy["WEIGHT"]

		if aggWeights != 1:
			self.__status = -21
			return False

		for data in list(set(self.__deployment.keys()) - {"BRANCHINGS"}):
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
		if len(self.__service["FUNCTIONS"]) == 0:
			self.__status = -7
			return
		if len(self.__service["EGRESSNODES"]) == 0:
			self.__status = -8
			return

		topoSymbols = ['<', '>', '{', '}', '/', 'IN']
		topoOElemenets = self.__service["FUNCTIONS"]
		topoEPoints = self.__service["EGRESSNODES"]
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

		for element in self.__service["FUNCTIONS"]:
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
				if not "ID" in policy or not "MIN" in policy or not "MAX" in policy or not "TYPE" in policy:
					self.__status = -13
					return
				if policy["TYPE"] != "TRANSITION" and policy["TYPE"] != "DOMAIN":
					self.__status = -14
					return
			for policy in self.__policies["AGGREGATE"]:
				if not "OBJECTIVE" in policy or not "WEIGHT" in policy:
					self.__status = -13
					return
				if policy["OBJECTIVE"] != "MIN" and policy["OBJECTIVE"] != "MAX":
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
			if "TOPOLOGY" in yamlParsed["SERVICE"]  and "FUNCTIONS" in yamlParsed["SERVICE"] and "EGRESSNODES" in yamlParsed["SERVICE"]:
				self.__service = yamlParsed["SERVICE"]

		if "EMB_OBJECTIVE_FUNCTION" in yamlParsed:
			if "IMMEDIATE" in yamlParsed["EMB_OBJECTIVE_FUNCTION"] and "AGGREGATE" in yamlParsed["EMB_OBJECTIVE_FUNCTION"]:
				self.__policies = yamlParsed["EMB_OBJECTIVE_FUNCTION"]

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

	def yePolicies(self):

		if self.__status != 1:
			return None

		return self.__policies

	def yeServiceEN(self):

		if self.__status != 1:
			return None

		return self.__service["EGRESSNODES"]

	def yeServiceNF(self):

		if self.__status != 1:
			return None

		return self.__service["FUNCTIONS"]

	def yeServiceBechmark(self):

		if self.__status != 1:
			return None

		serviceBecnhmark = []
		for metric in list(set(self.__deployment.keys()) - {"BRANCHINGS"}):
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

	def yePoliciesMetrics(self):

		if self.__status != 1:
			return None

		metrics = {"DOMAIN":[], "TRANSITION":[]}
		for policy in self.__policies["IMMEDIATE"] + self.__policies["AGGREGATE"]:
			if not policy["ID"] in metrics[policy["TYPE"]]:
				metrics[policy["TYPE"]].append(policy["ID"])

		return metrics

######## YAMLR EMBEDDING CLASS END ########