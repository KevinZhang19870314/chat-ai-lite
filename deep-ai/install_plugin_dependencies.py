import os

from log import log


# for root, dirs, files in os.walk('./plugins'):
# 	for file in files:
# 		if file == 'requirements.txt':
# 			req_file = os.path.join(root, file)
# 			os.system(f'pip install --no-cache-dir -r "{req_file}"')

def is_requirements_file_empty(file_path):
	with open(file_path, 'r') as file:
		content = file.read()
		return len(content.strip()) == 0


def install_plugin_dependencies(path: str):
	for root, dirs, files in os.walk(path):
		for file in files:
			req_file = os.path.join(root, file)
			if file == 'requirements.txt' and not is_requirements_file_empty(req_file):
				log(f"Install plugin dependencies from path {path}")
				os.system(f'pip install --no-cache-dir -r "{req_file}"')
