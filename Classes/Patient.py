from Classes.Series import Series


class Patient(object):
    patient_info = None
    study_id = None
    series = None

    def __init__(self):
        self.study_id = ''
        self.series = []
        self.patient_info = {}

    def add_series(self, list_series, study_id):
        try:
            for series in list_series:
                if type(series) is Series:
                    self.series.append(series)
                else:
                    print('Not need type of series')
            if len(self.series) > 0:
                self.study_id = study_id
            else:
                return -1
        except Exception as e:
            print(e)

    # def get_patient_info(self):
    #     series = self.series[0]
    #     self.patient_info = series.get_patient_info()

    def add_patient_info(self, dict_param):
        if type(dict_param) == dict:
            try:
                self.patient_info.update(dict_param)
            except Exception as e:
                print(e)
        else:
            print('It is not type dict for pat_info')

    def get_series(self):
        return self.series
