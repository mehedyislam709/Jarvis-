import yaml

class Config:

    def __init__(self, path="config/config.yaml"):

        with open(path, "r") as f:

            self.data = yaml.safe_load(f)

    def get(self, key):

        keys = key.split(".")

        value = self.data

        for k in keys:

            value = value[k]

        return value
