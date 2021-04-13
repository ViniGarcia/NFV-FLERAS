import yaml
import math
import random


requestFile = open("AWS_REQ_7.yaml", "r")
requestYAML = yaml.safe_load(requestFile)

for domain in requestYAML["DOMAINS"]:
	requestYAML["DOMAINS"][domain]["LOCAL"]["RELIABILITY"] = random.uniform(0.95, 0.99)
	requestYAML["DOMAINS"][domain]["LOCAL"]["LINKS"] = len(requestYAML["DOMAINS"][domain]["TRANSITION"])
	requestYAML["DOMAINS"][domain]["LOCAL"]["BANDWIDTH"] = random.randint(100, 500) * requestYAML["DOMAINS"][domain]["LOCAL"]["LINKS"]

	transList = []
	delayList = []
	for trans in requestYAML["DOMAINS"][domain]["TRANSITION"]:
		transList.append(trans)
		delayList.append(requestYAML["DOMAINS"][domain]["TRANSITION"][trans]["DELAY"])
	
	minDelay = min(delayList)
	maxDelay = max(delayList)
	delayParameters = [(maxDelay - d)/(maxDelay - minDelay)*-4 for d in delayList]
	delayValues = [math.ceil(delayList[index] * (1-math.pow(math.e, delayParameters[index])) * 0.05) for index in range(len(delayList))]
	
	for index in range(len(delayList)):
		requestYAML["DOMAINS"][domain]["TRANSITION"][transList[index]]["DELAY"] = delayValues[index]

resultFile = open("AWS_REQ_7_GALCB.yaml", "w+")
resultFile.write(yaml.dump(requestYAML))
resultFile.close()

		


