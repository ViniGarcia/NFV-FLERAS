import os
import yaml
import platypus

##------##------##------##------ REQUEST PARSER CLASS ------##------##------##------##
#NAME: RequestProcessor
#OBJECTIVE: Validates the YAML request document and organizes it to be processed by the
#			multu-objective genetic algorithm.
#STATUS CODES: 
#		0 -> Not evaluated yet
#		1 -> Succesfully evaluated
#		-1 to -30 -> Error

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
				if not policy[0] in ["=", ">", "<", ">=", "<="]:
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
			if member == "IN" or str.startswith(member, "EN"):
				continue
			if not member in requestYAML["SERVICE"]["FUNCTION"]:
				return -20

		for member in requestYAML["SERVICE"]["FUNCTION"]:
			if not member in requestYAML["SERVICE"]["TOPOLOGY"]:
				return -21

		if not isinstance(requestYAML["DOMAINS"], dict):
			return -22

		for member in requestYAML["SERVICE"]["FUNCTION"]:
			if not isinstance(requestYAML["SERVICE"]["FUNCTION"][member], dict):
				return -23
			if not "MEMORY" in requestYAML["SERVICE"]["FUNCTION"][member] or not "VCPU" in requestYAML["SERVICE"]["FUNCTION"][member] or not "IFACES" in requestYAML["SERVICE"]["FUNCTION"][member]:
				return -24
			if not isinstance(requestYAML["SERVICE"]["FUNCTION"][member]["MEMORY"], int) or not isinstance(requestYAML["SERVICE"]["FUNCTION"][member]["VCPU"], int) or not isinstance(requestYAML["SERVICE"]["FUNCTION"][member]["IFACES"], int):
				return -25
			if requestYAML["SERVICE"]["FUNCTION"][member]["MEMORY"] < 0 or requestYAML["SERVICE"]["FUNCTION"][member]["VCPU"] < 0 or requestYAML["SERVICE"]["FUNCTION"][member]["IFACES"] < 0:
				return -26

		for member in requestYAML["DOMAINS"]:
			if not isinstance(requestYAML["DOMAINS"][member], dict):
				return -27
			if not "RESOURCE" in requestYAML["DOMAINS"][member] or not "LOCAL" in requestYAML["DOMAINS"][member] or not "TRANSITION" in requestYAML["DOMAINS"][member]:
				return -28
			if not "MEMORY" in requestYAML["DOMAINS"][member]["RESOURCE"] or not "VCPU" in requestYAML["DOMAINS"][member]["RESOURCE"] or not "IFACES" in requestYAML["DOMAINS"][member]["RESOURCE"]:
				return -29
			if not isinstance(requestYAML["DOMAINS"][member]["RESOURCE"]["MEMORY"], int) or not isinstance(requestYAML["DOMAINS"][member]["RESOURCE"]["VCPU"], int) or not isinstance(requestYAML["DOMAINS"][member]["RESOURCE"]["IFACES"], int):
				return -30
			if requestYAML["DOMAINS"][member]["RESOURCE"]["MEMORY"] < 0 or requestYAML["DOMAINS"][member]["RESOURCE"]["VCPU"] < 0 or requestYAML["DOMAINS"][member]["RESOURCE"]["IFACES"] < 0:
				return -31

			for metric in requestYAML["DOMAINS"][member]["LOCAL"]:
				if not metric in requestYAML["METRICS"]["LOCAL"]:
					return -32
				if not isinstance(requestYAML["DOMAINS"][member]["LOCAL"][metric], int) and not isinstance(requestYAML["DOMAINS"][member]["LOCAL"][metric], float):
					return -33

			for metric in requestYAML["METRICS"]["LOCAL"]:
				if not metric in requestYAML["DOMAINS"][member]["LOCAL"]:
					return -34

			for domain in requestYAML["DOMAINS"][member]["TRANSITION"]:
				if not domain in requestYAML["DOMAINS"]:
					return -35

				for metric in requestYAML["DOMAINS"][member]["TRANSITION"][domain]:
					if not metric in requestYAML["METRICS"]["TRANSITION"]:
						return -36
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

		functions = []
		for index in range(len(self.__service["TOPOLOGY"])):
			if self.__service["TOPOLOGY"][index] in self.__service["FUNCTION"]:
				functions.append((self.__service["TOPOLOGY"][index], index))

		self.__service["STRUCTURE"] = functions

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

class ServiceMapping(platypus.Problem):

	__status = 0
	__metrics = None
	__service = None
	__domains = None
	
	__penalize = None


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


	def __init__(self, metrics, service, domains):
		#Initializing problem [(dimensions, objectives)])
		super(ServiceMapping, self).__init__(len(service["STRUCTURE"]), len(metrics["LOCAL"]) + len(metrics["TRANSITION"]))
		#Initializing candidate domains [from 0 to domain n-1 -- for all dimension] 
		self.types[:] = [platypus.Integer(0, len(domains)-1)] * len(service["STRUCTURE"])
		#Initializing problem directions
		directions = []
		for index in range(len(metrics["LOCAL"])):
			if metrics["LOCAL"][index] == "MAXIMIZATION":
				directions.append(platypus.Problem.MAXIMIZE)
			else:
				directions.append(platypus.Problem.MINIMIZE)
		for index in range(len(metrics["LOCAL"]), len(metrics["LOCAL"]) + len(metrics["TRANSITION"])):
			if metrics["TRANSITION"][index] == "MAXIMIZATION":
				directions.append(platypus.Problem.MAXIMIZE)
			else:
				directions.append(platypus.Problem.MINIMIZE)
		self.directions[:] = directions
		#Initializing processing data
		self.__metrics = metrics
		self.__service = service
		self.__domains = domains
		#Create the penalty vector
		self.__penalty()
		#Status updated to "ready to process"
		self.__status = 1
    

	def evaluate(self, solution):
		candidate = solution.variables[:]

		evaluation = [0] * (len(self.__metrics["LOCAL"]) + len(self.__metrics["TRANSITION"]))
		computation = [{"MEMORY":0, "VCPU":0, "IFACES":0} for index in range(len(self.__domains))]

		for index in range(len(candidate)):

			for resource in computation[0]:
				computation[candidate[index]][resource] += self.__service["FUNCTION"][self.__service["STRUCTURE"][index][0]][resource]
				if computation[candidate[index]][resource] > self.__domains[candidate[index]]["RESOURCE"][resource]:
					solution.objectives[:] = self.__penalize
					return

			for metric in self.__metrics["LOCAL"]:
				evaluation[metric] += self.__domains[candidate[index]]["LOCAL"][metric]

			if index == 0 or candidate[index] == candidate[index-1]:
				continue

			if not candidate[index] in self.__domains[candidate[index-1]]["TRANSITION"]:
				solution.objectives[:] = self.__penalize
				return

			for metric in self.__metrics["TRANSITION"]:
				evaluation[metric] += self.__domains[candidate[index-1]]["TRANSITION"][candidate[index]][metric]

		solution.objectives[:] = evaluation


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

	def __init__(self, request, algorithm, population, tournament, crossover, crossoverProbability):

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

		if crossover == "SBX":
			crossover = platypus.operators.SBX(probability = float(crossoverProbability))
		elif crossover == "HUX":
			crossover = platypus.operators.HUX(probability = float(crossoverProbability))
		elif crossover == "PMX":
			crossover = platypus.operators.PMX(probability = float(crossoverProbability))
		elif crossover == "SSX":
			crossover = platypus.operators.SSX(probability = float(crossoverProbability))

		self.__problem = ServiceMapping(self.__request.getMetrics(), self.__request.getService(), self.__request.getDomains())
		if platypus.Problem.MAXIMIZE in self.__problem.directions and algorithm == "NSGA2":
			print("\nPlaty.pus library does not support maximization problems with NSGAII - Algorithm changed to SPEA2!!\n")
			algorithm = "SPEA2"

		if algorithm == "NSGA2":
			self.__algorithm = platypus.NSGAII(self.__problem, population_size = population, selector = platypus.operators.TournamentSelector(tournament), variator = crossover)
		elif algorithm == "SPEA2":
			self.__algorithm = platypus.SPEA2(self.__problem, population_size = population, selector = platypus.operators.TournamentSelector(tournament, dominance=platypus.core.AttributeDominance(platypus.core.fitness_key)), variator = crossover)
		else:
			self.__status = -43

	def execute(self, iterations):

		if self.__status != 1 and (self.__status > -30 and self.__status < 0):
			return self.__status

		if not isinstance(iterations, int):
			self.__status = -44
			return -44

		if iterations < 1:
			self.__status = -45
			return -45

		self.__algorithm.run(iterations)

		final = [[], []]
		nondominated = platypus.nondominated(self.__algorithm.result)
		if str(nondominated[0].objectives) == str(self.__problem.getPenalize()):
			return final

		for solution in nondominated:
			if not solution.variables in final[0]:
				final[0].append(solution.variables)
				final[1].append(solution.objectives)
		return final

##------##------##------##------##-----##-----##-----##------##------##------##

test = Mapping("Request.yaml", "NSGA2", 100, 2, "SBX", 1)
result = test.execute(100)

for index in range(len(result[0])):
	print(result[0][index])
	print(result[1][index])
	print("----")

#Improvement -> enable the specification of generic topologies
#Improvement -> enable the specification of domain dependencies
#Improvement -> enbale the spefication of constraints