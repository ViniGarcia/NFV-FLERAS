######## DOMAINS DATA CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service)
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A YAML FILE WITH THE DOMAINS DATA
#AND AVAILABLE METRICS TO BE EVALUATED DURING
#SPLIT AND MAPPING PROCESSES.

#THE STATUS CLASS ATTRIBUTE INDICATE ITS
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: NO DATA VALIDATED
#1: VALID DATA

#ERROR CODES ->
#-1: FILE NAME/PATH IS INVALID
#-2: INCORRECT YAML SYNTAX
#-3: SOME OF MAIN KEYS IS NOT PRESENT IN THE YAML
#-4: SOME DOMAIN IS NOT INFORMED IN A LOCAL METRIC
#-5: SOME DOMAIN IS NOT INFORMED IN A TRANSITION METRIC
#-6: SOME DOMAIN IS NOT INFORMED IN RESOURCES
#-7: SOME RESOURCE IS NOT INFORMED IN A DOMAIN
#-8: SOME RESOURCE HAS INVALID TYPE IN A DOMAIN
#-9: SOME RESOURCE HAS INVALID VALUE IN A DOMAIN

###############################################

######## DOMAINS DATA CLASS BEGIN ########

import yaml
import os

class DomainsData:
	__status = None

	__domainsIDs = None
	__domainsResources = None
	__localMetrics = None
	__transitionsMetrics = None

	######## CONSTRUCTOR ########

	def __init__(self, domainFile):

		if domainFile == None:
			self.__status = 0
		else:
			self.ddProcess(domainFile)

	######## PRIVATE METHODS ########

	def __ddValidate(self, domainYaml):

		if not "DOMAINS" in domainYaml or not "RESOURCES" in domainYaml or not "LOCAL" in domainYaml or not "TRANSITION" in domainYaml:
			self.__status = -3
			return False

		domainsList = domainYaml["DOMAINS"]

		for metric in domainYaml["LOCAL"]:
			for domain in domainsList:
				if domain not in metric:
					self.__status = -4
					return False

		for metric in domainYaml["TRANSITION"]:
			for domain in domainsList:
				if domain not in metric:
					self.__status = -5
					return False

		for domain in domainsList:
			if not domain in domainYaml["RESOURCES"]:
				self.__status = -6
				return False

			if not "MEMORY" in domainYaml["RESOURCES"][domain] or not "NET_IFACES" in domainYaml["RESOURCES"][domain] or not "CPUS" in domainYaml["RESOURCES"][domain]:
				self.__status = -7
				return False

			if not isinstance(domainYaml["RESOURCES"][domain]["MEMORY"], int) and not isinstance(domainYaml["RESOURCES"][domain]["MEMORY"], float):
				self.__status = -8
				return False

			if not isinstance(domainYaml["RESOURCES"][domain]["NET_IFACES"], int):
				self.__status = -8
				return False

			if not isinstance(domainYaml["RESOURCES"][domain]["CPUS"], int):
				self.__status = -8
				return False

			if domainYaml["RESOURCES"][domain]["CPUS"] < 0 or domainYaml["RESOURCES"][domain]["NET_IFACES"] < 0 or domainYaml["RESOURCES"][domain]["MEMORY"] < 0:
				self.__status = -9
				return False

		return True

	######## PUBLIC METHODS ########

	def ddProcess(self, domainFile):

		if not os.path.isfile(domainFile):
			self.__status = -1
			return
		openedFile = open(domainFile, "r")
		fileData = openedFile.read()
		openedFile.close()

		try:
			domainYaml = yaml.safe_load(fileData)
		except:
			self.__status = -2
			return

		if self.__ddValidate(domainYaml):
			self.__domainsIDs = domainYaml["DOMAINS"]
			self.__domainsResources = domainYaml["RESOURCES"]
			self.__localMetrics = domainYaml["LOCAL"]
			self.__transitionsMetrics = domainYaml["TRANSITION"]
			self.__status = 1
		else:
			return

	def ddStatus(self):

		return self.__status

	def ddDomains(self):

		if self.__status != 1:
			return

		return self.__domainsIDs

	def ddResources(self):

		if self.__status != 1:
			return

		return self.__domainsResources

	def  ddLocalMetrics(self):

		if self.__status != 1:
			return

		localMetricsIDs = []
		for metric in self.__localMetrics:
			localMetricsIDs.append(metric["ID"])

		return localMetricsIDs

	def ddTransitionMetrics(self):

		if self.__status != 1:
			return

		transitionMetricsIDs = []
		for metric in self.__transitionsMetrics:
			transitionMetricsIDs.append(metric["ID"])

		return transitionMetricsIDs

	def ddLocalValues(self):

		if self.__status != 1:
			return

		localMetrics = {}
		for metric in self.__localMetrics:
			localMetrics[metric["ID"]] = metric

		return localMetrics

	def ddTransitionValues(self):

		if self.__status != 1:
			return

		transitionMetrics = {}
		for metric in self.__transitionsMetrics:
			transitionMetrics[metric["ID"]] = metric

		return transitionMetrics

######## DOMAINS DATA CLASS END ########
