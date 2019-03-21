from classes.PacsConfig import PacsConfig


class PacsDownload(object):
    list_pacs = None

    def __init__(self):
        super().__init__()
        self.list_pacs = []

    def add_pacs(self, pacs_config):
        if type(pacs_config) is dict:
            try:
                new_pacs = PacsConfig(ip=pacs_config['ip'], port=pacs_config['port'],
                                      ae_title=pacs_config['ae_title'],
                                      description=pacs_config['description'])
                self.list_pacs.append(new_pacs)
            except Exception as e:
                print(e)
                return -1

    def del_pacs(self, number):
        self.list_pacs.pop(number)

    def find_in_pacs(self, find_param=None):
        result = []
        if len(self.list_pacs) > 0:
            for pacs in self.list_pacs:
                try:
                    result.append(pacs.pacs_c_find(find_param))
                except Exception as e:
                    print(e)

            return result
        else:
            return -1
