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

###############################################

######## DOMAINS DATA CLASS BEGIN ########

import yaml
import os

class DomainsData:
	__status = None

	__domainsIDs = None
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
		
		if not "DOMAINS" in domainYaml or not "LOCAL" in domainYaml or not "TRANSITION" in domainYaml:
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
			domainYaml = yaml.load(fileData)
		except:
			self.__status = -2
			return

		if self.__ddValidate(domainYaml):
			self.__domainsIDs = domainYaml["DOMAINS"]
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

		return self.__localMetrics

	def ddTransitionValues(self):

		if self.__status != 1:
			return

		return self.__transitionsMetrics
		
######## DOMAINS DATA CLASS END ########