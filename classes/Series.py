import logging
import os
import zipfile
import json
import sys
import pydicom as dicom
import SimpleITK as sitk
import numpy as np
from classes.Volume import Volume
from pydicom.dataset import Dataset, FileDataset


class Series(object):
    series_id = None
    study_id = None
    metrics = None  # ?
    image = None
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
        current_path = os.getcwd()
        try:
            self.path_to_series = path_to_series
            series_reader = sitk.ImageSeriesReader()

            os.chdir(path_to_series)
            dicom_files_name = series_reader.GetGDCMSeriesFileNames('./')
            series_reader.SetFileNames(dicom_files_name)
            image = series_reader.Execute()
            os.chdir(current_path)

            meta_info = dicom.read_file('%s/%s' % (path_to_series, dicom_files_name[0]))
            self.meta_load(meta_info)
            self.image = np.array(sitk.GetArrayFromImage(image)[::-1], dtype=np.int16)
            self.series_info.update({'ImagesNumber': len(self.image),
                                     'ImageShape': self.image.shape[1:]})
            self.miniature = self.image[len(self.image) // 2] // 10 + 100
            self.loaded = True
            if 'series_info.json' in os.listdir(path_to_series):
                self.json_decode()
        except Exception as e:
            os.chdir(current_path)
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

    def get_list_contour_from_doctor(self):
        return [volume.get_coordinate() for volume in self.list_volumes if volume.is_doctor]

    def get_volume_size(self, coordinate):
        try:
            point_number = len(np.argwhere(self.image[coordinate[0, 0]:coordinate[1, 0],
                                           coordinate[0, 1]:coordinate[1, 1],
                                           coordinate[0, 2]:coordinate[1, 2]] > -150))
            point_number *= self.metrics.prod()
            return int(point_number)
        except Exception as e:
            print(e, 'get_volume_size')

    def get_volume_from_point(self, z, x, y):
        for volume in self.list_volumes:
            if volume.is_point_in_coordinate(z, x, y):
                return volume.json_code()

    def delete_volume_from_point(self, z, x, y):
        for volume, i in zip(self.list_volumes, range(len(self.list_volumes))):
            if volume.is_point_in_coordinate(z, x, y):
                self.list_volumes.pop(i)

    def save_series(self):
        try:
            if self.path_to_series != '':
                jsonfile = open(self.path_to_series + '/series_info.json', 'w')
                json.dump(self.json_code(), jsonfile)
                return True
            else:
                return False
        except Exception as e:
            print(e, 'save_series')
            return False

    def series_to_send_zip(self):
        current_dir = os.getcwd()
        try:
            zipf = zipfile.ZipFile('tmp/%s.zip' % self.series_id, 'w', zipfile.ZIP_DEFLATED)
            self.save_series()
            os.chdir(self.path_to_series)
            for file in os.listdir(self.path_to_series):
                if '.dcm' in file or '.json' in file:
                    zipf.write(file)
            zipf.close()
            os.chdir(current_dir)
            return 'tmp/%s.zip' % self.series_id
        except Exception as e:
            os.chdir(current_dir)
            print(e, 'series_to_send_zip')

    def json_code(self):
        try:
            list_volumes = [volume.json_code() for volume in self.list_volumes]
            file = {
                'Type': 'series',
                'SeriesID': self.series_id,
                'StudyID': self.study_id,
                'Information': self.series_info,
                'Metrics': self.metrics.tolist(),
                'Volumes': list_volumes
            }
            return file
        except Exception as e:
            print(e, 'json_code')
            return None

    def json_decode(self):
        try:
            file_name = '%s/series_info.json' % self.path_to_series
            with open(file_name, 'r') as json_file:
                file = json.load(json_file)
            self.series_from_dict(file)
        except Exception as e:
            print(e, 'json_decode')

    def series_from_dict(self, file):
        try:
            # self.series_id = file['SeriesID']
            # self.study_id = file['StudyID']
            # self.series_info = file['Information']
            self.metrics = np.array(file['Metrics'])
            list_volume = file['Volumes']
            for volume in list_volume:
                try:
                    self.add_value(volume['coordinate'], volume['volume_size'], volume['volume_type'],
                                   volume['probability'], volume['is_doctor'], volume['is_confirmed'])
                    if volume['information'] != dict([]):
                        self.list_volumes[-1].set_information(volume['information'])
                except Exception as e:
                    print(e, 'series_from_dict, for')
        except Exception as e:
            print(e, 'series_from_dict')
