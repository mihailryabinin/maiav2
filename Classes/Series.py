import logging
import pydicom as dicom
import SimpleITK as sitk
import numpy as np

from pydicom.dataset import Dataset, FileDataset


class Series(object):
    series_id = None
    study_id = None
    metrics = None  # ?
    image = None
    number_of_image = None  # ?
    series_info = None
    loaded = None

    def __init__(self):
        super().__init__()
        self.series_info = dict([
            ('PatientID', 0),
            ('PatientName', 0),
            ('PatientSex', 0),
            ('PatientAge', 0),
            ('PatientBirthDate', 0),
            ('ContentDate', 0),
            ('ContrastBolusAgent', 0),
            ('ContrastBolusRoute', 0),
            ('Manufacturer', 0),
            ('ManufacturerModelName', 0)
        ])
        self.loaded = False
        self.miniature = None

    def download_series(self, folder):
        if folder.type == 'pacs':
            self.parse_dataset(folder)
        elif folder.type == 'folder':
            self.from_folder(folder)

    def parse_dataset(self, dt):
        if type(dt) is Dataset:
            try:
                self.image = None
            except Exception as e:
                print(e)
        else:
            print('It not need type')

    def from_folder(self, path_to_series):
        try:
            series_reader = sitk.ImageSeriesReader()
            meta_info = dicom.read_file(series_reader.GetGDCMSeriesFileNames(path_to_series)[0])
            self.meta_load(meta_info)

            dicom_files_name = series_reader.GetGDCMSeriesFileNames(path_to_series)
            series_reader.SetFileNames(dicom_files_name)
            self.image = sitk.GetArrayFromImage(series_reader.Execute())[::-1]
            self.number_of_image = len(self.image)
            self.series_info.update({'ImagesNumber': self.number_of_image})
            self.miniature = self.image[self.number_of_image // 2] // 10 + 100
            self.loaded = True
        except Exception as e:
            print(path_to_series, self.loaded)
            print(e)

    def meta_load(self, meta_data):
        try:
            if type(meta_data) is FileDataset:
                for key, _ in self.series_info.items():
                    value = getattr(meta_data, key, '')
                    if key == 'ContentDate' or key == 'PatientBirthDate':
                        value = '.'.join([value[6:], value[4:6], value[:4]])
                    self.series_info.update({key: value})

                x, y = getattr(meta_data, 'PixelSpacing', [1, 1])
                z_t = float(getattr(meta_data, 'SliceThickness', 2))
                z_s = float(getattr(meta_data, 'spacingBetweenSlices', 0))
                self.metrics = np.array([z_t + z_s, float(y), float(x)])
                self.series_info.update({'SliceThickness': z_t})
                self.series_id = getattr(meta_data, 'SeriesInstanceUID', -1)
                self.study_id = getattr(meta_data, 'StudyInstanceUID', -1)
        except Exception as e:
            print(e)

    def get_series_info(self):
        return self.series_info

    def get_metric(self):
        return self.metrics

    def get_image(self):
        return self.image

    def get_study_id(self):
        return self.study_id

    def get_status(self):
        return self.loaded

    def get_miniature(self):
        return self.miniature
