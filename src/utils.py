import pickle
import os


class PickleHandler:
    def __init__(self, picklename):
        self.picklename = picklename

    def read(self):
        data = {}

        with open(self.picklename, 'rb') as obj:
            data = pickle.loads(obj.read())

        return data

    def write(self, data):
        with open(self.picklename, 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def chunks(lista, step=100):
    for i in range(0, len(lista), step):
        yield lista[i: i+step]
