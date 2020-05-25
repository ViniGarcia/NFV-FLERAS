import os
import sys
import yaml
import copy
import random
import itertools
import numpy

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


	def __evaluate(self, candidate):

		evaluation = [0] * (len(self.__metrics["LOCAL"]) + len(self.__metrics["TRANSITION"]))
		constraints = []
		computation = [{"MEMORY":0, "VCPU":0, "IFACES":0} for index in range(len(self.__domains))]

		for index in range(len(candidate)):

			for resource in computation[0]:
				computation[candidate[index]][resource] += self.__service["FUNCTION"][self.__service["STRUCTURE"][index][0]][resource]
				if computation[candidate[index]][resource] > self.__domains[candidate[index]]["RESOURCE"][resource]:
					return None

			for metric in self.__metrics["LOCAL"]:
				evaluation[metric] += self.__domains[candidate[index]]["LOCAL"][metric]

			flag = True
			for connection in self.__service["STRUCTURE"][index][2]:
				if candidate[index] != candidate[connection]:
					flag = False
					break
			if flag:
				continue

			meanDictionary = None
			meanFactor = 0
			for connection in self.__service["STRUCTURE"][index][2]:
				meanFactor += 1

				if candidate[index] == candidate[connection]:
					continue

				if not candidate[index] in self.__domains[candidate[connection]]["TRANSITION"]:
					return None

				if meanDictionary == None:
					meanDictionary = copy.copy(self.__domains[candidate[connection]]["TRANSITION"][candidate[index]])
				else:
					for metric in self.__metrics["TRANSITION"]:
						meanDictionary[metric] += self.__domains[candidate[connection]]["TRANSITION"][candidate[index]][metric]

			for metric in self.__metrics["TRANSITION"]:
				evaluation[metric] += meanDictionary[metric] / meanFactor

		return evaluation


	def execute(self, rounds):

		acceptedCandidates = [[],[]]
		for r in range(rounds):
			
			combination = []
			for index in range(len(self.__service["FUNCTION"])):
				combination.append(random.randint(0, len(self.__domains)-1))

			result = self.__evaluate(combination)
			if result != None:
				acceptedCandidates[0].append(combination)
				acceptedCandidates[1].append(result)

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
	__objectives = None
	__rounds = None


	def __paretoFrontierSubroutine(self, results, frontiers, front_index, exchange_indexes):

		new_front = []
		add_front = []

		for index in exchange_indexes:
			it_dominates = True

			for candidate in range(len(frontiers[front_index])):
				count_dominated = 0

				for objective in range(len(self.__objectives)):
					if self.__objectives[objective] == "MAXIMIZATION":
						if results[index][objective] < results[frontiers[front_index][candidate]][objective]:
							count_dominated += 1
					elif self.__objectives[objective] == "MINIMIZATION":
						if results[index][objective] > results[frontiers[front_index][candidate]][objective]:
							count_dominated += 1

				if count_dominated > 0:
					it_dominates = False
					break

			if it_dominates:
				new_front.append(index)
			else:
				add_front.append(index)

		frontiers[front_index] = frontiers[front_index] + add_front
		if len(new_front) > 0:
			frontiers.insert(front_index, new_front)


	def __paretoFrontiers(self, results):

		frontiers = [[0], []]
		indexes = [i for i in range(1, len(results))]

		while True:
			if len(indexes) == 0:
				break
			index = indexes.pop(0)

			for front in range(len(frontiers)):
				is_dominated = False
				it_dominates = []

				for candidate in range(len(frontiers[front])):
					count_dominated = 0
					result_equity = True

					for objective in range(len(self.__objectives)):
						if self.__objectives[objective] == "MAXIMIZATION":
							if results[index][objective] < results[frontiers[front][candidate]][objective]:
								count_dominated += 1
							if result_equity and results[index][objective] != results[frontiers[front][candidate]][objective]:
								result_equity = False
						elif self.__objectives[objective] == "MINIMIZATION":
							if results[index][objective] > results[frontiers[front][candidate]][objective]:
								count_dominated += 1
							if result_equity and results[index][objective] != results[frontiers[front][candidate]][objective]:
								result_equity = False

					if result_equity:
						break
					if count_dominated == len(self.__objectives):
						is_dominated = True
						break
					if count_dominated == 0:
						it_dominates.append(frontiers[front][candidate])

				if result_equity:
					frontiers[front].append(index)
					break
				if not is_dominated and len(it_dominates) < len(frontiers[front]):
					frontiers[front].append(index)
					if len(it_dominates) > 0:
						frontiers[front] = list(set(frontiers[front]) - set(it_dominates))
						self.__paretoFrontierSubroutine(results, frontiers, front + 1, it_dominates)
					break
				if is_dominated:
					continue
				if len(it_dominates) == len(frontiers[front]):
					frontiers.insert(front, [index])
					break

		return frontiers[:-1]


	def __init__(self, request, rounds):

		self.__request = RequestProcessor(request)
		self.__rounds = rounds
		self.__status = self.__request.getStatus()
		if self.__status != 1:
			return

		metrics = self.__request.getMetrics()
		self.__objectives = []
		for metric in metrics["LOCAL"]:
			self.__objectives.append(metrics["LOCAL"][metric]["OBJECTIVE"])
		for metric in metrics["TRANSITION"]:
			self.__objectives.append(metrics["TRANSITION"][metric]["OBJECTIVE"])

		self.__algorithm = ServiceMapping(self.__request.getMetrics(), self.__request.getService(), self.__request.getDomains())


	def execute(self):

		if self.__status != 1 and (self.__status > -30 and self.__status < 0):
			return self.__status

		evaluations = self.__algorithm.execute(self.__rounds)
		return evaluations


	def outputFrontiers(self, filename, result):

		ndResult = [[], []]
		for index in range(len(result[0])):
			if not result[0][index] in ndResult[0]:
				ndResult[0].append(result[0][index])
				ndResult[1].append(result[1][index])
		
		indexFrontiers = self.__paretoFrontiers(ndResult[1])
		metricList = list(self.__request.getMetrics()["LOCAL"].keys()) + list(self.__request.getMetrics()["TRANSITION"].keys())
		metricKeys = [self.__request.getMetricDictionary()[index] for index in range(len(metricList))]

		file = open(filename, "w+")
		file.write("MAPPING;")
		for metric in metricKeys:
			file.write(metric + ";")
		file.write("PARETO")
		file.write("\n")

		for index in indexFrontiers[0]:
			file.write(str(list(ndResult[0][index])) + ";")
			for subindex in range(len(metricKeys)):
				file.write(str(ndResult[1][index][subindex]) + ";")
			file.write("0")
			file.write("\n")

		file.close()

	def getStatus(self):
		return self.__status

##------##------##------##------##-----##-----##-----##------##------##------##

o = None
r = None

if len(sys.argv) < 4 or len(sys.argv) > 6:
	print("===================== RANDOM MAPPING =====================")
	print("-> *.py file_name -r nr_rounds [-o output_name]")
	print("==========================================================")
	exit()

if sys.argv[2] == "-r":
	try:
		r = int(sys.argv[3])
	except:
		print("ERROR: INVALID VALUE " + str(sys.argv[3]))
		exit()
else:
	print("ERROR: INVALID FLAG " + str(sys.argv[2]))
	exit()

if len(sys.argv) == 6:
	if sys.argv[4] == "-o":
		o = sys.argv[5]
	else:
		print("ERROR: INVALID FLAG " + str(sys.argv[5]))

mapper = Mapping(sys.argv[1], r)
result = mapper.execute()
if o != None:
	mapper.outputFrontiers(o, result)