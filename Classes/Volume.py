import numpy as np


class Volume(object):
    def __init__(self, coordinate, size=None, type_volume=None, probability=None, is_doctor=False, is_confirmed=False):
        # super().__init__()
        self.coordinate = np.array(coordinate)
        self.volume_size = size
        self.type_volume = type_volume
        self.information = dict([])
        self.probability = probability
        self.is_doctor = is_doctor
        self.is_confirmed = is_confirmed

    def set_information(self, info):
        if type(info) is dict:
            try:
                self.information.update(info)
            except Exception as e:
                print(e)

    def is_point(self, point):
        if type(point) == np.ndarray:
            try:
                return -1
            except Exception as e:
                print(e)
        return

    def json_code(self):
        file = {'type': 'volume',
                'coordinate': self.coordinate.tolist(),
                'volume_type': self.type_volume,
                'information': self.information,
                'probability': self.probability,
                'is_doctor': self.is_doctor,
                'is_confirmed': self.is_confirmed}
        return file

    def get_coordinate(self):
        return self.coordinate
