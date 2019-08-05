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
from YAMLR.GeneralRequest import GeneralRequest
from SCAG.SFCTopology import SFCTopology
from CUSCO.SFCExpansion import SFCExpansion
from CUSCO.GoalFunction import GoalFunction
from CUSCO.SFCComposition import SFCComposition

class FLERASCLI(Cmd):

	prompt = "fleras> "
	domains = None
	request = None
	topology = None
	composition = None

	def do_help(self, args):

		print("\n############### HELP #################")
		print("help -> show this message")
		print("exit -> ends the execution")
		print("domains path -> receives a domain data description path, validate and enable its informations for setup")
		print("setup path -> receives a sfc request path, validate and enable the commands below")
		print("compose -> executes the generic composition method in already informed sfc request, it enables the topologies and advice commands")
		print("topologies -> show all composed topologies in addition to their goal functions indexes")
		print("advice -> inidicates the best composed topology considering the goal function")
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

		if len(args) == 0:
			return

		if self.domains == None:
			print("DOMAINS SETUP IS NEEDED")
			return

		if not isfile(args):
			print("INVALID FILE")
			return

		self.request = GeneralRequest(args, self.domains.ddDomains())
		if self.request.grStatus() != 1:
			print("REQUEST VALIDATION FAILED - ERROR " + str(self.request.grStatus()))
			self.request = None
			return

		self.topology = SFCTopology(self.request.grServiceON(), self.request.grServiceOE(), self.domains.ddDomains())
		self.topology.stValidate(self.request.grServiceTopology())
		if self.topology.stStatus() != 1:
			print("TOPOLOGY VALIDATION FAILED - ERROR " + str(self.topology.grStatus()))
			self.request = None

		self.composition = None

		print("SUCCESS!!")

	def do_compose(self, args):

		if len(args) != 0:
			return

		if self.request == None:
			print("REQUEST SETUP IS NEEDED")
			return

		expand = SFCExpansion(self.topology)
		self.composition = SFCComposition(self.request, expand.seBranches())
		self.composition.scEvaluate()

		print("SUCCESS!!")

	def do_topologies(self, args):

		if len(args) != 0:
			return

		if self.composition == None:
			print("COMPOSE PROCESS IS NEEDED")
			return

		topologies = self.composition.scSFCIndexes()

		print("############### TOPOLOGIES #################")
		for topo in topologies:
			print("TOPOLOGY: " + topo[0] + "  " + "INDEX: " + str(topo[1]))
		print("###########################################")

	def do_advice(self, args):

		if len(args) != 0:
			return

		if self.composition == None:
			print("COMPOSE PROCESS IS NEEDED")
			return

		print("############### ADVICE #################")
		print("COMPOSITION: " + self.composition.scBestTopology())
		print("###########################################")

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
