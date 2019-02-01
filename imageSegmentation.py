import SimpleITK as sitk
import pydicom as dicom
import collections
import numpy as np
import os
from Classes.Series import Series
from Classes.FolderDownload import FolderDownload
from Classes.PacsDownload import PacsDownload


class ImageSegmentation:
    path_to_dicom_slices = None
    itk_dicom_slices = None
    array_dicom_slices = None
    dicom_data_dictionary = None
    dicom_meta_metric = None

    def __init__(self, path_to_dicom_slices):
        self.path_to_dicom_slices = path_to_dicom_slices
        print(path_to_dicom_slices)

    def getArrayDicomFromPath(self):
        conf_pacs = dict([
            ('ip', '192.168.96.18'),
            ('port', 3002),
            ('ae_title', 'PACS'),
            ('description', 'Oncocentr')
        ])
        downloder = PacsDownload()
        downloder.add_pacs(conf_pacs)

        dicom_reader = sitk.ImageSeriesReader()
        dicom_files_name = dicom_reader.GetGDCMSeriesFileNames(self.path_to_dicom_slices)
        dicom_reader.SetFileNames(dicom_files_name)
        self.itk_dicom_slices = dicom_reader.Execute()

        dicom_file_name = sitk.ImageSeriesReader().GetGDCMSeriesFileNames(self.path_to_dicom_slices)[0]
        mmetadata_from_dicom = dicom.read_file(dicom_file_name)
        x = float(getattr(mmetadata_from_dicom, 'SliceThickness', '0')) + float(
            getattr(mmetadata_from_dicom, 'spacingBetweenSlices', '0'))

        x = int(x + 0.6)
        self.itk_dicom_slices = sitk.Expand(self.itk_dicom_slices, (1, 1, x), sitk.sitkNearestNeighbor)
        if x > 2:
            self.itk_dicom_slices = sitk.CurvatureFlow(image1=self.itk_dicom_slices,
                                                       timeStep=0.2,
                                                       numberOfIterations=2)
        self.array_dicom_slices = sitk.GetArrayFromImage(self.itk_dicom_slices)[::-1]

        return self.array_dicom_slices

    def getDicomMetaData(self):
        self.dicom_data_dictionary = collections.OrderedDict([
            # ('PatientID', 0),
            ('PatientName', 0),
            ('PatientSex', 0),
            ('PatientAge', 0),
            ('PatientBirthDate', 0),
            ('ContentDate', 0),
            # ('ContrastBolusAgent', 0),
            # ('ContrastBolusRoute', 0),
            # ('Manufacturer', 0),
            # ('ManufacturerModelName', 0),
        ])
        # dicom_file_name = sitk.ImageSeriesReader().GetGDCMSeriesFileNames(self.path_to_dicom_slices)[0]
        # mmetadata_from_dicom = dicom.read_file(dicom_file_name)
        # z, y = getattr(mmetadata_from_dicom, 'PixelSpacing', '0')
        # x = float(getattr(mmetadata_from_dicom, 'SliceThickness', '0')) + float(
        #     getattr(mmetadata_from_dicom, 'spacingBetweenSlices', '0'))
        # self.dicom_meta_metric = np.array([x, float(y), float(z)])
        # np.save('metric', self.dicom_meta_metric)
        # # self.convolutionTest()
        # for key, _ in self.dicom_data_dictionary.items():
        #     value = getattr(mmetadata_from_dicom, key, '')
        #     self.dicom_data_dictionary.update({key: value})
        return self.dicom_data_dictionary
