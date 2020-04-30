######## CUSCO FUNCTION CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service)
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A VALID SFC REQUEST AND CREATES THE
#GOAL FUNCTION DESCRIBED BY IT. AFTER, IT MAKES
#AVAILABLE A EVALUATION FUNCTION TO RECEIVE
#ARGUMENTS, EVALUATE THEM AND RETURNS IT RESULTS.

#THE CLASS STATUS ATTRIBUTE INDICATE ITS
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: NO TOPOLOGY EXPANDED
#1: AVAILABLE EXPANDED TOPOLOGIES

#################################################

import copy

class CUSCOFunction:
	__status = None

	__sfcFunction = None
	__evaluationAggregate = None

	######## CONSTRUCTOR ########

	def __init__(self, sfcRequest):

		if sfcRequest != None:
			self.cfSetup(sfcRequest)
		else:
			self.__status = 0

	######## PRIVATE METHODS ########

	def __cfEvaluateMetric(self, metric, value):

		if (metric["EVALUATION"] == "MULT"):
			return metric["INPUT"] * value
		if (metric["EVALUATION"] == "DIV"):
			return metric["INPUT"] / value
		if (metric["EVALUATION"] == "SUM"):
			return metric["INPUT"] + value
		if (metric["EVALUATION"] == "SUB"):
			return metric["INPUT"] - value

	def __cfUpdateMetric(self, update, operation, value):

		if (operation["EVALUATION"] == "MULT"):
			update["INPUT"] = update["INPUT"] * value
		if (operation["EVALUATION"] == "DIV"):
			update["INPUT"] = update["INPUT"] / value
		if (operation["EVALUATION"] == "SUM"):
			update["INPUT"] = update["INPUT"] + value
		if (operation["EVALUATION"] == "SUB"):
			update["INPUT"] = update["INPUT"] - value

	######## PUBLIC METHODS ########

	def cfSetup(self, sfcRequest):

		self.__sfcFunction = {}
		self.__evaluationAggregate = {}

		for metric in sfcRequest.ycFunction():
			self.__sfcFunction[metric["ID"]] = metric.copy()
			self.__evaluationAggregate[metric["ID"]] = 0

		self.__status = 1

	def cfBranchSetup(self, sfcFunction, branchOperations, branchValues):

		self.__sfcFunction = copy.deepcopy(sfcFunction)
		self.__evaluationAggregate = {}

		for metric in self.__sfcFunction:

			self.__evaluationAggregate[metric] = 0
			if (branchOperations[metric] == "MULT"):
				self.__sfcFunction[metric]["INPUT"] = self.__sfcFunction[metric]["INPUT"] * branchValues[metric]
			if (branchOperations[metric] == "DIV"):
				self.__sfcFunction[metric]["INPUT"] = self.__sfcFunction[metric]["INPUT"] / branchValues[metric]
			if (branchOperations[metric] == "SUM"):
				self.__sfcFunction[metric]["INPUT"] = self.__sfcFunction[metric]["INPUT"] + branchValues[metric]
			if (branchOperations[metric] == "SUB"):
				self.__sfcFunction[metric]["INPUT"] = self.__sfcFunction[metric]["INPUT"] - branchValues[metric]

		self.__status = 1

	def cfBranchUnify(self, segmentsResults):

		for metric in self.__sfcFunction:
			self.__sfcFunction[metric]["INPUT"] = 0

			for result in segmentsResults:
				self.__evaluationAggregate[metric] += result.cfAggregation()[metric]
				self.__sfcFunction[metric]["INPUT"] += result.cfFunction()[metric]["INPUT"]

	def cfOnlyEvaluate(self, elementValues):

		results = {}
		for metric in self.__sfcFunction:
			results[metric] = self.__cfEvaluateMetric(self.__sfcFunction[metric], elementValues[metric])

		return results

	def cfOnlyUpdate(self, elementValues):

		for metric in self.__sfcFunction:
			updater = self.__sfcFunction[metric]["UPDATE"]
			if updater != "STATIC":
				self.__cfUpdateMetric(self.__sfcFunction[metric], self.__sfcFunction[updater], elementValues[updater])

	def cfProcess(self, elementValues):

		results = self.cfOnlyEvaluate(elementValues)
		for evaluation in results:
			self.__evaluationAggregate[evaluation] += results[evaluation]
		self.cfOnlyUpdate(elementValues)

	def cfStatus(self):

		return self.__status

	def cfFunction(self):

		if self.__status != 1:
			return None

		return self.__sfcFunction

	def cfAggregation(self):

		if self.__status != 1:
			return None

		return self.__evaluationAggregate

######## CUSCO FUNCTION CLASS END ########
