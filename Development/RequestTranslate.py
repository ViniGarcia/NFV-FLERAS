import yaml

class RequestTranslate:

	__yamlData = None
	__domainsPart = None
	__servicePart = None


	def __translateDomains(self):

		self.__domainsPart = {"DOMAINS":None, "RESOURCES":None, "LOCAL":None, "TRANSITION":None}
		self.__domainsPart["DOMAINS"] = list(self.__yamlData["DOMAINS"].keys())
		self.__domainsPart["RESOURCES"] = {}
		self.__domainsPart["LOCAL"] = []
		self.__domainsPart["TRANSITION"] = []

		localDict = {}
		transDict = {}
		for domain in self.__domainsPart["DOMAINS"]:
			self.__domainsPart["RESOURCES"][domain] = {"MEMORY":self.__yamlData["DOMAINS"][domain]["RESOURCE"]["MEMORY"], "NET_IFACES":self.__yamlData["DOMAINS"][domain]["RESOURCE"]["IFACES"], "CPUS":self.__yamlData["DOMAINS"][domain]["RESOURCE"]["VCPU"]}

			for metric in self.__yamlData["DOMAINS"][domain]["LOCAL"]:
				if not metric in localDict:
					self.__domainsPart["LOCAL"].append({"ID":metric})
					localDict[metric] = self.__domainsPart["LOCAL"][-1]
				localDict[metric][domain] = self.__yamlData["DOMAINS"][domain]["LOCAL"][metric]

			for transition in self.__yamlData["DOMAINS"][domain]["TRANSITION"]:
				for metric in self.__yamlData["DOMAINS"][domain]["TRANSITION"][transition]:
					if not metric in list(transDict.keys()):
						self.__domainsPart["TRANSITION"].append({"ID":metric})
						transDict[metric] = self.__domainsPart["TRANSITION"][-1]
					if not domain in transDict[metric]:
						transDict[metric][domain] = {}

					transDict[metric][domain][transition] = self.__yamlData["DOMAINS"][domain]["TRANSITION"][transition][metric]


	def __translateService(self, identifier):

		self.__servicePart = {"METADATA":{"ID":identifier, "DESCRIPTION": "Just a description..."}, "SERVICE":{}, "POLICIES":{"IMMEDIATE":[], "AGGREGATE":[]}, "DEPLOYMENT":{}}
		self.__servicePart["SERVICE"]["TOPOLOGY"] = " ".join(self.__yamlData["SERVICE"]["TOPOLOGY"])
		self.__servicePart["SERVICE"]["OELEMENTS"] = list(self.__yamlData["SERVICE"]["FUNCTION"].keys())
		self.__servicePart["SERVICE"]["OUTNODES"] = []

		for element in self.__yamlData["SERVICE"]["TOPOLOGY"]:
			if not element in self.__servicePart["SERVICE"]["OELEMENTS"] + ["IN", "{", "/", "}"]:
				if not element.startswith("<"):
					self.__servicePart["SERVICE"]["OUTNODES"].append(element)

		weight = 1/(len(self.__yamlData["METRICS"]["LOCAL"].keys()) + len(self.__yamlData["METRICS"]["TRANSITION"].keys()))
		for ptype in ["LOCAL", "TRANSITION"]:
			for metric in self.__yamlData["METRICS"][ptype]:
				self.__servicePart["POLICIES"]["AGGREGATE"].append({"ID":metric, "MIN":0, "MAX":100000000, "TYPE":"DOMAIN", "GOAL":self.__yamlData["METRICS"][ptype][metric]["OBJECTIVE"][:3], "WEIGHT":weight})
				for policy in self.__yamlData["METRICS"][ptype][metric]["POLICIES"]:
					if policy.startswith("<="):
						self.__servicePart["POLICIES"]["AGGREGATE"][-1]["MAX"] = int(policy.split(" ")[-1])
						continue
					if policy.startswith("<"):
						self.__servicePart["POLICIES"]["AGGREGATE"][-1]["MAX"] = int(policy.split(" ")[-1])-1
						continue
					if policy.startswith(">="):
						self.__servicePart["POLICIES"]["AGGREGATE"][-1]["MIN"] = int(policy.split(" ")[-1])
						continue
					if policy.startswith(">"):
						self.__servicePart["POLICIES"]["AGGREGATE"][-1]["MIN"] = int(policy.split(" ")[-1])+1
						continue
					if policy.startswith("=="):
						self.__servicePart["POLICIES"]["AGGREGATE"][-1]["MIN"] = int(policy.split(" ")[-1])
						self.__servicePart["POLICIES"]["AGGREGATE"][-1]["MAX"] = int(policy.split(" ")[-1])
						continue

		for function in self.__yamlData["SERVICE"]["FUNCTION"]:
			self.__servicePart["DEPLOYMENT"][function] = {"FLAVOUR":{}}
			self.__servicePart["DEPLOYMENT"][function]["FLAVOUR"]["MEMORY"] = self.__yamlData["SERVICE"]["FUNCTION"][function]["MEMORY"]
			self.__servicePart["DEPLOYMENT"][function]["FLAVOUR"]["CPUS"] = self.__yamlData["SERVICE"]["FUNCTION"][function]["VCPU"]
			self.__servicePart["DEPLOYMENT"][function]["FLAVOUR"]["NET_IFACES"] = self.__yamlData["SERVICE"]["FUNCTION"][function]["IFACES"]

	def __makeFiles(self, oRequest):

		domain = open(oRequest.split(".")[0] + "DOMAIN.yaml", "w+")
		domain.write(yaml.dump(self.__domainsPart))
		domain.close()
		service = open(oRequest.split(".")[0] + "SERVICE.yaml", "w+")
		service.write(yaml.dump(self.__servicePart))
		service.close()

	def __init__(self, oRequest):

		fRequest = open(oRequest, 'r')
		self.__yamlData = yaml.safe_load(fRequest)
		fRequest.close()

		self.__translateDomains()
		self.__translateService(oRequest)
		self.__makeFiles(oRequest)

test = RequestTranslate("test.yaml")