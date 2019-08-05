######## GOAL FUNCTION CLASS DESCRIPTION ########

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

from YAMLR.GeneralRequest import GeneralRequest

class GoalFunction:
	__status = None

	__sfcFunction = None
	__evaluationAggregate = None

	######## CONSTRUCTOR ########

	def __init__(self, sfcRequest):

		if sfcRequest != None:
			self.gfSetup(sfcRequest)
		else:
			self.__status = 0

	######## PRIVATE METHODS ########

	def __gfEvaluateMetric(self, metric, value):

		if (metric["EVALUATION"] == "MULT"):
			return metric["INPUT"] * value
		if (metric["EVALUATION"] == "DIV"):
			return metric["INPUT"] / value
		if (metric["EVALUATION"] == "SUM"):
			return metric["INPUT"] + value
		if (metric["EVALUATION"] == "SUB"):
			return metric["INPUT"] - value

	def __gfUpdateMetric(self, update, operation, value):

		if (operation["EVALUATION"] == "MULT"):
			update["INPUT"] = update["INPUT"] * value
		if (operation["EVALUATION"] == "DIV"):
			update["INPUT"] = update["INPUT"] / value
		if (operation["EVALUATION"] == "SUM"):
			update["INPUT"] = update["INPUT"] + value
		if (operation["EVALUATION"] == "SUB"):
			update["INPUT"] = update["INPUT"] - value

	######## PUBLIC METHODS ########

	def gfSetup(self, sfcRequest):

		self.__sfcFunction = {}
		self.__evaluationAggregate = {}

		for metric in sfcRequest.crFunction()["METRICS"]:
			self.__sfcFunction[metric["ID"]] = metric.copy()
			self.__evaluationAggregate[metric["ID"]] = 0

		self.__status = 1

	def gfBranchSetup(self, sfcFunction, branchOperations, branchValues):

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

	def gfBranchUnify(self, segmentsResults):

		for metric in self.__sfcFunction:
			self.__sfcFunction[metric]["INPUT"] = 0

			for result in segmentsResults:
				self.__evaluationAggregate[metric] += result.gfAggregation()[metric]
				self.__sfcFunction[metric]["INPUT"] += result.gfFunction()[metric]["INPUT"]

	def gfOnlyEvaluate(self, elementValues):

		results = {}
		for metric in self.__sfcFunction:
			results[metric] = self.__gfEvaluateMetric(self.__sfcFunction[metric], elementValues[metric])

		return results

	def gfOnlyUpdate(self, elementValues):

		for metric in self.__sfcFunction:
			updater = self.__sfcFunction[metric]["UPDATE"]
			if updater != "STATIC":
				self.__gfUpdateMetric(self.__sfcFunction[metric], self.__sfcFunction[updater], elementValues[updater])

	def gfProcess(self, elementValues):

		results = self.gfOnlyEvaluate(elementValues)
		for evaluation in results:
			self.__evaluationAggregate[evaluation] += results[evaluation]
		self.gfOnlyUpdate(elementValues)

	def gfStatus(self):

		return self.__status

	def gfFunction(self):

		if self.__status != 1:
			return None

		return self.__sfcFunction

	def gfAggregation(self):

		if self.__status != 1:
			return None

		return self.__evaluationAggregate

######## GOAL FUNCTION CLASS END ########
