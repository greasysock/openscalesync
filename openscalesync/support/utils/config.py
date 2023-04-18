import yaml

def load_config(path):
  with open(path, 'r') as stream:
    return yaml.unsafe_load(stream)