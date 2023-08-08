import json
import re
import random
import copy

BOOL = {
    'true': True,
    'True': True,
    'false': False,
    'False': False,
    'None': False,
    'none': False
}

class JsonTraverser():

    # object, find_with_regex(must contain only one group), replace_with
    def __init__(self, **kwargs):
        self.object = kwargs['object']
        self.find_with_regex = kwargs['find_with_regex']
        self.replace_with = kwargs['replace_with']


    def get_attribute_value_from_json(self, json_obj, attribute_path):
        if attribute_path and (type(json_obj) is dict or isinstance(json_obj, dict)):
            attribute_value = json_obj
            attribute_path = attribute_path.split('.')
            for attribute in attribute_path:
                list_available = re.match(r'^(.*)\[([0-9]+)\]$', attribute)
                index = None
                if list_available:
                    attribute = list_available[1]
                    index = int(list_available[2])

                # if type(attribute_value) is dict:
                attribute_value = attribute_value.get(attribute)
                if index is not None:
                    attribute_value = attribute_value[index]
            
            return attribute_value

        raise Exception('get_attribute_value_from_json: argument error')

    def interpret_default(self, data):
        if type(data) is not str:
            return data
        if re.match(r'random\((.*, [0-9]+)\)', data):
            matched = re.match(r'random\((.*), ([0-9]+)\)', data)
            random_str = ''.join(random.choice(matched[1]) for _ in range(int(matched[2])))
            return random_str
        elif re.match(r'integer\(([0-9]+)\)', data):
            return int(re.match(r'integer\(([0-9]+)\)', data)[1])
        elif re.match(r'bool\((.*)\)', data):
            return BOOL.get(re.match(r'bool\((.*)\)', data)[1])
        else:
            return data


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
                obj[key] = self.interpret_default(value)
                if re.match(r''+self.find_with_regex, str(value)):
                    var = re.match(r''+self.find_with_regex, str(value))[1]
                    # obj[key] = self.replace_with.get(var)
                    obj[key] = self.get_attribute_value_from_json(self.replace_with, var)


    def __list_parser(self, obj):
        for index, item in enumerate(obj):
            if type(item) is list:
                self.__list_parser(item)
            elif type(item) is dict:
                self.__dict_parser(item)
            else:
                obj[index] = self.interpret_default(item)
                if re.match(r''+self.find_with_regex, str(item)):
                    var = re.match(r''+self.find_with_regex, str(item))[1]
                    obj[index] = self.get_attribute_value_from_json(self.replace_with, var)




## test
# object = [
#     'bool(true)',
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