import json
import re

class JsonTraverser():

    # object, find_with_regex(must contain only one group), replace_with
    def __init__(self, **kwargs):
        self.object = kwargs['object']
        self.find_with_regex = kwargs['find_with_regex']
        self.replace_with = kwargs['replace_with']

    def get_analyzed(self):
        return self.object
        
    def play(self):
        try:
            json.dumps(self.object)
        except Exception as e:
            raise Exception('Invalid JSON Object')

        if type(self.object) is list:
            self.__list_parser(self.object)
        elif type(self.object) is dict:
            self.__dict_parser(self.object)

    def __dict_parser(self, obj):
        for key, value in obj.items():
            if type(value) is list:
                self.__list_parser(value)
            elif type(value) is dict:
                self.__dict_parser(value)
            else:
                if re.match(r''+self.find_with_regex, str(value)):
                    var = re.match(r''+self.find_with_regex, str(value))[1]
                    obj[key] = self.replace_with.get(var)


    def __list_parser(self, obj):
        for index, item in enumerate(obj):
            if type(item) is list:
                self.__list_parser(item)
            elif type(item) is dict:
                self.__dict_parser(item)
            else:
                if re.match(r''+self.find_with_regex, str(item)):
                    var = re.match(r''+self.find_with_regex, str(item))[1]
                    obj[index] = self.replace_with.get(var)




## test
# object = [
#     'test',
#     12,
#     {
#         'o1': 'Context.abc'
#     },
#     [
#         'Context.abc', 'afadgds', {'o2': 'Context.abc'}
#     ]
# ]

# context = {
#     'abc': 'okay'
# }
    

# regex = 'Context\.(.*)'
# manager = JsonTraverser(object=object, find_with_regex=regex, replace_with=context)
# manager.play()
# print(manager.get_analyzed())