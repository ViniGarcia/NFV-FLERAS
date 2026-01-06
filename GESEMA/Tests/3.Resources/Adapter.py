import random
import yaml

def adapt_values(yaml_data, action, factor, incidence):

	probability = incidence * 100
	action_select_min = [1-factor, 1+factor]
	action_select_max = [1+factor, 1-factor]

	for domain in yaml_data["DOMAINS"]:
		for transition in yaml_data["DOMAINS"][domain]["TRANSITION"]:
			for metric in yaml_data["DOMAINS"][domain]["TRANSITION"][transition]:
				if random.randrange(1,100) <= probability: 
					if yaml_data["METRICS"]["TRANSITION"][metric]["OBJECTIVE"] == "MAXIMIZATION": 
						yaml_data["DOMAINS"][domain]["TRANSITION"][transition][metric] *= action_select_max[action]
					else:
						yaml_data["DOMAINS"][domain]["TRANSITION"][transition][metric] *= action_select_min[action]
		for metric in yaml_data["DOMAINS"][domain]["LOCAL"]:
			if random.randrange(1,100) <= probability:
				if yaml_data["METRICS"]["LOCAL"][metric]["OBJECTIVE"] == "MAXIMIZATION":
					yaml_data["DOMAINS"][domain]["LOCAL"][metric] *= action_select_max[action]
				else:
					yaml_data["DOMAINS"][domain]["LOCAL"][metric] *= action_select_min[action]

#=====================================================

file_path = "25x9.yaml"

raw_file = open(file_path, "r")
raw_data = raw_file.read()
raw_file.close()

yaml_data = yaml.safe_load(raw_data)

#action 0 - degrade
#factor 0~1 - how much to degrade
#incidence 0~1 - how many to degrade
adapt_values(yaml_data, 0, 0.05, 0.05)
file = open("25x9-improved.yaml", "w+")
file.write(yaml.dump(yaml_data))
file.close()

#action 1 - improve
#factor 0~1 - how much to improve
#incidence 0~1 - how many to improve
adapt_values(yaml_data, 1, 0.05, 0.05)
file = open("25x9-damaged.yaml", "w+")
file.write(yaml.dump(yaml_data))
file.close()