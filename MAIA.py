class MAIA:
    class ToolSettings:
        CancerSelectionPenSize = 2.0

    class WindowsSettings:
        PercentVisibleImageDicomViewer = 0.95

    class TextSetting:
        PatientInfoInPatientView = "<p style='color: black; font-size: 16px' > " \
                                   " PN: %s <br> BD: %s <br> Series:%s</p>"

        DicomViewerInitText = '<p align="center" style="font-size: 90px">' \
                              '<font face="Freestyle Script" color="darkgray"> %s </p>'
        NumberSliceViewerTest = "<font color='white'>Slice: %s</font>"
        DicomMetaDataText = "<p style='color: white; font-size: 12px' align='center'> %s: %s</p>"
        InformationMessage = "<p style='color: black; font-size: 14px' align='center'> %s</p>"
        ToolsLabelText = "<p style='color: white; font-size: 14px' align='center'>%s</p>"

    class SegmentationSettings:
        pass

    class ClassificationSettings:
        pass
