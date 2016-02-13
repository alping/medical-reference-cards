import yaml

def yaml_loader(filepath):
	with open(filepath, 'r') as file_descriptor:
		data = yaml.load(file_descriptor)
		file_descriptor.close()
	return data

def yaml_dump(filepath, data):
	with open(filepath, 'w') as file_descriptor:
		yaml.dump(data, file_descriptor)
		file_descriptor.close()

if __name__ == "__main__":
	filepath = "../content/pediatrics/general/pediatrics-normal-physiology/pediatrics-normal-physiology.yml"
	data = yaml_loader(filepath)
	print(data)