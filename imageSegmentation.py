import SimpleITK as sitk
import pydicom as dicom


class ImageSegmentation:
    path_to_dicom_slices = None
    itk_dicom_slices = None
    array_dicom_slices = None

    def __init__(self, path_to_dicom_slices):
        self.path_to_dicom_slices = path_to_dicom_slices
        print(path_to_dicom_slices)

    def getArrayDicomFromPath(self):
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
