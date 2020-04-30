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

from CUSTOM.CUSTOM import CUSTOM

from YAMLR.YAMLRDomains import YAMLRDomains
from YAMLR.YAMLRComposition import YAMLRComposition
from YAMLR.YAMLREmbedding import YAMLREmbedding

from CUSCO.CUSCO import CUSCO
from CUSMAP.CUSMAP import CUSMAP

class FLERASCLI(Cmd):

	prompt = "fleras> "
	
	domains = None
	request = None
	topology = None

	player = None
	mode = None

	def do_help(self, args):

		print("\n############### HELP #################")
		print("help -> show this message")
		print("exit -> ends the execution")
		print("setup CUSCO request_file [domains_file] -> receives a mandatory request_file and an optional domains_file and prepare CUSCO execution")
		print("setup CUSMAP request_file domains_file -> receives mandatory request_file and domains_file and prepare CUSMAP execution")
		print("execute -> process the provided files with the requested algorithm")
		print("results -> presents all the results of the last execution")
		print("advice -> presents the best result of the last execution")
		print ('######################################\n')

	def do_setup(self, args):

		args = args.split()
		if len(args) < 2 or len(args) > 3:
			print("ERROR: INVALID ARGUMENTS TO SETUP REQUEST!")
			return

		if not args[0] in ["CUSCO", "CUSMAP"]:
			print("ERROR: DEPLOYMENT SOLUTION MUST BE DEFINED AS THE FIRST ARGUMENT (CUSCO/CUSMAP)!")
			return

		if args[0] == "CUSMAP" and len(args) != 3:
			print("ERROR: A DOMAINS FILE MUST BE PROVIDED FOR CUSMAP EXECUTION!")
			return

		if not isfile(args[1]): 
			print("ERROR: FILE \"" + args[1] + "\" DOES NOT EXIST!")
			return

		if len(args) == 3 and not isfile(args[2]):
			print("ERROR: FILE \"" + args[2] + "\" DOES NOT EXIST!")
			return

		domains_list = []
		if len(args) == 3:
			self.domains = YAMLRDomains(args[2])
			if self.domains.ydStatus() != 1:
				print("YAMLR DOMAINS ERROR " + str(self.domains.ydStatus()) + ": INVALID DOMAINS FILE!")
				return
			domains_list = self.domains.ydDomains()

		if args[0] == "CUSCO":
			self.request = YAMLRComposition(args[1], domains_list)
			if self.request.ycStatus() != 1:
				print("YAMLR COMPOSITION ERROR " + str(self.request.ycStatus()) + ": INVALID CUSCO REQUEST FILE!")
				self.request = None
				return

			self.topology = CUSTOM(self.request.ycServiceNF(), [], domains_list, [], self.request.ycServiceEN())
			self.topology.cValidate(self.request.ycServiceTopology())
			if self.topology.cStatus() != 1:
				print("CUSTOM ERROR " + str(self.topology.cStatus()) + ": INVALID SERVICE TOPOLOGY!")
				self.request = None
				return

		elif args[0] == "CUSMAP":
			self.request = YAMLREmbedding(args[1], domains_list)
			if self.request.yeStatus() != 1:
				print("YAMLR EMBEDDING ERROR " + str(self.request.yeStatus()) + ": INVALID CUSMAP REQUEST FILE!")
				self.request = None
				return

			self.topology = CUSTOM(self.request.yeServiceNF(), [], domains_list, [], self.request.yeServiceEN())
			self.topology.cValidate(self.request.yeServiceTopology())
			if self.topology.cStatus() != 1:
				print("CUSTOM ERROR " + str(self.topology.cStatus()) + ": INVALID SERVICE TOPOLOGY!")
				self.request = None
				return

		self.mode = args[0]
		self.player = None

		print("SUCCESS: SETUP IS DONE!")

	def do_execute(self, args):

		if len(args) != 0:
			print("ERROR: EXECUTE DOES NOT RECEIVE ANY ARGUMENT!")
			return

		if self.player != None:
			if (self.mode == "CUSCO" and self.player.scStatus() != 2) or (self.mode == "CUSMAP" and self.player.smStatus() != 2):
				print("NOTICE: CURRENT SETUP WAS ALREADY EXECUTED AND IT FAILED!")
			else:
				print("NOTICE: CURRENT SETUP WAS ALREADY EXECUTED AND IT SUCESSED!")
			return

		if self.request == None:
			print("ERROR: SETUP MUST BE DONE BEFORE EXECUTION PROCESS!")
			return

		if self.mode == "CUSCO":
			self.player = CUSCO(self.request, self.topology)
			self.player.scEvaluate()

			if self.player.scStatus() != 2:
				print("CUSCO ERROR " + self.player.scStatus() + ": COMPOSITION FAILED!")
				return

		elif self.mode == "CUSMAP":
			self.player = CUSMAP(self.request, self.domains)
			self.player.smEvaluate()

			if self.player.smStatus() != 2:
				print("CUSMAP ERROR " + self.player.smStatus() + ": EMBEDDING FAILED!")
				return

		print("SUCCESS: EXECUTION IS DONE!")

	def do_results(self, args):

		if len(args) != 0:
			print("ERROR: RESULTS DOES NOT RECEIVE ANY ARGUMENT!")
			return

		if self.player == None:
			print("NOTICE: EXECUTION MUST BE DONE BEFORE RESUTS REQUEST!")
			return

		if self.mode == "CUSCO":
			if self.player.scStatus() != 2:
				print("ERROR: EXECUTION MUST BE DONE BEFORE RESUTS REQUEST!")
				return

			compositions = self.player.scSFCIndexes()
			print("############### CUSCO RESULTS #################")
			for index in range(len(compositions)):
				print(str(index) + ". COMPOSITION: " + compositions[index][0] + "  INDEX: " + str(compositions[index][1]))
			print("###############################################")

		elif self.mode == "CUSMAP":
			if self.player.smStatus() != 2:
				print("ERROR: EXECUTION MUST BE DONE BEFORE RESUTS REQUEST!")
				return

			embeddings = list(self.player.smIndexes().keys())
			print("################ CUSMAP RESULTS ##################")
			for index in range(len(embeddings)):
				print(str(index) + ". EMBEDDING: " + str(embeddings[index]) + "  INDEX: " + str(self.player.smIndexes()[embeddings[index]]))
			print("##################################################")

	def do_advice(self, args):

		if len(args) != 0:
			print("ERROR: RESULTS DOES NOT RECEIVE ANY ARGUMENT!")
			return

		if self.player == None:
			print("NOTICE: EXECUTION MUST BE DONE BEFORE ADVICE REQUEST!")
			return

		if self.mode == "CUSCO":
			advice = "COMPOSITION: " + self.player.scSFCBest()
		elif self.mode == "CUSMAP":
			advice = "MAPPING: " + self.player.smBest()

		print("############### ADVICE #################")
		print(advice)
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
