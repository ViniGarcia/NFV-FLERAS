import os
import yaml

class SFCRequest:

	__metadata = None
	__topology = None
	__objFunctions = None

	def __init__(self, requestFile):

		if not os.path.isfile(requestFile):
			return
		openedFile = open(requestFile, "r")
		fileData = openedFile.read()
		openedFile.close()

		try:
			yamlParsed = yaml.load(fileData)
		except:
			return
		
		self.__metadata = {"ID":yamlParsed["ID"], "DESCRIPTION":yamlParsed["DESCRIPTION"]}
		self.__topology = {"TOPOLOGY":yamlParsed["TOPOLOGY"], "BRANCHINGS":yamlParsed["BRANCHINGS"], "OPELEMENTS":yamlParsed["OPELEMENTS"], "EPS":yamlParsed["EPS"]}
		self.__objFunctions = {"GOAL":yamlParsed["GOAL"], "FUNCTION":yamlParsed["FUNCTION"]}
		#CALL VALIDATE

lala = SFCRequest("ReqExample.yaml")




