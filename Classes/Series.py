import logging
import os
import zipfile
import json
import pydicom as dicom
import SimpleITK as sitk
import numpy as np
from Classes.Volume import Volume

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
        self.list_volumes = []
        self.path_to_series = ''

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
            self.path_to_series = path_to_series
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
                    if type(value) not in (str, int, float):
                        value = str(value)
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

    def add_value(self, coordinate, size=None, type_volume=None, probability=None, is_doctor=False, is_confirmed=False):
        if coordinate is not None:
            try:
                self.list_volumes.append(Volume(coordinate, size, type_volume, probability, is_doctor, is_confirmed))
            except Exception as e:
                print('add_value', e)

    def get_series_info(self):
        return self.series_info

    def get_metric(self):
        return self.metrics

    def get_image(self):
        return self.image

    def get_study_id(self):
        return self.study_id

    def get_series_id(self):
        return self.series_id

    def get_status(self):
        return self.loaded

    def get_miniature(self):
        return self.miniature

    def json_code(self):
        list_volumes = [volume.json_code() for volume in self.list_volumes]
        file = {
            'Type': 'series',
            'SeriesID': self.series_id,
            'StudyID': self.study_id,
            'Information': self.series_info,
            'Volumes': list_volumes,
            # 'Image': self.image.tolist()
        }
        return file

    def json_decode(self):
        pass

    def get_list_contour(self):
        return [volume.get_coordinate() for volume in self.list_volumes]

    def save_series(self):
        try:
            jsonfile = open(self.path_to_series + '/series_info.json', 'w')
            json.dump(self.json_code(), jsonfile)
            self.series_to_send()
            return True
        except Exception as e:
            print(e, 'save_series')
            return False

    def series_to_send(self):
        # self.save_series()
        zipf = zipfile.ZipFile('tmp/%s.zip' % self.series_id, 'w', zipfile.ZIP_DEFLATED)
        current_dir = os.getcwd()
        os.chdir(self.path_to_series)
        for file in os.listdir(self.path_to_series):
            if '.dcm' in file or '.json' in file:
                zipf.write(file)
        zipf.close()
        os.chdir(current_dir)
