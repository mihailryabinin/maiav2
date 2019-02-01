import numpy as np


class Volume(object):
    def __init__(self, coordinate, size):
        super().__init__()
        self.coordinate = np.array(coordinate)
        self.volume_size = size
        self.type_volume = ''
        self.information = dict([])
        self.probability = 0

    def set_information(self, info):
        if type(info) is dict:
            try:
                self.information
            except Exception as e:
                print(e)

    def is_point(self, point):
        if type(point) == np.ndarray:
            try:
                return -1
            except Exception as e:
                print(e)
        return
