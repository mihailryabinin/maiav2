class MAIA:
    class ToolSettings:
        CancerSelectionPenSize = 2.0

    class WindowsSettings:
        PercentWidthForWindowImageSlice = 0.90
        PercentToolsWidget = 0.1
        PercentWidth3DViewer = 1 - PercentWidthForWindowImageSlice - PercentToolsWidget
        SpacePointsBetween2DImages = 10
        PercentHeightForViewers = 0.85

    class TextSetting:
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
