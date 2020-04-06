
import json
import copy
import re
import collections



class ObjectManager():

    def __init__(self, obj_x, obj_y, modifier_str=None):
        self.obj_1 = copy.deepcopy(obj_x)
        self.obj_2 = copy.deepcopy(obj_y)
        if modifier_str:
            self.modifier_str = modifier_str
        else:
            self.modifier_str = "<span class='text-danger'><<replace-here>></span>"
                
        self.matched = True
        self.mismatch_keys = []


    def match_schema(self, val_1, val_2):
        # match datetime +/- offset
        # match time +/- offset
        # match random token(regex)
        # match any value exists
        regex_found = re.match(r'REGEX\((.*)\)', str(val_2))
        
        if regex_found:
            regex = regex_found[1]
            return re.match(r'{}'.format(regex), str(val_1)) is not None




    def match_dict_obj(self, dict_1, dict_2):
        if dict_1 == dict_2:
            return True
        
        keys = list(set(dict_1.keys()) | set(dict_2.keys()))
        
        for key in keys:
            if dict_1.get(key) != dict_2.get(key):          
                if type(dict_1.get(key)) is list and type(dict_2.get(key)) is list:
                    self.match_list_obj(dict_1.get(key), dict_2.get(key))
                elif type(dict_1.get(key)) is dict and type(dict_2.get(key)) is dict:
                    self.match_dict_obj(dict_1.get(key), dict_2.get(key))
                elif self.match_schema(dict_1.get(key), dict_2.get(key)):
                    continue
                else:
                    self.mismatch_keys.append(key)
                    self.matched = False
                    dict_1[key] = self.modifier_str.replace('<<replace-here>>', str(dict_1.get(key)))
                    dict_2[key] = self.modifier_str.replace('<<replace-here>>', str(dict_2.get(key)))
                    # dict_1[key] = "<span class='text-danger'>" + str(dict_1.get(key)) + '</span>'
                    # dict_2[key] = "<span class='text-danger'>" + str(dict_2.get(key)) + '</span>'


    
    def match_list_obj(self, list_1, list_2):

        if list_1 == list_2:
            return True

        if len(list_2) > len(list_1):
            list_1 += [None] * (len(list_2) - len(list_1))
        if len(list_1) > len(list_2):
            list_2 += [None] * (len(list_1) - len(list_2))
        
        for index, element in enumerate(list_1):
            if element != list_2[index]:
                if type(element) is dict and type(list_2[index]) is dict:
                    self.match_dict_obj(element, list_2[index])
                elif type(element) is list and type(list_2[index]) is list:
                    self.match_list_obj(element, list_2[index])
                elif self.match_schema(element, list_2[index]):
                    continue
                else:
                    self.matched = False
                    list_1[index] = "<span class='text-danger'>" + str(list_1[index]) + '</span>'
                    list_2[index] = "<span class='text-danger'>" + str(list_2[index]) + '</span>'


    def match_obj(self):

        if self.obj_1 == self.obj_2:
            # self.matched = True
            return True

        if type(self.obj_1) is not type(self.obj_2):
            self.mismatch_keys.append('whole object mismatch')
            print('Can not compare two different type of objects')
            return False

        if not self.obj_1 or not self.obj_2:
            # self.mismatches.append([obj_1, obj_2])
            return False


        if type(self.obj_1) is list:
            self.match_list_obj(self.obj_1, self.obj_2)

        if type(self.obj_2) is dict:
            self.obj_1 = dict(collections.OrderedDict(sorted(self.obj_1.items())))
            self.obj_2 = dict(collections.OrderedDict(sorted(self.obj_2.items())))
            self.match_dict_obj(self.obj_1, self.obj_2)





    def get_converted(self):
        return self.obj_1, self.obj_2

    def is_matched(self):
        return self.matched

    def mismatched_keys(self):
        return list(set(self.mismatch_keys))


# def test_object_manager():
#     obj_2 = {
#         'a': 'test',
#         'b': 'REGEX([0-9]+)',
#         'c': 'REGEX(^[0-9]$)',
#     }

#     obj_1 = {
#         'a': 'test',
#         'b': 23432,
#         'c': 2222
#     }
#     obj_manager = ObjectManager(obj_1, obj_2)
#     obj_manager.match_obj()
#     print(obj_manager.get_converted())
#     print(obj_manager.is_matched())


# test_object_manager()