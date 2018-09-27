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

from SFCRequest import SFCRequest
from SFCTopology import SFCTopology
from SFCExpansion import SFCExpansion
from GoalFunction import GoalFunction
from SFCComposition import SFCComposition

class FLERASCLI(Cmd):

	prompt = "fleras> "
	request = None
	topology = None
	composition = None

	def do_help(self, args):
		
		print("\n############### HELP #################")
		print("help -> show this message")
		print("exit -> ends the execution")
		print("setup path -> receives a sfc request path, validate and enable the commands below")
		print("compose -> executes the generic composition method in already informed sfc request, it enables the topologies and advice commands")
		print("topologies -> show all composed topologies in addition to their goal functions indexes")
		print("advice -> inidicates the best composed topology considering the goal function")
		print ('######################################\n')

	def do_setup(self, args):

		if len(args) == 0:
			return

		if not isfile(args):
			print("INVALID FILE")
			return

		self.request = SFCRequest(args)
		if self.request.srStatus() != 1:
			print("REQUEST VALIDATION FAILED - ERROR " + str(self.request.srStatus()))
			self.request = None
			return
		
		self.topology = SFCTopology(self.request.srEPs(), self.request.srOPEs())
		self.topology.stValidate(self.request.srTopology())
		if self.topology.stStatus() != 1:
			print("TOPOLOGY VALIDATION FAILED - ERROR " + str(self.topology.srStatus()))
			self.request = None

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
			print("COMPOSITION PROCESS IS NEEDED")
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
			print("COMPOSITION PROCESS IS NEEDED")
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
