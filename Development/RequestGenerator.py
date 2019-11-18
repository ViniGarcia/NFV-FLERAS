import networkx
import copy
import random
import yaml

class RequestGenerator:

	__metrics = None
	__status = None

	def __defineObjectives(self):
		skeleton = {"METRICS": {"LOCAL":{}, "TRANSITION":{}}}

		for mtype in skeleton["METRICS"]:
			for metric in self.__metrics[mtype]:
				skeleton["METRICS"][mtype][metric] = {"OBJECTIVE":"MINIMIZATION", "POLICIES":[]}

		return skeleton

	def __defineService(self, service, bounds, stype):
		skeleton = {"SERVICE":{"TOPOLOGY":[], "FUNCTION":{}}}

		index = 0
		limit = len(service)
		inBranch = False
		outBranch = False

		skeleton["SERVICE"]["TOPOLOGY"].append("IN")
		for function in service:

			if inBranch:
				skeleton["SERVICE"]["TOPOLOGY"].append("{")
				skeleton["SERVICE"]["TOPOLOGY"].append(function)
				skeleton["SERVICE"]["TOPOLOGY"].append("/")
				inBranch = False
				outBranch = True
			elif outBranch:
				skeleton["SERVICE"]["TOPOLOGY"].append(function)
				skeleton["SERVICE"]["TOPOLOGY"].append("}")
				outBranch = False
				stype = "LINEAR"
			else:
				skeleton["SERVICE"]["TOPOLOGY"].append(function)
			index += 1	

			if stype == "BRANCHED" and not outBranch:
				if index != 0 and limit - index == 3:
					inBranch = True
				else:
					if random.randrange(1, 10) >= 6:
						inBranch = True

			skeleton["SERVICE"]["FUNCTION"][function] = {}
			for resource in bounds:
				skeleton["SERVICE"]["FUNCTION"][function][resource] = random.randrange(bounds[resource]["BEGIN"], bounds[resource]["END"])
		skeleton["SERVICE"]["TOPOLOGY"].append("EN")

		return skeleton

	def __defineMetrics(self, graph):
		domains = {"DOMAINS":{}}
		m_skeleton = {"RESOURCE":{"MEMORY":0, "VCPU":0, "IFACES":0}, "LOCAL":{}, "TRANSITION":{}}

		for e_node in graph:
			t_skeleton = copy.deepcopy(graph[e_node])
			l_skeleton = copy.deepcopy(m_skeleton)

			for resource in self.__metrics["RESOURCE"]:
				l_skeleton["RESOURCE"][resource] = random.randrange(self.__metrics["RESOURCE"][resource]["BEGIN"], self.__metrics["RESOURCE"][resource]["END"])

			for metric in self.__metrics["LOCAL"]:
				if self.__metrics["LOCAL"][metric]["TYPE"] == "INT":
					l_skeleton["LOCAL"][metric] = random.randrange(self.__metrics["LOCAL"][metric]["BEGIN"], self.__metrics["LOCAL"][metric]["END"])
				else:
					l_skeleton["LOCAL"][metric] = random.uniform(float(self.__metrics["LOCAL"][metric]["BEGIN"]), float(self.__metrics["LOCAL"][metric]["END"]))

			for i_node in t_skeleton:
				for metric in self.__metrics["TRANSITION"]:
					if self.__metrics["TRANSITION"][metric]["TYPE"] == "INT":
						t_skeleton[i_node][metric] = random.randrange(self.__metrics["TRANSITION"][metric]["BEGIN"], self.__metrics["TRANSITION"][metric]["END"])
					else:
						t_skeleton[i_node][metric] = random.uniform(float(self.__metrics["TRANSITION"][metric]["BEGIN"]), float(self.__metrics["TRANSITION"][metric]["END"]))

			l_skeleton["TRANSITION"] = t_skeleton
			domains["DOMAINS"][e_node] = l_skeleton

		return domains

	def __init__(self, metrics):

		if not isinstance(metrics, dict):
			self.__status = -1
			return

		if not "LOCAL" in metrics or not "TRANSITION" in metrics:
			self.__status = -2
			return

		if not isinstance(metrics["LOCAL"], dict) or not isinstance(metrics["TRANSITION"], dict):
			self.__status = -3
			return

		for request in metrics["LOCAL"]:
			if not "BEGIN" in metrics["LOCAL"][request]:
				self.__status = -4
				return
			if not "END" in metrics["LOCAL"][request]:
				self.__status = -5
				return

			if not isinstance(metrics["LOCAL"][request]["BEGIN"], int):
				if not isinstance(metrics["LOCAL"][request]["BEGIN"], float):
					self.__status = -6
					return
				else:
					metrics["LOCAL"][request]["TYPE"] = "FLOAT"
			else:
				metrics["LOCAL"][request]["TYPE"] = "INT"

			if not isinstance(metrics["LOCAL"][request]["END"], int):
				if not isinstance(metrics["LOCAL"][request]["END"], float):
					self.__status = -7
					return
				elif metrics["LOCAL"][request]["TYPE"] == "INT":
					metrics["LOCAL"][request]["TYPE"] = "FLOAT"

			if metrics["LOCAL"][request]["BEGIN"] > metrics["LOCAL"][request]["END"]:
				self.__status = -8
				return

		for request in metrics["TRANSITION"]:
			if not "BEGIN" in metrics["TRANSITION"][request]:
				self.__status = -9
				return
			if not "END" in metrics["TRANSITION"][request]:
				self.__status = -10
				return

			if not isinstance(metrics["TRANSITION"][request]["BEGIN"], int):
				if not isinstance(metrics["TRANSITION"][request]["BEGIN"], float):
					self.__status = -11
					return
				else:
					metrics["TRANSITION"][request]["TYPE"] = "FLOAT"
			else:
				metrics["TRANSITION"][request]["TYPE"] = "INT"

			if not isinstance(metrics["TRANSITION"][request]["END"], int):
				if not isinstance(metrics["TRANSITION"][request]["END"], float):
					self.__status = -12
					return
				elif metrics["TRANSITION"][request]["TYPE"] == "INT":
					metrics["TRANSITION"][request]["TYPE"] = "FLOAT"

			if metrics["TRANSITION"][request]["BEGIN"] > metrics["TRANSITION"][request]["END"]:
				self.__status = -13
				return

			if not "RESOURCE" in metrics:
				self.__status = -14
				return

			if not isinstance(metrics["RESOURCE"], dict):
				self.__status = -15
				return

			if not "MEMORY" in metrics["RESOURCE"] or not "VCPU" in metrics["RESOURCE"] or not "IFACES" in metrics["RESOURCE"]:
				self.__status = -16
				return
			elif len(metrics["RESOURCE"]) != 3:
				self.__status = -17
				return

			for resource in metrics["RESOURCE"]:
				if not isinstance(metrics["RESOURCE"][resource], dict):
					self.__status = -18
					return

				if not "BEGIN" in metrics["RESOURCE"][resource] or not "END" in metrics["RESOURCE"][resource]:
					self.__status = -19
					return

				if not isinstance(metrics["RESOURCE"][resource]["BEGIN"], int) or not isinstance(metrics["RESOURCE"][resource]["END"], int):
					self.__status = -20
					return

				if metrics["RESOURCE"][resource]["BEGIN"] > metrics["RESOURCE"][resource]["END"]:
					self.__status = -21
					return

		self.__metrics = metrics
		self.__status = 1

	def completeGraph(self, nodes):
		if not isinstance(nodes, int):
			self.__status = -1
			return -1
		if nodes <= 1:
			self.__status = -2
			return -2

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.complete_graph(nodes)))

	def barbellGraph(self, nodes, connection):
		if not isinstance(nodes, int):
			self.__status = -1
			return -1
		if nodes <= 1:
			self.__status = -2
			return -2
		if not isinstance(connection, int):
			self.__status = -22
			return -22
		if connection <= 0:
			self.__status = -24
			return-24

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.barbell_graph(nodes, connection)))

	def cycleGraph(self, nodes):
		if not isinstance(nodes, int):
			self.__status = -1
			return -1
		if nodes <= 1:
			self.__status = -2
			return -2

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.cycle_graph(nodes)))

	def grid2dGraph(self, x_nodes, y_nodes):
		if not isinstance(x_nodes, int) or not isinstance(y_nodes, int):
			self.__status = -1
			return -1
		if x_nodes <= 1 or y_nodes <= 1:
			self.__status = -2
			return -2

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.grid_2d_graph(x_nodes, y_nodes)))

	def starGraph(self, nodes):
		if not isinstance(nodes, int):
			self.__status = -1
			return -1
		if nodes <= 1:
			self.__status = -2
			return -2

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.star_graph(nodes)))

	def wheelGraph(self, nodes):
		if not isinstance(nodes, int):
			self.__status = -1
			return -1
		if nodes <= 1:
			self.__status = -2
			return -2

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.wheel_graph(nodes)))

	def serviceGraph(self, functions, bounds, stype):

		if not isinstance(functions, list):
			self.__status = -25
			return -25
		for item in functions:
			if not isinstance(item, str):
				self.__status = -26
				return -26

		if not isinstance(bounds, dict):
			self.__status = -27
			return -27
		if not "MEMORY" in bounds or not "VCPU" in bounds or not "IFACES" in bounds or len(bounds) != 3:
			self.__status = -28
			return -28

		for key in bounds:
			if not isinstance(bounds[key], dict):
				self.__status = -29
				return -29
			if not "BEGIN" in bounds[key] or not "END" in bounds[key] or len(bounds[key]) != 2:
				self.__status = -30
				return -30

			for marks in bounds[key]:
				if not isinstance(bounds[key][marks], int):
					self.__status = -31
					return -31
				if bounds[key][marks] < 0:
					self.__status = -32
					return -32

			if bounds[key]["BEGIN"] > bounds[key]["END"]:
				self.__status = -33
				return -33

		if not isinstance(stype, str):
			self.__status = -34
			return -34

		if not stype in ["LINEAR", "BRANCHED"]:
			self.__status = -35
			return -35

		if stype == "BRANCHED" and len(functions) < 4:
			self.__status = -36
			return -36

		return self.__defineService(functions, bounds, stype)

	def requestDocument(self, path, service, network):

		fullDictionary = self.__defineObjectives()
		fullDictionary.update(service)
		fullDictionary.update(network)

		file = open(path, "w+")
		file.write(yaml.dump(fullDictionary))
		file.close()

	def getStatus(self):
		return self.__status


test = RequestGenerator({"RESOURCE":{"MEMORY":{"BEGIN":512, "END":2048}, "VCPU":{"BEGIN":1, "END":4}, "IFACES":{"BEGIN":2, "END":6}}, "LOCAL":{"PRICE":{"BEGIN":50, "END":200}}, "TRANSITION":{"RTT":{"BEGIN":10, "END":25}, "HOPS":{"BEGIN":2, "END":10}}})
network = test.completeGraph(50)
service = test.serviceGraph(["F1", "F2"], {"MEMORY":{"BEGIN":128, "END":1024}, "VCPU":{"BEGIN":1, "END":2}, "IFACES":{"BEGIN":2, "END":4}}, "LINEAR")
test.requestDocument("50x2.yaml", service, network)
