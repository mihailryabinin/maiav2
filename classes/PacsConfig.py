from pynetdicom import AE
from pydicom.dataset import Dataset, DataElement
from copy import deepcopy


class PacsConfig:
    ip_address = None
    port = None
    ae_title = None
    context = None
    server_pacs = None
    patient_mask = None
    description = None

    def __init__(self, ip, port, ae_title, description, self_title='MAIA'):
        self.ip_address = ip
        self.port = port
        self.ae_title = ae_title
        self.description = description
        self.server_pacs = AE(self_title)
        self.add_context_to_pacs()
        self.patient_mask = Dataset()
        self.default_patient_mask()

    def add_context_to_pacs(self):
        self.context = [
            '1.2.840.10008.1.1',  # For connection
            '1.2.840.10008.5.1.4.1.2.2.1',  # For find with type S
            '1.2.840.10008.5.1.4.1.2.2.1',  # For find with type P
        ]
        for line in self.context:
            self.server_pacs.add_requested_context(line)

    def default_patient_mask(self):
        self.patient_mask.StudyDate = ''  # (0008,0020)
        self.patient_mask.PatientName = ''  # (0010,0010)
        self.patient_mask.PatientBirthDate = ''  # (0010,0030)
        self.patient_mask.PatientID = ''  # (0010,0020)
        self.patient_mask.StudyDescription = ''  # (0008,1030)
        self.patient_mask.AccessionNumber = ''  # (0008,0050)
        self.patient_mask.ReferringPhysicianName = ''  # (0008,0090)
        self.patient_mask.add(DataElement(0x00081060, 'PN', ''))  # (0008,1060)
        self.patient_mask.add(DataElement(0x00080080, 'LO', ''))  # InstitutionName
        self.patient_mask.add(DataElement(0x00081050, 'PN', ''))  # PerformingPhysicianName

        self.patient_mask.StudyInstanceUID = ''
        self.patient_mask.QueryRetrieveLevel = 'STUDY'

    def get_patient_mask(self, params=None):
        if params is None:
            params = dict()
        patient_mask = deepcopy(self.patient_mask)
        if type(params) is dict:
            for key, value in params.items():
                try:
                    patient_mask.data_element(key).value = value
                except Exception as e:
                    print(e)
            return patient_mask
        else:
            print('Not need type of patient param find')

    def pacs_c_find(self, params=None, query_model='S'):
        connection = self.get_connection()
        patient_mask = self.get_patient_mask(params)
        list_studies = []
        try:
            if connection.is_established:
                responses = connection.send_c_find(patient_mask, query_model=query_model)
                for (status, series) in responses:
                    if status.Status in (0xFF00, 0xFF01):
                        list_studies.append(series)
                connection.release()
                return list_studies
            else:
                print('Connection is not established')
                connection.release()
                return -1
        except Exception as e:
            print(e)
            connection.release()
            return -1

    def get_connection(self):
        return self.server_pacs.associate(addr=self.ip_address, port=self.port, ae_title=self.ae_title)
