import copy

class gesema_greedy:

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


	def __dependencies(self, search, dependencies):

		constraints = {}
		for dependency in dependencies:

			constraints[dependency[0]] = [dependency[1], []]
			for domain in search:
				if dependency[1] in search[domain]:
					constraints[1][dependency[0]].append(domain)	

		return constraints

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
			return True

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

		aggregations = [0.0] * len(options)

		for origin in ["LOCAL", "TRANSITION"]:
			metrics = list(self.__metrics[origin].keys())
			for parameter in range(len(metrics)):
				partial = [candidate[1][parameter] for candidate in options]
				aMax, aMin = max(partial), min(partial)
				if self.__metrics[origin][metrics[parameter]]["OBJECTIVE"] == "MAXIMIZATION":
					for index in range(len(partial)):
						if aMax != aMin:
							aggregations[index] += float(aMax - partial[index]) / float(aMax - aMin)
				else:
					aMin = min(partial)
					for index in range(len(partial)):
						if aMax != aMin:
							aggregations[index] = float(partial[index] - aMin) / float(aMax - aMin)

		return aggregations.index(min(aggregations))


	def execute(self):

		accepted = [[],[]]
		search = {x:list(self.__domains[x]["TRANSITION"].keys()) for x in list(self.__domains.keys())}
		for domain in search:
			search[domain].append(domain)

		constraints = self.__dependencies(search, self.__service["DEPENDENCY"])
		if 0 in constraints:
			if 1 in constraints:
				if not constraints[0][0] in constraints[1][1]:
					return accepted
			start = [constraints[0][0]]
		else:
			if 1 in constraints:
				start = constraints[1][1]
			else:
				start = range(len(self.__domains))

		for initial in start:
			current = [initial]
			evaluation = [0] * (len(self.__metrics["LOCAL"]) + len(self.__metrics["TRANSITION"]))
			computation = [{"MEMORY":0, "VCPU":0, "IFACES":0} for index in range(len(self.__domains))]
			found = True

			if not self.__evaluate(current, 0, evaluation, computation):
				continue

			while len(current) < len(self.__service["FUNCTION"]):

				saveEvaluation = copy.deepcopy(evaluation)
				saveComputation = copy.deepcopy(computation)
				greedyOptions = []

				if len(current) in constraints:
					valid = self.__evaluate(current + [domain], len(current), evaluation, computation)
					if not valid:
						found = False
						break
					current.append(constraints[len(current)][0])
					continue

				if len(current)+1 in constraints:
					iterate = set(search[current[-1]]).intersection(constraints[len(current)+1][1])
				else:
					iterate = search[current[-1]] 

				for domain in iterate:
					valid = self.__evaluate(current + [domain], len(current), evaluation, computation)
					if not valid:
						continue
					greedyOptions.append((domain, evaluation, computation))
					evaluation = copy.deepcopy(saveEvaluation)
					computation = copy.deepcopy(saveComputation)

				if len(greedyOptions) == 0:
					found = False
					break
				
				index = self.__choose(greedyOptions)
				current.append(greedyOptions[index][0])
				evaluation = greedyOptions[index][1]
				computation = greedyOptions[index][2]

			if not found:
				continue

			accepted[0].append(current)
			accepted[1].append(evaluation)

		return accepted


	def getStatus(self):
		return self.__status