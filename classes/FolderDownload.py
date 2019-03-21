import os
from classes.Series import Series
from classes.Patient import Patient
from numpy import unique, array


class FolderDownload(object):
    type_ = 'folder'
    path_to_dicom = None
    pattern = None
    series_folders = None

    def __init__(self, path_to_dicom, pattern='.dcm'):
        super().__init__()
        self.path_to_dicom = path_to_dicom
        self.pattern = pattern
        self.set_path_to_series()

    def set_path_to_series(self):
        try:
            result = []
            for root, dirs, files in os.walk(self.path_to_dicom):
                for name in files:
                    if self.pattern in name:
                        result.append(root)
            self.series_folders = unique(result)
        except Exception as e:
            print(e)
            self.series_folders = None

    def get_patient_from_folders(self):
        if self.series_folders is not None:
            try:
                list_series = []
                patients_list = []
                for folder in self.series_folders:
                    series = Series()
                    series.from_folder(folder)
                    if series.get_status():
                        list_series.append([series, series.get_study_id()])
                list_series = array(list_series)
                for study_id in unique(list_series[:, 1]):
                    patient = Patient()
                    patient.add_series(list_series[:, 0][list_series[:, 1] == study_id], study_id)
                    patients_list.append(patient)
                return patients_list
            except Exception as e:
                print(e)
                return -1
        else:
            print('Some problem with folders create')
            return -1
