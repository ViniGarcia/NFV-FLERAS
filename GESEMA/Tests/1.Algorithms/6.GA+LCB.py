import collections
import networkx
import random
import math
import yaml
import sys
import os

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

	def getNetworkX(self):

		nxGraph = networkx.Graph()
		nxGraph.add_nodes_from([(nId, {**self.__domains[nId]["RESOURCE"], **self.__domains[nId]["LOCAL"]}) for nId in self.__domainDictionary])
		for nId in self.__domainDictionary:
			nxGraph.add_edges_from([(nId, nodeConn, {**self.__domains[nId]["TRANSITION"][nodeConn]}) for nodeConn in self.__domains[nId]["TRANSITION"]])

		return nxGraph

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

class GALCB:

	__mapRequest = None
	__graphNetX = None
	__constraintsTuple = None

	def __init__(self, requestFile):

		self.__mapRequest = RequestProcessor(requestFile)
		if self.__mapRequest.getStatus() < 0:
			print("ERROR: INVALID REQUEST PROVIDED (REQ. ERROR CODE " + str(self.__mapRequest.getStatus()) + ")")
			exit()
		self.__graphNetX = self.__mapRequest.getNetworkX()

		for key, value in self.__mapRequest.getMetricDictionary().items():
			if value == "DELAY":
				delayPolicy = key
			elif value == "RELIABILITY":
				reliabilityPolicy = key
			elif value == "BANDWIDTH":
				bandwidthPolicy = key
			elif value == "LINKS":
				linksPolicy = key

		serviceMetrics = self.__mapRequest.getMetrics()
		delayValue = serviceMetrics["TRANSITION"][delayPolicy]["POLICIES"][0]
		for index in range(len(delayValue)):
			try:
				int(delayValue[index])
			except:
				continue
			break
		delayValue = float(delayValue[index:])
		reliabilityValue = serviceMetrics["LOCAL"][reliabilityPolicy]["POLICIES"][0]
		for index in range(len(reliabilityValue)):
			try:
				int(reliabilityValue[index])
			except:
				continue
			break
		reliabilityValue = float(reliabilityValue[index:])
		self.__constraintsTuple = ((delayPolicy, delayValue), (reliabilityPolicy, reliabilityValue), (bandwidthPolicy,), (linksPolicy,))
	
	def __binary_search(self, arr, x):
		low = 0
		high = len(arr) - 1
		
		while low <= high:
			mid = (high + low) // 2
			if arr[mid] < x:
				if arr[mid+1] > x:
					return mid+1
				low = mid + 1
			elif arr[mid] > x:
				if mid == 0 or arr[mid-1] < x:
					return mid
				high = mid - 1
			else:
				return mid

	def __checkConstraints(self, individual):

		candidateCheck = {}
		serviceData = self.__mapRequest.getService()
		serviceMetrics = self.__mapRequest.getMetrics()
		delayReliability = [0,1]

		for index in range(len(individual)):
			if not individual[index] in candidateCheck:
				candidateCheck[individual[index]] = self.__graphNetX.nodes[individual[index]].copy()
			candidateCheck[individual[index]]["IFACES"] -= serviceData["FUNCTION"][serviceData["STRUCTURE"][index][0]]["IFACES"]
			candidateCheck[individual[index]]["MEMORY"] -= serviceData["FUNCTION"][serviceData["STRUCTURE"][index][0]]["MEMORY"]
			candidateCheck[individual[index]]["VCPU"] -= serviceData["FUNCTION"][serviceData["STRUCTURE"][index][0]]["VCPU"]
			if candidateCheck[individual[index]]["IFACES"] < 0 or candidateCheck[individual[index]]["MEMORY"] < 0 or candidateCheck[individual[index]]["VCPU"] < 0:
				return False

			delayReliability[1] *= candidateCheck[individual[index]][self.__constraintsTuple[1][0]]
			if index != 0:
				if individual[index-1] != individual[index]:
					delayReliability[0] += self.__graphNetX[individual[index-1]][individual[index]][self.__constraintsTuple[0][0]]

		if self.__constraintsTuple[0][1] < delayReliability[0] or self.__constraintsTuple[1][1] > delayReliability[1]:
			return False

		for domain in set(individual):
			if individual.count(domain) > 2:
				return False

		return True

	def __evaluateIndividual(self, individual):
		
		cumulativeData = [self.__graphNetX.nodes[individual[0]][self.__constraintsTuple[3][0]], self.__graphNetX.nodes[individual[0]][self.__constraintsTuple[2][0]], self.__graphNetX.nodes[individual[0]][self.__constraintsTuple[1][0]], 0]
		for index in range(1, len(individual)):
			cumulativeData[0] += self.__graphNetX.nodes[individual[index]][self.__constraintsTuple[3][0]]
			cumulativeData[1] += self.__graphNetX.nodes[individual[index]][self.__constraintsTuple[2][0]]
			cumulativeData[2] *= self.__graphNetX.nodes[individual[index]][self.__constraintsTuple[1][0]]
			if individual[index] != individual[index-1]:
				cumulativeData[3] += self.__graphNetX[individual[index-1]][individual[index]][self.__constraintsTuple[0][0]]

		return cumulativeData

	def __evaluateGeneration(self, individualEvals):
		
		bestIndividual = 0
		attrWeights = [0.25, 0.25, 0.25, 0.25]
		maxMin = [[individualEvals[0][0], individualEvals[0][0]], [individualEvals[0][1], individualEvals[0][1]], [individualEvals[0][2], individualEvals[0][2]], [individualEvals[0][3], individualEvals[0][3]]]
		for index in range(1, len(individualEvals)):
			for attr in range(4):
				if individualEvals[index][attr] < maxMin[attr][0]:
					maxMin[attr][0] = individualEvals[index][attr]
				elif individualEvals[index][attr] > maxMin[attr][1]:
					maxMin[attr][1] = individualEvals[index][attr]

		for ie in range(len(individualEvals)):
			unifiedEval = 0
			for attr in range(3):
				if maxMin[attr][0] != maxMin[attr][1]:
					unifiedEval += (individualEvals[ie][attr] - maxMin[attr][0])/(maxMin[attr][1] - maxMin[attr][0]) * attrWeights[attr]
				else:
					unifiedEval += attrWeights[attr]
			if maxMin[3][0] != maxMin[3][1]:
				unifiedEval += (maxMin[3][1] - individualEvals[ie][3])/(maxMin[3][1] - maxMin[3][0]) * attrWeights[3]
			else:
				unifiedEval += attrWeights[3]
			individualEvals[ie].append(unifiedEval)

			if unifiedEval > individualEvals[bestIndividual][-1]:
				bestIndividual = ie

		return bestIndividual


	def __randomIndividual(self, originNode, destinyNode, nVNFs):
		
		while True:
			randomIndividual = [originNode]
			for index in range(nVNFs-2):
				possibilities = list(self.__graphNetX[randomIndividual[index]].keys())
				for attemps in range(len(possibilities)//10):
					chosenNode = random.choice(possibilities)
					if randomIndividual.count(chosenNode) < 2:
						break
				randomIndividual.append(chosenNode)
			if destinyNode in self.__graphNetX[randomIndividual[-1]]:
				randomIndividual.append(destinyNode)
				return randomIndividual

	def __initialPopulation(self, kPaths, nIndividuals, nVNFs):

		removePaths = []
		for kp in kPaths:
			if len(kp) > nIndividuals:
				removePaths.append(kp)
		for rp in removePaths:
			kPaths.pop(rp)
		if len(kPaths) == 0:
			print("NO ADEQUATE PATH TO INSTANTIATE THIS SERVICE IN THE NETWORK TOPOLOGY!!")
			exit()

		initialPopulation = []
		for kp in kPaths:
			for pki in range(math.ceil(nIndividuals/len(kPaths))):
				control = 0
				while control < 10:
					individual = kp.copy()
					randomGroup = list(range(len(individual)))
					
					for rf in range(nVNFs - len(individual)):
						rd = random.choice(randomGroup)	
						randomGroup.append(max(randomGroup)+1)
						randomGroup.pop(randomGroup.index(rd)+1)
						randomGroup.pop(randomGroup.index(rd))
						individual.insert(rd+1, individual[rd])

					if self.__checkConstraints(individual):
						initialPopulation.append(individual)
						break
					control += 1

		return initialPopulation

	def __partiallyNextGeneration(self, roulettedIndividuals, currentPopulation, currentEvals, bestGeneration):

		partialNextGeneration = []
		worstIndividual = [0, 1]

		for ri in roulettedIndividuals:
			if currentEvals[ri][-1] < worstIndividual[1]:
				worstIndividual[0] = len(partialNextGeneration)
				worstIndividual[1] = currentEvals[ri][-1]
			partialNextGeneration.append(currentPopulation[ri])

		if not bestGeneration in roulettedIndividuals:
			partialNextGeneration.pop(worstIndividual[0])
		else:
			partialNextGeneration.pop(partialNextGeneration.index(currentPopulation[bestGeneration]))
		partialNextGeneration.insert(0, currentPopulation[bestGeneration])

		return partialNextGeneration

	def __rouletteIndividuals(self, individualEvals, nChoices):

		individualSlots = [round(individualEvals[0][-1]*100)]
		for index in range(1, len(individualEvals)):
			individualSlots.append(round(individualEvals[0][-1]*100) + individualSlots[-1])
		
		individualChoices = []
		for nc in range(nChoices):
			choice = random.randint(1, individualSlots[-1])
			individualChoices.append(self.__binary_search(individualSlots, choice))

		return individualChoices

	def __crossoverIndividuals(self, firstIndividual, secondIndividual):
		
		for attempt in range(len(firstIndividual)//2):
			crossPoint = random.randint(1, len(firstIndividual)-1)
			if firstIndividual[crossPoint-1] in self.__graphNetX[secondIndividual[crossPoint]]:
				return firstIndividual[:crossPoint] + secondIndividual[crossPoint:]

		return firstIndividual

	def __mutateIndividual(self, individual):
		
		mutateIndividual = individual.copy()
		for attempPoint in range(2):
			mutatePoint = random.randint(1, len(individual)-2)
			mutateOptions = list(self.__graphNetX[individual[mutatePoint-1]].keys())
			for attemptDomain in range(len(mutateOptions) // 10):
				mutateDomain = mutateOptions[random.randint(0, len(mutateOptions)-1)]
				if individual[mutatePoint+1] in self.__graphNetX[mutateDomain]:
					mutateIndividual[mutatePoint] = mutateDomain
					return mutateIndividual

		return individual

	def __firstPart(self, originNode, destinyNode, kPaths, sLenght):
		#This function is desgined for GeSeMa paper experiment
		pathSize = math.ceil(sLenght/2)
		resultPaths = []
		for k in range(kPaths):
			for attemps in range(10):
				minimumSimplePath = [originNode]
				for p in range(pathSize-2):
					minimumSimplePath.append(random.choice(list(self.__graphNetX[minimumSimplePath[p]].keys())))
				if minimumSimplePath[-1] in self.__graphNetX[destinyNode]:
					minimumSimplePath.append(destinyNode)
					resultPaths.append(minimumSimplePath)
					break

		return resultPaths
		#return list(networkx.all_simple_paths(self.__graphNetX, originNode, destinyNode, math.ceil(sLenght/2)))[-kPaths:]
	
	def __secondPart(self, kPaths, nVNFs, nIndividuals, nGenerations, nConvergence, pMutation):
		
		currentPopulation = self.__initialPopulation(kPaths, nIndividuals, nVNFs)
		
		ng = 0 #number of generations
		nc = 0 #number of rounds with the same best candidate
		bestIndividual = [[], 0]
		while ng < nGenerations and nc < nConvergence:

			populationEval = []
			for individual in currentPopulation:
				populationEval.append(self.__evaluateIndividual(individual))
			bestGeneration = self.__evaluateGeneration(populationEval)
			if bestIndividual[0] == currentPopulation[bestGeneration]:
				bestIndividual[1] = bestGeneration
				nc += 1
			else:
				bestIndividual = [currentPopulation[bestGeneration], bestGeneration]
				nc = 0

			rouletteResults = self.__rouletteIndividuals(populationEval, nIndividuals//2)
			nextGeneration = self.__partiallyNextGeneration(rouletteResults, currentPopulation, populationEval, bestGeneration)
			
			populationLimit = len(currentPopulation)//2
			for index in range(populationLimit):
				nextGeneration.append(self.__crossoverIndividuals(currentPopulation[index], currentPopulation[index+populationLimit]))

			if len(nextGeneration) < nIndividuals:
				nextGeneration.append(self.__randomIndividual(currentPopulation[0][0], currentPopulation[0][-1], nVNFs))

			invalidIndividuals = []
			for index in range(1, len(nextGeneration)):
				if random.uniform(0.0,1.0) <= pMutation:
					nextGeneration[index] = self.__mutateIndividual(nextGeneration[index])
				if not self.__checkConstraints(nextGeneration[index]):
					invalidIndividuals.append(index)

			for ii in sorted(invalidIndividuals, reverse=True):
				nextGeneration.pop(ii)

			currentPopulation = nextGeneration
			ng += 1
		
		return (bestIndividual[0], self.__evaluateIndividual(bestIndividual[0]))

	def executeGALCB(self, originNode, destinyNode, kPaths, nIndividuals, nGenerations, nConvergence, pMutation):

		originId = -1
		destinyId = -1
		for key, value in self.__mapRequest.getDomainDictionary().items():
   			if value == originNode:
   				originId = key
   				if destinyId != -1:
   					break
   			elif value == destinyNode:
   				destinyId = key
   				if originId != -1:
   					break
		if originId == -1 or destinyId == -1:
   			print("ERROR: INVALID ORIGIN OR DESTINY NODE INFORMED!!")
   			exit()

		try:
			kPaths = int(kPaths)
		except:
   			print("ERROR: INVALID KPATHS VARIABLE TYPE (INT EXPECTED)!!")
   			exit()

		try: 
			nIndividuals = int(nIndividuals)
		except:
   			print("ERROR: INVALID NINDIVIDUALS VARIABLE TYPE (INT EXPECTED)!!")
   			exit()

		try:
			nGenerations = int(nGenerations)
		except:
   			print("ERROR: INVALID NGENERATIONS VARIABLE TYPE (INT EXPECTED)!!")
   			exit()

		try:
			nConvergence = int(nConvergence)
		except:
   			print("ERROR: INVALID NCONVERGENCE VARIABLE TYPE (INT EXPECTED)!!")
   			exit()

		try:
			pMutation = float(pMutation)
		except:
   			print("ERROR: INVALID PMUTATION VARIABLE TYPE (FLOAT EXPECTED)!!")
   			exit()

		if kPaths <= 0 or kPaths > nIndividuals:
   			print("ERROR: INVALID KPATHS VALUE (>0 & <=NINDIVIDUALS)")
   			exit()

		if nIndividuals <= 0:
   			print("ERROR: INVALID NINDIVIDUALS VALUE (>0)")
   			exit()

		if nConvergence <= 0:
   			print("ERROR: INVALID NCONVERGENCE VALUE (>0)")
   			exit()

		if pMutation < 0 or pMutation > 1:
   			print("ERROR: INVALID PMUTATION VALUE (>=0 & <=1)")
   			exit()

		nVNFs = len(self.__mapRequest.getService()["STRUCTURE"])
		initialPaths = self.__firstPart(originId, destinyId, kPaths, nVNFs)
		if len(initialPaths) == 0:
			print("ERROR: THE REQUEST COULD NOT BE SATISFIED -- THERE IS NO PATH (FIRST PART)")
			exit()

		finalResult = self.__secondPart(initialPaths, nVNFs, nIndividuals, nGenerations, nConvergence, pMutation)
		
		resultTranslator = self.__mapRequest.getDomainDictionary()
		translatedResult = []
		for cDomain in finalResult[0]:
			translatedResult.append(resultTranslator[cDomain])
		return (translatedResult, finalResult[1])

#========================================================= MAIN =========================================================

if len(sys.argv) < 16:
	print("ERROR: INVALID ARGMENTS (.py FILE -on STR -dn STR -kp INT -ni INT -ng INT -nc INT -mp FLOAT [-o STR])")
	exit()
if len(sys.argv) > 16 and len(sys.argv) != 18:
	print("ERROR: INVALID ARGMENTS (.py FILE -on STR -dn STR -kp INT -ni INT -ng INT -nc INT -mp FLOAT [-o STR])")
	exit()

f = sys.argv[1]

if sys.argv[2] == "-on":
	on = sys.argv[3]
else:
	print("ERROR: INVALID FLAG #1 (-on)")
	exit()

if sys.argv[4] == "-dn":
	dn = sys.argv[5]
else:
	print("ERROR: INVALID FLAG #2 (-dn)")
	exit()

if sys.argv[6] == "-kp":
	kp = sys.argv[7]
else:
	print("ERROR: INVALID FLAG #3 (-kp)")
	exit()

if sys.argv[8] == "-ni":
	ni = sys.argv[9]
else:
	print("ERROR: INVALID FLAG #4 (-ni)")
	exit()

if sys.argv[10] == "-ng":
	ng = sys.argv[11]
else:
	print("ERROR: INVALID FLAG #5 (-ng)")
	exit()

if sys.argv[12] == "-nc":
	nc = sys.argv[13]
else:
	print("ERROR: INVALID FLAG #6 (-nc)")
	exit()

if sys.argv[14] == "-mp":
	mp = sys.argv[15]
else:
	print("ERROR: INVALID FLAG #7 (-mp)")
	exit()

if len(sys.argv) > 16:
	if sys.argv[16] == "-o":
		o = sys.argv[17]
	else:
		print("ERROR: INVALID FLAG #8 (-o)")
		exit()
else:
	o = None

algorithmManager = GALCB(f)
algorithmResult = algorithmManager.executeGALCB(on, dn, kp, ni, ng, nc, 0.1)

if o == None:
	print("\n============== RESULT SUMMARY ==============")
	print("BEST CANDIDATE:", algorithmResult[0])
	print("\t-> BANDWIDTH:", algorithmResult[1][0])
	print("\t-> LINKS:", algorithmResult[1][1])
	print("\t-> RELIABILITY:", algorithmResult[1][2])
	print("\t-> DELAY:", algorithmResult[1][3])
	print("============================================")
else:
	resultFile = open(o, "w+")
	resultFile.write("MAPPING;BANDWIDTH;LINKS;RELIABILITY;DELAY;PARETO\n")
	resultFile.write(str(algorithmResult[0]) + ";" + str(algorithmResult[1][0]) + ";" + str(algorithmResult[1][1]) + ";" + str(algorithmResult[1][2]) + ";" + str(algorithmResult[1][3]) + ";0")