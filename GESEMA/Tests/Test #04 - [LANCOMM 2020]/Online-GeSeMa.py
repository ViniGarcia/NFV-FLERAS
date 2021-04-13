import os
import sys
import yaml
import copy
import random
import numpy
import statistics
import local_platypus

##------##------##------##------ REQUEST PARSER CLASS ------##------##------##------##
#NAME: RequestProcessor
#OBJECTIVE: Validates the YAML request document and organizes it to be processed by the
#			multu-objective genetic algorithm.
#STATUS CODES:
#		0 -> Not evaluated yet
#		1 -> Succesfully evaluated
#		-1 to -38 -> Error

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
				if not isinstance(requestYAML["DOMAINS"][member]["LOCAL"][metric], int) and not isinstance(requestYAML["DOMAINS"][member]["LOCAL"][metric], float):
					return -34

			for metric in requestYAML["METRICS"]["LOCAL"]:
				if not metric in requestYAML["DOMAINS"][member]["LOCAL"]:
					return -35

			for domain in requestYAML["DOMAINS"][member]["TRANSITION"]:
				if not domain in requestYAML["DOMAINS"]:
					return -36

				for metric in requestYAML["DOMAINS"][member]["TRANSITION"][domain]:
					if not isinstance(requestYAML["DOMAINS"][member]["TRANSITION"][domain][metric], int) and not isinstance(requestYAML["DOMAINS"][member]["TRANSITION"][domain][metric], float):
						return -37

				for metric in requestYAML["METRICS"]["TRANSITION"]:
					if not metric in requestYAML["DOMAINS"][member]["TRANSITION"][domain]:
						return -38

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

class ServiceMapping(local_platypus.Problem):

	__status = 0
	__metrics = None
	__service = None
	__domains = None
	__policies = None

	__penalize = None
	__taboo = None
	__generator = None

	def __penalty(self):
		self.__penalize = []

		for metric in range(0, len(self.__metrics["LOCAL"])):
			parameter = self.__domains[0]["LOCAL"][metric]
			for domain in range(1, len(self.__domains)):
				if self.__metrics["LOCAL"][metric]["OBJECTIVE"] == "MINIMIZATION":
					if self.__domains[domain]["LOCAL"][metric] > parameter:
						parameter = self.__domains[domain]["LOCAL"][metric]
				else:
					if self.__domains[domain]["LOCAL"][metric] < parameter:
						parameter = self.__domains[domain]["LOCAL"][metric]

			if self.__metrics["LOCAL"][metric]["OBJECTIVE"] == "MINIMIZATION":
				if parameter < 0:
					self.__penalize.append(1)
				else:
					self.__penalize.append(parameter * len(self.__service["STRUCTURE"]) + 1)
			else:
				if parameter < 0:
					self.__penalize.append(parameter * len(self.__service["STRUCTURE"]) - 1)
				else:
					self.__penalize.append(-1)

		for metric in range(len(self.__metrics["LOCAL"]), len(self.__metrics["LOCAL"]) + len(self.__metrics["TRANSITION"])):
			parameter = None
			for domain in range(0, len(self.__domains)):
				for connection in self.__domains[domain]["TRANSITION"]:

					if parameter == None:
						parameter = self.__domains[domain]["TRANSITION"][connection][metric]
						continue

					if self.__metrics["TRANSITION"][metric]["OBJECTIVE"] == "MINIMIZATION":
						if self.__domains[domain]["TRANSITION"][connection][metric] > parameter:
							parameter = self.__domains[domain]["TRANSITION"][connection][metric]
					else:
						if self.__domains[domain]["TRANSITION"][connection][metric] < parameter:
							parameter = self.__domains[domain]["TRANSITION"][connection][metric]

			if self.__metrics["TRANSITION"][metric]["OBJECTIVE"] == "MINIMIZATION":
				if parameter < 0:
					self.__penalize.append(1)
				else:
					self.__penalize.append(parameter * len(self.__service["STRUCTURE"]) + 1)
			else:
				if parameter < 0:
					self.__penalize.append(parameter * len(self.__service["STRUCTURE"]) - 1)
				else:
					self.__penalize.append(-1)


	def __adjust(self, candidate):
	
		cDomains = set(candidate)
		cDuplicates = set([x for x in candidate if candidate.count(x) > 1])
		pSearch = self.__generator.search()

		for duplicate in cDuplicates:
			index = len(candidate) - candidate[::-1].index(duplicate) - 1
			available = set(pSearch[candidate[index-1]]) - cDomains
			substitute = random.randint(0, len(available)-1)
			candidate[index] = list(available)[substitute]
			cDomains.add(substitute)


	def __init__(self, metrics, service, domains, generator):
		#Preparing problem directions and constraints
		self.__policies = {"EQUATION":[], "INDEX":[]}
		directions = []
		for index in range(len(metrics["LOCAL"])):
			if metrics["LOCAL"][index]["OBJECTIVE"] == "MAXIMIZATION":
				directions.append(local_platypus.Problem.MAXIMIZE)
			else:
				directions.append(local_platypus.Problem.MINIMIZE)
			for policy in metrics["LOCAL"][index]["POLICIES"]:
				self.__policies["EQUATION"].append(policy)
				self.__policies["INDEX"].append(index)
		for index in range(len(metrics["LOCAL"]), len(metrics["LOCAL"]) + len(metrics["TRANSITION"])):
			if metrics["TRANSITION"][index]["OBJECTIVE"] == "MAXIMIZATION":
				directions.append(local_platypus.Problem.MAXIMIZE)
			else:
				directions.append(local_platypus.Problem.MINIMIZE)
			for policy in metrics["TRANSITION"][index]["POLICIES"]:
				self.__policies["EQUATION"].append(policy)
				self.__policies["INDEX"].append(index)
		self.__policies["EQUATION"].append("==0")

		#Initializing problem [(dimensions, objectives)])
		super(ServiceMapping, self).__init__(len(service["STRUCTURE"]), len(metrics["LOCAL"]) + len(metrics["TRANSITION"]), len(self.__policies["EQUATION"]))

		#Initializing candidate domains [from 0 to domain n-1 -- for all dimension]
		self.types[:] = [local_platypus.Integer(0, len(domains)-1)] * len(service["STRUCTURE"])

		#Initializing directions
		self.directions[:] = directions

		#Initializing constraints
		self.constraints[:] = self.__policies["EQUATION"]

		#Initializing processing data
		self.__metrics = metrics
		self.__service = service
		self.__domains = domains

		#Create the penalty vector
		self.__penalty()

		#Create the taboo list and initialize taboo generator
		self.__taboo = [[], []]
		self.__generator = generator

		#Status updated to "ready to process"
		self.__status = 1


	def evaluate(self, solution):
		candidate = solution.variables[:]
		
		if candidate in self.__taboo[0]:
			solution.variables[:] = self.__generator.substitute()
			candidate = solution.variables[:]

		if candidate in self.__taboo[1]:
			self.__adjust(candidate)

		evaluation = [0] * (len(self.__metrics["LOCAL"]) + len(self.__metrics["TRANSITION"]))
		constraints = []
		computation = [{"MEMORY":0, "VCPU":0, "IFACES":0} for index in range(len(self.__domains))]

		for index in range(len(candidate)):

			for resource in computation[0]:
				computation[candidate[index]][resource] += self.__service["FUNCTION"][self.__service["STRUCTURE"][index][0]][resource]
				if computation[candidate[index]][resource] > self.__domains[candidate[index]]["RESOURCE"][resource]:
					solution.objectives[:] = self.__penalize
					solution.constraints[:] = self.__policies["INDEX"] + [1]
					self.__taboo[1].append(candidate)
					return

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
					solution.objectives[:] = self.__penalize
					solution.constraints[:] = self.__policies["INDEX"] + [2]
					self.__taboo[0].append(candidate)
					return

				if meanDictionary == None:
					meanDictionary = copy.copy(self.__domains[candidate[connection]]["TRANSITION"][candidate[index]])
				else:
					for metric in self.__metrics["TRANSITION"]:
						meanDictionary[metric] += self.__domains[candidate[connection]]["TRANSITION"][candidate[index]][metric]

			for metric in self.__metrics["TRANSITION"]:
				evaluation[metric] += meanDictionary[metric] / meanFactor

		solution.objectives[:] = evaluation
		for policy in self.__policies["INDEX"]:
			constraints.append(evaluation[policy])
		solution.constraints[:] = constraints + [0]


	def getStatus(self):
		return self.__status


	def getPenalize(self):
		return self.__penalize

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
	__domains = None
	__feedback = []

	def __translate(self, result):
		translator = local_platypus.Integer(0, len(self.__request.getDomains())-1)
		domainDict = self.__request.getDomainDictionary()
		metricDict = self.__request.getMetricDictionary()

		for index in range(len(result[0])):
			for domain in range(len(result[0][index])):
				result[0][index][domain] = domainDict[translator.decode(result[0][index][domain])]

			values = {}
			for metric in range(len(metricDict)):
				values[metricDict[metric]] = result[1][index][metric]
			result[1][index] = values


	def __pareto(self, aggregations):

		aggregations = numpy.array(aggregations)
		i_dominates_j = numpy.all(aggregations[:,None] >= aggregations, axis=-1) & numpy.any(aggregations[:,None] > aggregations, axis=-1)
		remaining = numpy.arange(len(aggregations))
		fronts = numpy.empty(len(aggregations), int)
		frontier_index = 0

		while remaining.size > 0:
			dominated = numpy.any(i_dominates_j[remaining[:,None], remaining], axis=0)
			fronts[remaining[~dominated]] = frontier_index
			remaining = remaining[dominated]
			frontier_index += 1

		return fronts.tolist()


	def __refine(self, results):

		aggregations = []
		for step in results:
			for data in step[1]:
				include = []
				keys = list(data.keys())
				keys.sort()
				for metric in keys:
					include.append(data[metric])
				aggregations.append(include)
		pareto = self.__pareto(aggregations)

		for step in results:
			step.append(pareto[:len(step[0])])
			pareto = pareto[len(step[0]):]

		completeList = [[], []]
		for step in range(len(results)):
			for candidate in range(len(results[step][0])):
				if not results[step][0][candidate] in completeList[0]:
					completeList[0].append(results[step][0][candidate])
					completeList[1].append(results[step][1][candidate])
					completeList[1][-1]["PARETO"] = results[step][2][candidate]
					completeList[1][-1]["MEAN_PARETO"] = str(statistics.mean(results[step][2])).replace(".", ",")
					completeList[1][-1]["MAX_PARETO"] = str(max(results[step][2]))
					completeList[1][-1]["MIN_PARETO"] = str(min(results[step][2]))
					completeList[1][-1]["STEP"] = step

		return completeList


	def __update_feedback(self, final, percentage):

		for genome in final[0]:
			self.__feedback.append([int(gene) for gene in genome])
			if len(self.__feedback) == int(self.__algorithm.population_size * percentage):
				break
		if len(self.__feedback) < int(self.__algorithm.population_size * percentage):
			general = [[], []]
			raw = []
			for solution in self.__algorithm.result:
				if not solution.variables in final[0] and solution.feasible:
					general[0].append(copy.deepcopy(solution.variables))
					general[1].append(copy.deepcopy(solution.objectives))
			self.__translate(general)
			for objectives in general[1]:
				raw.append(list(objectives.values()))
			frontiers = self.__pareto(raw)
			for front in range(max(frontiers)):
				indexes = [i for i,v in enumerate(frontiers) if v==front]
				for choosen in indexes:
					self.__feedback.append([int(gene) for gene in general[0][choosen]])
					if len(self.__feedback) == int(self.__algorithm.population_size * percentage):
						break
				if len(self.__feedback) == int(self.__algorithm.population_size * percentage):
						break


	def __update_problem_agressive(self, final, changes):

		counter = {}
		for genome in final[0]:
			for gene in genome:
				if gene in counter:
					counter[gene] += 1
				else:
					counter[gene] = 1
		counter = [(k, v) for k, v in counter.items()]
		counter.sort(key = lambda x: x[1])
		
		for index in range(changes):
			selected = counter.pop()
			self.__domains[int(selected[0])]["LOCAL"][0] = int(self.__domains[int(selected[0])]["LOCAL"][0] / 2)
			if len(selected) == 0:
				break

		search = {x:list(self.__domains[x]["TRANSITION"].keys()) for x in list(self.__domains.keys())}
		generation = local_platypus.operators.FeedbackMechanismGenerator(search, self.__request.getService()["DEPENDENCY"], self.__feedback)
		self.__problem = ServiceMapping(self.__request.getMetrics(), self.__request.getService(), self.__domains, generation)

		if str(self.__algorithm.__class__.__name__) == "SPEA2":
			self.__algorithm = local_platypus.SPEA2(self.__problem, population_size = self.__algorithm.population_size, generator = self.__algorithm.generator, variator = self.__algorithm.variator)
		else:
			self.__algorithm = local_platypus.NSGAII(self.__problem, population_size = self.__algorithm.population_size, generator = self.__algorithm.generator, selector = self.__algorithm.selector, variator = self.__algorithm.variator)


	def __update_problem_normal(self, final, changes):

		genome = final[0][0]
		for index in range(changes):
			gene = random.randrange(len(genome))
			self.__domains[int(gene)]["LOCAL"][0] = int(self.__domains[int(gene)]["LOCAL"][0] / 2)

		search = {x:list(self.__domains[x]["TRANSITION"].keys()) for x in list(self.__domains.keys())}
		generation = local_platypus.operators.FeedbackMechanismGenerator(search, self.__request.getService()["DEPENDENCY"], self.__feedback)
		self.__problem = ServiceMapping(self.__request.getMetrics(), self.__request.getService(), self.__domains, generation)

		if str(self.__algorithm.__class__.__name__) == "SPEA2":
			self.__algorithm = local_platypus.SPEA2(self.__problem, population_size = self.__algorithm.population_size, generator = self.__algorithm.generator, variator = self.__algorithm.variator)
		else:
			self.__algorithm = local_platypus.NSGAII(self.__problem, population_size = self.__algorithm.population_size, generator = self.__algorithm.generator, selector = self.__algorithm.selector, variator = self.__algorithm.variator)


	def __init__(self, request, algorithm, population, tournament, crossover, crossoverProbability, mutation, mutationProbability):

		self.__request = RequestProcessor(request)
		self.__status = self.__request.getStatus()
		if self.__status != 1:
			return

		if population < 1:
			self.__status = -39
			return
		if tournament < 2 or tournament > population:
			self.__status = -40
			return
		if not crossover in ["SBX", "HUX", "PMX", "SSX"]:
			self.__status = -41
			return
		if crossoverProbability <= 0 or crossoverProbability > 1:
			self.__status = -42
			return
		if not mutation in ["FLIP", "SWAP"]:
			self.__status = -43
			return
		if mutationProbability <= 0 or mutationProbability > 1:
			self.__status = -44
			return

		if crossover == "SBX":
			crossover = local_platypus.operators.SBX(probability = float(crossoverProbability))
		elif crossover == "HUX":
			crossover = local_platypus.operators.HUX(probability = float(crossoverProbability))
		elif crossover == "PMX":
			crossover = local_platypus.operators.PMX(probability = float(crossoverProbability))
		elif crossover == "SSX":
			crossover = local_platypus.operators.SSX(probability = float(crossoverProbability))

		mutationConstraints = [constraint[0] for constraint in self.__request.getService()["DEPENDENCY"]]
		if mutation == "FLIP":
			mutation = local_platypus.operators.ConstrainedBitFlip(probability = float(mutationProbability), constraints = mutationConstraints)
		elif mutation == "SWAP":
			mutation = local_platypus.operators.ConstrainedBitSwap(probability = float(mutationProbability), constraints = mutationConstraints)

		self.__domains = self.__request.getDomains()
		search = {x:list(self.__domains[x]["TRANSITION"].keys()) for x in list(self.__domains.keys())}
		generation = local_platypus.operators.FeedbackMechanismGenerator(search, self.__request.getService()["DEPENDENCY"], self.__feedback)

		self.__problem = ServiceMapping(self.__request.getMetrics(), self.__request.getService(), self.__request.getDomains(), generation)
		if local_platypus.Problem.MAXIMIZE in self.__problem.directions and algorithm == "NSGA2":
			print("\nPlaty.pus library does not support maximization problems with NSGAII - Algorithm changed to SPEA2!!\n")
			algorithm = "SPEA2"

		if algorithm == "NSGA2":
			self.__algorithm = local_platypus.NSGAII(self.__problem, population_size = population, generator = generation, selector = local_platypus.operators.TournamentSelector(tournament), variator = local_platypus.operators.GAOperator(crossover, mutation))
		elif algorithm == "SPEA2":
			self.__algorithm = local_platypus.SPEA2(self.__problem, population_size = population, generator = generation, selector = local_platypus.operators.TournamentSelector(tournament, dominance = local_platypus.core.AttributeDominance(local_platypus.core.fitness_key)), variator = local_platypus.operators.GAOperator(crossover, mutation))
		else:
			self.__status = -45


	def execute(self, iterations):

		if self.__status != 1 and (self.__status > -30 and self.__status < 0):
			return self.__status

		if not isinstance(iterations, int):
			self.__status = -46
			return -46

		if iterations < 1:
			self.__status = -47
			return -47

		self.__algorithm.run(iterations)
		final = [[], []]
		nondominated = local_platypus.nondominated(self.__algorithm.result)

		for solution in nondominated:
			if not solution.variables in final[0] and solution.feasible:
				final[0].append(solution.variables)
				final[1].append(solution.objectives)
		self.__translate(final)

		return final    	

	def experiment(self, step, iterations, problem_update, feedback_mechanism):

		if self.__status != 1 and (self.__status > -30 and self.__status < 0):
			return self.__status

		if not isinstance(step, int):
			self.__status = -46
			return -46

		if step < 1:
			self.__status = -47
			return -47
		
		last = []
		results = []
		index = 0
		while True:
			if problem_update != None:
				self.__algorithm.nfe = False #Initial population reset (Tests #1, #2 , and #3)
			index += 1
			self.__algorithm.run(step)
			final = [[], []]
			nondominated = local_platypus.nondominated(self.__algorithm.result)

			for solution in nondominated:
				if not solution.variables in final[0] and solution.feasible:
					final[0].append(copy.deepcopy(solution.variables))
					final[1].append(copy.deepcopy(solution.objectives))
			self.__translate(final)
			
			if feedback_mechanism != None:
				self.__update_feedback(final, feedback_mechanism)
			if problem_update != None:
				if problem_update > len(self.__domains):
					print("ERROR: PROBLEM UPDATE SIZE NOT ALLOWED!!\n")
					exit()
				self.__update_problem_normal(final, problem_update) #Standard update, degrades the first local metric by 0.5
			
			check = copy.deepcopy(final[0])
			check.sort()

			if last == check:
				break
			last = check
			
			results.append(final)
			
			if index*step >= iterations:
				break

		return self.__refine(results)


	def getStatus(self):
		return self.__status

##------##------##------##------##-----##-----##-----##------##------##------##

def usage():

	print("================== Genetic Service Mapping (GeSeMa) ==================")
	print("USAGE: *.py request_file [FLAGS]")
	print("FLAGS: ")
	print("\t-a algorithm_name: SPEA2 || NSGA2 (std: SPEA2)")
	print("\t-p population_size: 0 < population_size < +n (std: 50)")
	print("\t-t tournament_size: 0 < tournament_size <= population_size (std: 2)")
	print("\t-c crossover_technique: SBX || HUX || PMX || SSX (std: SBX)")
	print("\t-cp crossover_probability: 0 <= crossover_probability <= 1 (std: 1)")
	print("\t-m mutation_technique: FLIP || SWAP (std: FLIP)")
	print("\t-mp mutation_probability: 0 <= crossover_probability <= 1 (std: 0.1)")
	print("\t-g generations: 0 < generations < +n (std:1000)")
	print("\t\t-s step_generations: 0 < step_generations < +n (for experimentation, uses -g to maximum)")
	print("\t\t\t-pu problem_update: 0 <= problem_update < number_of_domains")
	print("\t\t\t-fm feedback_percentage: 0 < feedback_percentage <= 1")
	print("\t-o output: output file name (std: None)")
	print("======================================================================")


a = "SPEA2"
p = 50
t = 2
c = "SBX"
cp = 1.0
m = "FLIP"
mp = 0.1
g = 1000
s = None
pu = None
fm = None
o = None

if len(sys.argv) < 2 or len(sys.argv)%2 != 0:
	usage()
	exit()

if not os.path.isfile(sys.argv[1]):
	print("ERROR: FILE DOES NOT EXISTS!!\n")
	exit()

for flag in range(2, len(sys.argv), 2):
	
	if sys.argv[flag] == "-a":
		a = sys.argv[flag + 1]
		continue
	if sys.argv[flag] == "-p":
		if not sys.argv[flag + 1].isdigit() or sys.argv[flag + 1] == "0":
			print("ERROR: POPULATION SIZE NOT ALLOWED!!\n")
			exit()
		p = int(sys.argv[flag + 1])
		continue
	if sys.argv[flag] == "-t":
		if not sys.argv[flag + 1].isdigit() or sys.argv[flag + 1] == "0":
			print("ERROR: TOURNAMENT SIZE NOT ALLOWED!!\n")
			exit()
		t = int(sys.argv[flag + 1])
		continue
	if sys.argv[flag] == "-c":
		c = sys.argv[flag + 1]
		continue
	if sys.argv[flag] == "-cp":
		try:
			cp = float(sys.argv[flag + 1])
		except ValueError:
			print("ERROR: CROSSOVER PROBABILITY NOT ALLOWED!!")
			exit()
		continue
	if sys.argv[flag] == "-m":
		m = sys.argv[flag + 1]
		continue
	if sys.argv[flag] == "-mp":
		try:
			mp = float(sys.argv[flag + 1])
		except ValueError:
			print("ERROR: MUTATION PROBABILITY NOT ALLOWED!!")
			exit()
		continue
	if sys.argv[flag] == "-g":
		if not sys.argv[flag + 1].isdigit() or sys.argv[flag + 1] == "0":
			print("ERROR: NUMBER OF GENERATIONS NOT ALLOWED!!\n")
			exit()
		g = int(sys.argv[flag + 1])
		continue
	if sys.argv[flag] == "-s":
		if not sys.argv[flag + 1].isdigit() or sys.argv[flag + 1] == "0":
			print("ERROR: STEP SIZE NOT ALLOWED!!\n")
			exit()
		s = int(sys.argv[flag + 1])
		continue
	if sys.argv[flag] == "-pu":
		if not sys.argv[flag + 1].isdigit():
			print("ERROR: PROBLEM UPDATE SIZE NOT ALLOWED!!\n")
			exit()
		if not "-s" in sys.argv:
			print("ERROR: -pu OPTION REQUIRES -s OPTION!!\n")
			exit()
		pu = int(sys.argv[flag + 1])
		continue
	if sys.argv[flag] == "-fm":
		if not "-s" in sys.argv:
			print("ERROR: -fm OPTION REQUIRES -s OPTION!!\n")
			exit()
		try:
			fm = float(sys.argv[flag + 1])
			if fm < 0 or fm > 1:
				print("ERROR: FEEDBACK PERCENTAGE NOT ALLOWED!!\n")
				exit()
		except ValueError:
			print("ERROR: FEEDBACK PERCENTAGE NOT ALLOWED!!\n")
			exit()
		continue
	if sys.argv[flag] == "-o":
		o = sys.argv[flag + 1]
		continue
	print("ERROR: INVALID FLAG "+ sys.argv[flag])
	exit()

processor = Mapping(sys.argv[1], a, p, t, c, cp, m, mp)
if s == None:
	result = processor.execute(g)
else:
	result = processor.experiment(s, g, pu, fm)

if o != None:
	file = open(o, "w+")
	file.write("MAPPING;")
	if len(result[0]) > 0:
		for metric in result[1][0]:
			file.write(metric + ";")
	file.write("\n")

	for index in range(len(result[0])):
		file.write(str(result[0][index]) + ";")
		for metric in result[1][index]:
			file.write(str(result[1][index][metric]) + ";")
		file.write("\n")
