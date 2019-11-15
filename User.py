######## USER CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service)
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#SIMPLE CLI INTERFACE TO REQUISITE FLERAS ALGORITHMS.
#ALL THE DATA TO BE PROCESSED WILL BE INDICATED BY
#A SFC REQUEST IN THE SATANDARD FLERAS MODEL.

#########################################

from os.path import isfile
from cmd import Cmd

from YAMLR.DomainsData import DomainsData
from YAMLR.ComposingRequest import ComposingRequest
from YAMLR.EmbeddingRequest import EmbeddingRequest
from SCAG.SFCTopology import SFCTopology
from CUSCO.SFCExpansion import SFCExpansion
from CUSCO.GoalFunction import GoalFunction
from CUSCO.SFCComposition import SFCComposition
from CUSMAP.SFCSplitMap import SFCSplitAndMap

class FLERASCLI(Cmd):

	prompt = "fleras> "
	domains = None
	request = None
	topology = None
	composition = None
	mapping = None
	type = None

	def do_help(self, args):

		print("\n############### HELP #################")
		print("help -> show this message")
		print("exit -> ends the execution")
		print("domains path -> receives a domain data description path, validate and enable its informations for setup")
		print("setup type path -> receives a request type (C for compose and SM for split and mapping) and a sfc request path, validate and enable the commands below according to setup type")
		print("compose -> executes the generic composition method in an already informed sfc request, it enables the topologies and advice commands")
		print("map -> executes the generic split and mappings method in an already informed sfc request, it enables the mappings and advice commands")
		print("topologies -> show all composed topologies in addition to their suitability indexes")
		print("mappings -> show all mapped topologies in addition to their suitability indexes and pareto front location")
		print("advice -> inidicates the best composed/mapped topology considering the goal function")
		print ('######################################\n')

	def do_domains(self, args):

		if len(args) == 0:
			return

		if not isfile(args):
			print("INVALID FILE")
			return

		self.domains = DomainsData(args)
		if self.domains.ddStatus() != 1:
			print("DOMAINS VALIDATION FAILED - ERROR " + str(self.domains.ddStatus()))
			self.domains = None
			return

		self.request = None
		self.topology = None
		self.composition = None

		print("SUCCESS!!")

	def do_setup(self, args):

		args = args.split()
		if len(args) < 2:
			print("TOO FEW ARGUMENTS TO SETUP REQUEST")
			return

		if not args[0] in ["C", "SM"]:
			print("TYPE IS NEED AS FIRST ARGUMENT (C FOR COMPOSING OR SM FOR SPLIT/MAP)")
			return

		if self.domains == None:
			print("DOMAINS SETUP IS REQUIRED")
			return

		if not isfile(args[1]):
			print("INVALID FILE")
			return

		if args[0] == "C":
			self.request = ComposingRequest(args[1], self.domains.ddDomains())
			if self.request.crStatus() != 1:
				print("REQUEST VALIDATION FAILED - ERROR " + str(self.request.crStatus()))
				self.request = None
				return
			self.topology = SFCTopology(self.request.crServiceON(), self.request.crServiceOE(), self.domains.ddDomains())
			self.topology.stValidate(self.request.crServiceTopology())
			if self.topology.stStatus() != 1:
				print("TOPOLOGY VALIDATION FAILED - ERROR " + str(self.topology.crStatus()))
				self.request = None
		else:
			if args[0] == "SM":
				self.request = EmbeddingRequest(args[1], self.domains.ddDomains())
				if self.request.erStatus() != 1:
					print("REQUEST VALIDATION FAILED - ERROR " + str(self.request.erStatus()))
					self.request = None
					return
				self.topology = SFCTopology(self.request.erServiceON(), self.request.erServiceOE(), self.domains.ddDomains())
				self.topology.stValidate(self.request.erServiceTopology())
				if self.topology.stStatus() != 1:
					print("TOPOLOGY VALIDATION FAILED - ERROR " + str(self.topology.erStatus()))
					self.request = None

		self.type = args[0]
		self.composition = None

		print("SUCCESS!!")

	def do_compose(self, args):

		if len(args) != 0 or self.type != "C":
			return

		if self.request == None:
			print("REQUEST SETUP IS REQUIRED")
			return

		expand = SFCExpansion(self.topology)
		self.composition = SFCComposition(self.request, expand.seBranches())
		self.composition.scEvaluate()

		print("SUCCESS!!")

	def do_map(self, args):

		if len(args) != 0 or self.type != "SM":
			return

		if self.request == None:
			print("REQUEST SETUP IS REQUIRED")
			return

		self.mapping = SFCSplitAndMap(self.request, self.domains)
		self.mapping.ssamNaturalRequest()

	def do_topologies(self, args):

		if len(args) != 0:
			return

		if self.composition == None:
			print("COMPOSE TASK IS REQUIRED")
			return

		topologies = self.composition.scSFCIndexes()

		print("############### TOPOLOGIES #################")
		for topo in topologies:
			print("TOPOLOGY: " + topo[0] + "  " + "INDEX: " + str(topo[1]))
		print("###########################################")

	def do_mappings(self, args):

		if len(args) != 0:
			return

		if self.mapping == None:
			print("MAPPING TASK IS REQUIRED")
			return

		maps = self.mapping.ssamKeys()
		sis = self.mapping.ssamIndexes()
		front = self.mapping.ssamFrontiers()

		print("################ MAPPINGS ##################")
		for index in range(len(maps)):
			print("MAPPING: " + str(maps[index]) + "  INDEX: " + str(sis[index]) + " FRONT: " + str(front[index]))
		print("###########################################")

	def do_advice(self, args):

		if len(args) != 0:
			return

		if self.composition == None and self.mapping == None:
			print("DEPLOYMENT PROCESS IS REQUIRED")
			return

		print("############### ADVICE #################")
		if self.composition != None:
			print("COMPOSITION: " + self.composition.scBestTopology())
		if self.mapping != None:
			print("MAPPING: " + self.mapping.ssamAdvice())
		print("###########################################")

	#xxx - Deevelopment
	def do_report(self, args):

		args = args.split()
		if len(args) < 2:
			print("TOO FEW ARGUMENTS TO SETUP REQUEST")
			return

		if not args[0] in ["C", "SM"]:
			print("TYPE IS NEED AS FIRST ARGUMENT (C FOR COMPOSING OR SM FOR SPLIT/MAP)")
			return

		if args[0] == "SM":
			
			if self.mapping == None:
				print("MAPPING TASK IS REQUIRED")
				return

			maps = self.mapping.ssamKeys()
			sis = self.mapping.ssamIndexes()
			front = self.mapping.ssamFrontiers()

			file = open(args[1], "w+")
			file.write("MAPPING;SUITABILITY;FRONTIER\n")
			for index in range(len(maps)):
				file.write(str(maps[index]) + ";" + str(sis[index]) + ";" + str(front[index]) + "\n")
			file.close()

	def do_exit(self, args):

		exit()

	def do_EOF(self, args):

		return

if __name__ == '__main__':

	print(" _   _ ______ _   _     ______ _      ___________  ___   _____ ")
	print("| \ | ||  ___| | | |    |  ___| |    |  ___| ___ \/ _ \ /  ___|")
	print("|  \| || |_  | | | |    | |_  | |    | |__ | |_/ / /_\ \\\\ `--. ")
	print("| . ` ||  _| | | | |    |  _| | |    |  __||    /|  _  | `--. \\")
	print("| |\  || |   \ \_/ /    | |   | |____| |___| |\ \| | | |/\__/ /")
	print("\_| \_/\_|    \___/     \_|   \_____/\____/\_| \_\_| |_/\____/")
	print("")

	FLERASCLI().cmdloop()
