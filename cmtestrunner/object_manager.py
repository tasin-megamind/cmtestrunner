
import json
import copy




class ObjectManager():

    def __init__(self, obj_x, obj_y):
        self.obj_1 = copy.deepcopy(obj_x)
        self.obj_2 = copy.deepcopy(obj_y)
        self.matched = False
        self.match_obj()


    def match_dict_obj(self, dict_1, dict_2):
        if dict_1 == dict_2:
            return True

        if len(dict_2.keys()) > len(dict_1.keys()):
            temp = dict_1
            dict_1 = dict_2
            dict_2 = temp
        
        keys = list(set(dict_1.keys()) | set(dict_2.keys()))
        
        for key in keys:
            print(key)
            if dict_1.get(key) != dict_2.get(key):
                if type(dict_1.get(key)) is list and type(dict_2.get(key)) is list:
                    self.match_list_obj(dict_1.get(key), dict_2.get(key))
                elif type(dict_1.get(key)) is dict and type(dict_2.get(key)) is dict:
                    self.match_dict_obj(dict_1.get(key), dict_2.get(key))
                else:
                    dict_1[key] = "<span class='text-danger'>" + str(dict_1.get(key)) + '</span>'
                    dict_2[key] = "<span class='text-danger'>" + str(dict_2.get(key)) + '</span>'


    
    def match_list_obj(self, list_1, list_2):

        if list_1 == list_2:
            return True

        if len(list_2) > len(list_1):
            list_1 += [None] * (len(list_2) - len(list_1))
        if len(list_1) > len(list_2):
            list_2 += [None] * (len(list_1) - len(list_2))
        
        for index, element in enumerate(list_1):
            if element != list_2[index]:
                if type(element) is dict or type(list_2[index]) is dict:
                    self.match_dict_obj(element, list_2[index])
                elif type(element) is list and type(list_2[index]) is list:
                    self.match_list_obj(element, list_2[index])
                else:
                    list_1[index] = "<span class='text-danger'>" + str(list_1[index]) + '</span>'
                    list_2[index] = "<span class='text-danger'>" + str(list_2[index]) + '</span>'


    def match_obj(self):

        if self.obj_1 == self.obj_2:
            self.matched = True
            return True

        if type(self.obj_1) is not type(self.obj_2):
            print('Can not compare two different type of objects')
            return False

        if not self.obj_1 or not self.obj_2:
            # self.mismatches.append([obj_1, obj_2])
            return False


        if type(self.obj_1) is list:
            self.match_list_obj(self.obj_1, self.obj_2)

        if type(self.obj_2) is dict:
            self.match_dict_obj(self.obj_1, self.obj_2)




    def get_converted(self):
        return self.obj_1, self.obj_2

    def is_matched(self):
        return self.matched
