

class CaseInsensitiveDict():
    def __init__(self, obj):
        self.obj = obj
        self.converted = dict()

    
    def convert_to_lower(self):
        pass

    def check_dict(self, obj):
        for key, val in obj:
            if type(val) == dict:
                self.converted[self.check_dict(val)] = val
            elif type(val) == list:
                self.check_list(val)
            else:
                return key.lower()

    def check_list(self, obj):
        pass
    