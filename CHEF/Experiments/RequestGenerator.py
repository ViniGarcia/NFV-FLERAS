import copy
import random
import yaml

class RequestGenerator:

	def __stringfy(self, sample):
		optOrder = False
		string = ""
		for index in range(len(sample)):
			if sample[index] == '(':
				string += sample[index] + ' '
				optOrder = True
			else:
				if sample[index] == ')':
					string = string + sample[index] + ' - '
					optOrder = False
				else:
					if not optOrder:
						string += sample[index] + ' - '
					else:
						string += sample[index] + ' '

		if string[-2] == '-':
			string = string[:-3]
		else:
			string = string[:-1]
		return string

	def __process(self, nodes, maxOrders):

		if nodes == None and maxOrders == None:
			return

		samples = []

		baseNodes = []
		for index in range(nodes):
			baseNodes.append('NF' + str(index))

		for order in range(1, maxOrders):
			for position in range(nodes - order):
				sample = copy.copy(baseNodes)
				sample = sample[:position] + ['('] + sample[position:position + (order + 1)] + [')'] + sample[position + (order + 1):]
				samples.append(sample)

		return samples

	def mehDocuments(self, nodes, maxOrders, specification):

		if nodes < 2 or maxOrders < 2:
			return

		if maxOrders > nodes:
			return

		samples = self.__process(nodes, maxOrders)

		if len(samples) == 0:
			return

		docIndex = 1
		for sample in samples:
			document = {}
			document['TOPOLOGY'] = self.__stringfy(sample)
			document['ELEMENTS'] = {}
			for index in range(len(sample)):
				if sample[index] == '(' or sample[index] == ')':
					continue
				document['ELEMENTS'][sample[index]] = {}
				for spec in specification:
					document['ELEMENTS'][sample[index]][spec] = random.uniform(specification[spec][0], specification[spec][1])

			with open('mehDocument' + str(docIndex) + '.yaml', 'w') as outfile:
				yaml.dump(document, outfile, default_flow_style=False)
			document["METRICS"] = {'TR':('min', 1.0)}
			with open('mehDocumentMulti' + str(docIndex) + '.yaml', 'w') as outfile:
				yaml.dump(document, outfile, default_flow_style=False)
			docIndex += 1

	def mijDocuments(self, samples, nrNodes, nodesSpec, functionsSpec):

		docIndex = 1
		for sample in samples:
			document = {'REQUEST':{}}
			document['REQUEST']['TOPOLOGY'] = sample
			document['REQUEST']['ELEMENTS'] = {}
			sample = sample.replace(' ', '').split('-')
			for index in range(len(sample)):
				if sample[index] == '(' or sample[index] == ')':
					continue
				document['REQUEST']['ELEMENTS'][sample[index]] = {}
				for spec in functionsSpec:
					if spec == 'BT':
						document['REQUEST']['ELEMENTS'][sample[index]][spec] = random.randint(functionsSpec[spec][0], functionsSpec[spec][1])
					else:
						document['REQUEST']['ELEMENTS'][sample[index]][spec] = random.uniform(functionsSpec[spec][0], functionsSpec[spec][1])

			baseNodes = []
			for index in range(nrNodes):
				baseNodes.append('N' + str(index))

			document['INFRA'] = {}
			for node in baseNodes:
				document['INFRA'][node] = {}
				for spec in nodesSpec:
					if spec == 'BT':
						document['INFRA'][node][spec] = random.randint(nodesSpec[spec][0], nodesSpec[spec][1])
					else:
						document['INFRA'][node][spec] = random.uniform(nodesSpec[spec][0], nodesSpec[spec][1])

			with open('mijDocument' + str(docIndex) + '.yaml', 'w') as outfile:
				yaml.dump(document, outfile, default_flow_style=False)
			document['REQUEST']['METRICS'] = {'C':{'TYPE':'CATALOG', 'SPEC':('min', 1.0)}}
			with open('mijDocumentMulti' + str(docIndex) + '.yaml', 'w') as outfile:
				yaml.dump(document, outfile, default_flow_style=False)
			docIndex += 1



#generator = RequestGenerator()
#generator.mehDocuments(8, 8, {'TR':(0.5, 1.0)})
#generator.mijDocuments(["NF0", "NF0 - NF1", "NF0 - NF1 - NF2", "NF0 - NF1 - NF2 - NF3", "NF0 - NF1 - NF2 - NF3 - NF4", "NF0 - NF1 - NF2 - NF3 - NF4 - NF5", "NF0 - NF1 - NF2 - NF3 - NF4 - NF5 - NF6", "NF0 - NF1 - NF2 - NF3 - NF4 - NF5 - NF6 - NF7"], 4, {'BT':(2,5), 'C':(0.5,2)}, {'BT':(1,4)})
