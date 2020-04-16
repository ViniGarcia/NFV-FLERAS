import os
import sys
import yaml
import copy
import itertools
import numpy
import random

##------##------##------##------ REQUEST PARSER CLASS ------##------##------##------##
#NAME: RequestProcessor
#OBJECTIVE: Validates the YAML request document and organizes it to be processed by the
#			multu-objective genetic algorithm.
#STATUS CODES:
#		0 -> Not evaluated yet
#		1 -> Succesfully evaluated
#		-1 to -40 -> Error

class RequestProcessor:

	__status = 0
	__metrics = None
	__service = None
	__domains = None

	__domainDictionary = None
	__metricDictionary = None

	def __validate(self, requestYAML):

		if not "METRICS" in requestYAML or not "SERVICE" in requestYAML or not "DOMAINS" in requestYAML:
			return -3


		if not "LOCAL" in requestYAML["METRICS"] or not "TRANSITION" in requestYAML["METRICS"]:
			return -4

		if not "TOPOLOGY" in requestYAML["SERVICE"] or not "FUNCTION" in requestYAML["SERVICE"]:
			return -5

		if len(requestYAML["DOMAINS"]) == 0:
			return -6

		if not isinstance(requestYAML["METRICS"]["LOCAL"], dict) or not isinstance(requestYAML["METRICS"]["TRANSITION"], dict):
			return -7

		if len(requestYAML["METRICS"]["LOCAL"]) == 0 and len(requestYAML["METRICS"]["TRANSITION"]) == 0:
			return -8

		for metric in requestYAML["METRICS"]["LOCAL"]:
			if not "OBJECTIVE" in requestYAML["METRICS"]["LOCAL"][metric] or not "POLICIES" in requestYAML["METRICS"]["LOCAL"][metric]:
				return -9

			if not requestYAML["METRICS"]["LOCAL"][metric]["OBJECTIVE"] in ["MAXIMIZATION", "MINIMIZATION"]:
				return -10

			if not isinstance(requestYAML["METRICS"]["LOCAL"][metric]["POLICIES"], list):
				return -11

			validPolicies = []
			for policy in requestYAML["METRICS"]["LOCAL"][metric]["POLICIES"]:
				policy = policy.split(" ")
				if not policy[0] in ["!=", "==", ">", "<", ">=", "<="]:
					return -12
				try:
					float(policy[1])
				except:
					return -13
				validPolicies.append(policy[0] + policy[1])
			requestYAML["METRICS"]["LOCAL"][metric]["POLICIES"] = validPolicies

		for metric in requestYAML["METRICS"]["TRANSITION"]:
			if not "OBJECTIVE" in requestYAML["METRICS"]["TRANSITION"][metric] or not "POLICIES" in requestYAML["METRICS"]["TRANSITION"][metric]:
				return -14

			if not requestYAML["METRICS"]["TRANSITION"][metric]["OBJECTIVE"] in ["MAXIMIZATION", "MINIMIZATION"]:
				return -15

			if not isinstance(requestYAML["METRICS"]["TRANSITION"][metric]["POLICIES"], list):
				return -16

			validPolicies = []
			for policy in requestYAML["METRICS"]["TRANSITION"][metric]["POLICIES"]:
				policy = policy.split(" ")
				if not policy[0] in ["=", ">", "<", ">=", "<="]:
					return -17
				try:
					float(policy[1])
				except:
					return -18
				validPolicies.append(policy[0] + policy[1])
			requestYAML["METRICS"]["TRANSITION"][metric]["POLICIES"] = validPolicies

		if not isinstance(requestYAML["SERVICE"]["TOPOLOGY"], list) or not isinstance(requestYAML["SERVICE"]["FUNCTION"], dict):
			return -19

		for member in requestYAML["SERVICE"]["TOPOLOGY"]:
			if member in ["IN", "{", "}", "/"] or str.startswith(member, "EN"):
				continue
			if str.startswith(member, "< ") and str.endswith(member, " >"):
				dependency = member.split(" ")
				if len(dependency) != 3:
					return -20
				if not dependency[1] in requestYAML["DOMAINS"]:
					return -21
				continue
			if not member in requestYAML["SERVICE"]["FUNCTION"]:
				return -22

		for member in requestYAML["SERVICE"]["FUNCTION"]:
			if not member in requestYAML["SERVICE"]["TOPOLOGY"]:
				return -23

		if not isinstance(requestYAML["DOMAINS"], dict):
			return -24

		for member in requestYAML["SERVICE"]["FUNCTION"]:
			if not isinstance(requestYAML["SERVICE"]["FUNCTION"][member], dict):
				return -25
			if not "MEMORY" in requestYAML["SERVICE"]["FUNCTION"][member] or not "VCPU" in requestYAML["SERVICE"]["FUNCTION"][member] or not "IFACES" in requestYAML["SERVICE"]["FUNCTION"][member]:
				return -26
			if not isinstance(requestYAML["SERVICE"]["FUNCTION"][member]["MEMORY"], int) or not isinstance(requestYAML["SERVICE"]["FUNCTION"][member]["VCPU"], int) or not isinstance(requestYAML["SERVICE"]["FUNCTION"][member]["IFACES"], int):
				return -27
			if requestYAML["SERVICE"]["FUNCTION"][member]["MEMORY"] < 0 or requestYAML["SERVICE"]["FUNCTION"][member]["VCPU"] < 0 or requestYAML["SERVICE"]["FUNCTION"][member]["IFACES"] < 0:
				return -28

		for member in requestYAML["DOMAINS"]:
			if not isinstance(requestYAML["DOMAINS"][member], dict):
				return -29
			if not "RESOURCE" in requestYAML["DOMAINS"][member] or not "LOCAL" in requestYAML["DOMAINS"][member] or not "TRANSITION" in requestYAML["DOMAINS"][member]:
				return -30
			if not "MEMORY" in requestYAML["DOMAINS"][member]["RESOURCE"] or not "VCPU" in requestYAML["DOMAINS"][member]["RESOURCE"] or not "IFACES" in requestYAML["DOMAINS"][member]["RESOURCE"]:
				return -31
			if not isinstance(requestYAML["DOMAINS"][member]["RESOURCE"]["MEMORY"], int) or not isinstance(requestYAML["DOMAINS"][member]["RESOURCE"]["VCPU"], int) or not isinstance(requestYAML["DOMAINS"][member]["RESOURCE"]["IFACES"], int):
				return -32
			if requestYAML["DOMAINS"][member]["RESOURCE"]["MEMORY"] < 0 or requestYAML["DOMAINS"][member]["RESOURCE"]["VCPU"] < 0 or requestYAML["DOMAINS"][member]["RESOURCE"]["IFACES"] < 0:
				return -33

			for metric in requestYAML["DOMAINS"][member]["LOCAL"]:
				if not metric in requestYAML["METRICS"]["LOCAL"]:
					return -34
				if not isinstance(requestYAML["DOMAINS"][member]["LOCAL"][metric], int) and not isinstance(requestYAML["DOMAINS"][member]["LOCAL"][metric], float):
					return -35

			for metric in requestYAML["METRICS"]["LOCAL"]:
				if not metric in requestYAML["DOMAINS"][member]["LOCAL"]:
					return -36

			for domain in requestYAML["DOMAINS"][member]["TRANSITION"]:
				if not domain in requestYAML["DOMAINS"]:
					return -37

				for metric in requestYAML["DOMAINS"][member]["TRANSITION"][domain]:
					if not metric in requestYAML["METRICS"]["TRANSITION"]:
						return -38
					if not isinstance(requestYAML["DOMAINS"][member]["TRANSITION"][domain][metric], int) and not isinstance(requestYAML["DOMAINS"][member]["TRANSITION"][domain][metric], float):
						return -39

				for metric in requestYAML["METRICS"]["TRANSITION"]:
					if not metric in requestYAML["DOMAINS"][member]["TRANSITION"][domain]:
						return -40

		return 1


	def __translate(self):

		self.__metricDictionary = {}
		keylist = list(self.__metrics["LOCAL"].keys()) + list(self.__metrics["TRANSITION"].keys())
		for index in range(len(keylist)):
			self.__metricDictionary[index] = keylist[index]
			if keylist[index] in self.__metrics["LOCAL"]:
				place = "LOCAL"
			else:
				place = "TRANSITION"
			self.__metrics[place][index] = self.__metrics[place].pop(keylist[index])
			for member in self.__domains:
				if place == "LOCAL":
					self.__domains[member][place][index] = self.__domains[member][place].pop(keylist[index])
				else:
					for domain in self.__domains[member][place]:
						self.__domains[member][place][domain][index] = self.__domains[member][place][domain].pop(keylist[index])

		self.__domainDictionary = {}
		keylist = list(self.__domains.keys())
		for index in range(len(keylist)):
			self.__domainDictionary[index] = keylist[index]
			self.__domains[index] = self.__domains.pop(keylist[index])
		for index in range(len(keylist)):
			for domain in list(self.__domains[index]["TRANSITION"].keys()):
				self.__domains[index]["TRANSITION"][keylist.index(domain)] = self.__domains[index]["TRANSITION"].pop(domain)


	def __update(self):

		self.__service["STRUCTURE"] = []
		self.__service["DEPENDENCY"] = []

		domainKeys = list(self.__domainDictionary.keys())
		domainNames = list(self.__domainDictionary.values())
		branchList = []

		self.__service["STRUCTURE"].append((self.__service["TOPOLOGY"][1], 1, [0]))
		for index in range(2, len(self.__service["TOPOLOGY"])):
			if self.__service["TOPOLOGY"][index] in self.__service["FUNCTION"]:
				if self.__service["TOPOLOGY"][index-1] != "/":
					if self.__service["TOPOLOGY"][index-1] != "}":
						self.__service["STRUCTURE"].append((self.__service["TOPOLOGY"][index], index, [(len(self.__service["STRUCTURE"]) - 1)]))
					else:
						self.__service["STRUCTURE"].append((self.__service["TOPOLOGY"][index], index, branchList[-1][1]))
						branchList.pop()
				else:
					self.__service["STRUCTURE"].append((self.__service["TOPOLOGY"][index], index, [branchList[-1][0]]))
					branchList[-1][1].append((len(self.__service["STRUCTURE"]) - 2))
				continue
			if str.startswith(self.__service["TOPOLOGY"][index], "<"):
				self.__service["DEPENDENCY"].append((len(self.__service["STRUCTURE"])-1, domainKeys[domainNames.index(self.__service["TOPOLOGY"][index].split(" ")[1])]))
				continue
			if self.__service["TOPOLOGY"][index] == "{":
				branchList.append((len(self.__service["STRUCTURE"]) - 1, []))
				continue
			if self.__service["TOPOLOGY"][index] == "}":
				branchList[-1][1].append(len(self.__service["STRUCTURE"]) - 1)


	def __init__(self, requestFile):

		if not os.path.isfile(requestFile):
			self.__status = -1
			return

		file = open(requestFile, 'r')
		try:
			requestYAML = yaml.safe_load(file)
		except:
			self.__status = -2
			return

		self.__status = self.__validate(requestYAML)
		if self.__status != 1:
			return

		self.__metrics = requestYAML["METRICS"]
		self.__service = requestYAML["SERVICE"]
		self.__domains = requestYAML["DOMAINS"]
		self.__translate()
		self.__update()

	def getStatus(self):
		return self.__status


	def getMetrics(self):
		return self.__metrics


	def getService(self):
		return self.__service


	def getDomains(self):
		return self.__domains


	def getMetricDictionary(self):
		return self.__metricDictionary


	def getDomainDictionary(self):
		return self.__domainDictionary


##------##------##------##------##--------##--------##------##------##------##------##


##------##------##------##------ SERVICE MAPPING PROBLEM CLASS ------##------##------##------##
#NAME: ServiceMapping
#OBJECTIVE: Evaluates mappings create by the platypus genetic algorithms, this class is designed
#			to be directly used in platypus.
#STATUS CODES:
#		0 -> Iddle state
#		1 -> Ready to process

class ServiceMapping():

	__status = 0
	__metrics = None
	__service = None
	__domains = None
	__policies = None

	def __init__(self, metrics, service, domains):

		#Initializing processing data
		self.__metrics = metrics
		self.__service = service
		self.__domains = domains

		#Status updated to "ready to process"
		self.__status = 1


	def __rollback(self, partialCandidate, index, parameter, computation):
		
		for resource in computation[index]:
			computation[partialCandidate[index]][resource] -= self.__service["FUNCTION"][self.__service["STRUCTURE"][index][0]][resource]
			if resource == parameter:
				return

	def __evaluate(self, partialCandidate, index, evaluation, computation):

		for resource in computation[index]:
			computation[partialCandidate[index]][resource] += self.__service["FUNCTION"][self.__service["STRUCTURE"][index][0]][resource]
			if computation[partialCandidate[index]][resource] > self.__domains[partialCandidate[index]]["RESOURCE"][resource]:
				self.__rollback(partialCandidate, index, resource, computation)
				return False

		for metric in self.__metrics["LOCAL"]:
			evaluation[metric] += self.__domains[partialCandidate[index]]["LOCAL"][metric]

		flag = True
		for connection in self.__service["STRUCTURE"][index][2]:
			if partialCandidate[index] != partialCandidate[connection]:
				flag = False
				break
		if flag:
			return evaluation

		meanDictionary = None
		meanFactor = 0
		for connection in self.__service["STRUCTURE"][index][2]:
			meanFactor += 1

			if partialCandidate[index] == partialCandidate[connection]:
				continue

			if meanDictionary == None:
				meanDictionary = copy.copy(self.__domains[partialCandidate[connection]]["TRANSITION"][partialCandidate[index]])
			else:
				for metric in self.__metrics["TRANSITION"]:
					meanDictionary[metric] += self.__domains[partialCandidate[connection]]["TRANSITION"][partialCandidate[index]][metric]

		for metric in self.__metrics["TRANSITION"]:
			evaluation[metric] += meanDictionary[metric] / meanFactor

		return True


	def __choose(self, options):

		aggregations = [0] * len(options)

		for origin in ["LOCAL", "TRANSITION"]:
			metrics = list(self.__metrics[origin].keys())
			for parameter in range(len(metrics)):
				partial = [candidate[1][parameter] for candidate in options]
				aMax, aMin = max(partial), min(partial)
				if self.__metrics[origin][metrics[parameter]]["OBJECTIVE"] == "MAXIMIZATION":
					for index in range(len(partial)):
						if aMax != aMin:
							aggregations[index] += (aMax - partial[index]) / (aMax - aMin)
						else:
							aggregations[index] += 0
				else:
					aMin = min(partial)
					for index in range(len(partial)):
						if aMax != aMin:
							aggregations[index] = (partial[index] - aMin) / (aMax - aMin)
						else:
							aggregations[index] += 0

		return aggregations.index(min(aggregations))


	def execute(self, rounds, factor):

		acceptedCandidates = [[],[]]
		for control in range(rounds):
			
			evaluation = [0] * (len(self.__metrics["LOCAL"]) + len(self.__metrics["TRANSITION"]))
			computation = [{"MEMORY":0, "VCPU":0, "IFACES":0} for index in range(len(self.__domains))]
			partialCandidate = None

			search = {x:list(self.__domains[x]["TRANSITION"].keys()) for x in list(self.__domains.keys())}
			for domain in search:
				search[domain].append(domain)

			initialPoint = list(search.keys())
			random.shuffle(initialPoint)
			
			saveEvaluation = copy.deepcopy(evaluation)
			saveComputation = copy.deepcopy(computation)
			greedyOptions = []

			flag = False
			for domain in range(len(initialPoint)):
				partialCandidate = [initialPoint[domain]]
				flag = self.__evaluate(partialCandidate, 0, evaluation, computation)
				if flag:
					greedyOptions.append((partialCandidate, evaluation, computation))
					if domain < factor:
						evaluation = copy.deepcopy(saveEvaluation)
						computation = copy.deepcopy(saveComputation)
						continue
					else:
						break
				else:
					continue
			if len(greedyOptions) == 0:
				return acceptedCandidates
			elif len(greedyOptions) == 1:
				partialCandidate = greedyOptions[0][0]
				evaluation = greedyOptions[0][1]
				computation = greedyOptions[0][2]
			else:
				greedyIndex = self.__choose(greedyOptions)
				partialCandidate = greedyOptions[greedyIndex][0]
				evaluation = greedyOptions[greedyIndex][1]
				computation = greedyOptions[greedyIndex][2]

			for index in range(1, len(self.__service["FUNCTION"])):
				domainOptions = list(search.keys())
				for connection in self.__service["STRUCTURE"][index][2]:
					domainOptions = set(domainOptions).intersection(set(search[connection]))
				
				domainOptions = list(domainOptions)
				random.shuffle(domainOptions)
				if len(domainOptions) == 0:
					flag = False
					break

				savePartialCandidate = copy.deepcopy(partialCandidate)
				saveEvaluation = copy.deepcopy(evaluation)
				saveComputation = copy.deepcopy(computation)
				greedyOptions = []

				for domain in range(len(domainOptions)):
					partialCandidate.append(domainOptions[domain])
					flag = self.__evaluate(partialCandidate, index, evaluation, computation)
					if flag:
						greedyOptions.append((partialCandidate, evaluation, computation))
						if domain < factor:
							partialCandidate = copy.deepcopy(savePartialCandidate)
							evaluation = copy.deepcopy(saveEvaluation)
							computation = copy.deepcopy(saveComputation)
							continue
						else:
							break
					else:
						partialCandidate.pop()
						evaluation = copy.deepcopy(saveEvaluation)
						computation = copy.deepcopy(saveComputation)
				if len(greedyOptions) == 0:
					break
				elif len(greedyOptions) == 1:
					partialCandidate = greedyOptions[0][0]
					evaluation = greedyOptions[0][1]
					computation = greedyOptions[0][2]
					flag = True
				else:
					greedyIndex = self.__choose(greedyOptions)
					partialCandidate = greedyOptions[greedyIndex][0]
					evaluation = greedyOptions[greedyIndex][1]
					computation = greedyOptions[greedyIndex][2]
					flag = True
			if not flag:
				continue

			acceptedCandidates[0].append(partialCandidate)
			acceptedCandidates[1].append(evaluation)

		return acceptedCandidates

	def getStatus(self):
		return self.__status

##------##------##------##------##-----##-----##-----##------##------##------##------##------##


##------##------##------##------ MAPPING CLASS ------##------##------##------##
#NAME: Mapping
#OBJECTIVE:
#STATUS CODES:

class Mapping:

	__status = 0
	__request = None
	__algorithm = None
	__problem = None

	def __paretoFront(self, aggregations):

		aggregations = numpy.array(aggregations)
		is_efficient = numpy.ones(aggregations.shape[0], dtype = bool)
		for i, c in enumerate(aggregations):
			if is_efficient[i]:
				is_efficient[is_efficient] = numpy.any(aggregations[is_efficient]>c, axis=1)
				is_efficient[i] = True

		return is_efficient.tolist()

	def __paretoIndexes(self, aggregations):

		aggregations = numpy.array(aggregations)
		i_dominates_j = numpy.all(aggregations[:,None] <= aggregations, axis=-1) & numpy.any(aggregations[:,None] < aggregations, axis=-1)
		remaining = numpy.arange(len(aggregations))
		fronts = numpy.empty(len(aggregations), int)
		frontier_index = 0

		while remaining.size > 0:
			dominated = numpy.any(i_dominates_j[remaining[:,None], remaining], axis=0)
			fronts[remaining[~dominated]] = frontier_index
			remaining = remaining[dominated]
			frontier_index += 1

		return fronts.tolist()


	def __init__(self, request):

		self.__request = RequestProcessor(request)
		self.__status = self.__request.getStatus()
		if self.__status != 1:
			return

		self.__algorithm = ServiceMapping(self.__request.getMetrics(), self.__request.getService(), self.__request.getDomains())


	def execute(self, rounds, tests):

		if self.__status != 1 and (self.__status > -30 and self.__status < 0):
			return self.__status

		evaluations = self.__algorithm.execute(rounds, tests)
		return evaluations


	def outputIndex(self, filename, result):

		result.append(self.__paretoIndexes(result[1]))
		metricList = list(self.__request.getMetrics()["LOCAL"].keys()) + list(self.__request.getMetrics()["TRANSITION"].keys())
		metricKeys = [self.__request.getMetricDictionary()[index] for index in range(len(metricList))]

		file = open(o, "w+")
		file.write("MAPPING;")
		for metric in metricKeys:
			file.write(metric + ";")
		file.write("PARETO")
		file.write("\n")

		for index in range(len(result[0])):
			file.write(str(list(result[0][index])) + ";")
			for subindex in range(len(metricKeys)):
				file.write(str(result[1][index][subindex]) + ";")
			file.write(str(result[2][index]))
			file.write("\n")

		file.write("PF CANDIDATES:;" + str(result[2].count(0)))
		file.close()

	def outputFront(self, filename, result):

		result.append(self.__paretoFront(result[1]))
		metricList = list(self.__request.getMetrics()["LOCAL"].keys()) + list(self.__request.getMetrics()["TRANSITION"].keys())
		metricKeys = [self.__request.getMetricDictionary()[index] for index in range(len(metricList))]

		file = open(o, "w+")
		file.write("MAPPING;")
		for metric in metricKeys:
			file.write(metric + ";")
		file.write("PARETO")
		file.write("\n")

		for index in range(len(result[0])):
			file.write(str(list(result[0][index])) + ";")
			for subindex in range(len(metricKeys)):
				file.write(str(result[1][index][subindex]) + ";")
			if result[2][index]:
				file.write(str(0))
			else:
				file.write(str(1))
			file.write("\n")

		file.write("PF CANDIDATES:;" + str(result[2].count(True)))
		file.close()

	def getStatus(self):
		return self.__status

##------##------##------##------##-----##-----##-----##------##------##------##

o = None
r = None
t = None

if len(sys.argv) < 6 or len(sys.argv) > 9:
	print("===================== RANDOM/GREEDY MAPPING ============================")
	print("-> *.py file_name -r nr_rounds -t nr_tests [-o output_name -i|-f]")
	print("\t- -t 1 -> Random Search")
	print("\t- -t n | n < max_domain_connections -> Stochastic Greedy Search")
	print("\t- -t n | n = max_domain_connections -> Traditional Greedy Search")
	print("========================================================================")
	exit()

if len(sys.argv) >= 6:
	if not os.path.isfile(sys.argv[1]):
		print("ERROR: FILE DOES NOT EXIST!")
		exit()
	if sys.argv[2] == "-r" and sys.argv[4] == "-t":
		try:
			r = int(sys.argv[3])
			t = int(sys.argv[5])
		except:
			print("ERROR: -r AND -t MUST BE INTEGER NUMBERS!")
			exit()
	else:
		print("ERROR: ESSENTIAL FLAGS ARE NOT DEFINED (-r / -t)!")
		exit()

if len(sys.argv) == 9:
	if sys.argv[6] == "-o" and sys.argv[8] in ["-i", "-f"]:
		o = sys.argv[7]
	else:
		print("ERROR: INVALID OPTIONAL FLAGS FOUND (JUST -o AND -i|-f)!")
		exit()
else:
	if len(sys.argv) > 6:
		print("ERROR: INVALID DEFINITION OF OPTIONAL FLAGS!")
		exit()

mapper = Mapping(sys.argv[1])
result = mapper.execute(r, t)
if o != None:
	if sys.argv[6] == "-i":
		mapper.outputIndex(o, result)
	else:
		mapper.outputFront(o, result)