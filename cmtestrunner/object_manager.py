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
                    list_1[index] = self.modifier_str.replace('<<replace-here>>', str(list_1[index]))
                    list_2[index] = self.modifier_str.replace('<<replace-here>>', str(list_2[index]))


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
            self.matched = False
            self.obj_1 = self.modifier_str.replace('<<replace-here>>', str(self.obj_1))
            self.obj_2 = self.modifier_str.replace('<<replace-here>>', str(self.obj_2))
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
#     expected = {
#     "accessToken": "REGEX([A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12})",
#     "expiresInSecond": "3600",
#     "productName": "Merchant Till",
#     "featureList": [
#         {
#             "displayOrder": "1",
#             "featureCheck": None,
#             "featureId": "MY_QR",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "My QR"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "আমার QR"
#                 }
#             ]
#         },
#         {
#             "displayOrder": 2,
#             "featureCheck": None,
#             "featureId": "M2A",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "Agent Cash Out"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "এজেন্ট ক্যাশ আউট"
#                 }
#             ]
#         },
#         {
#             "displayOrder": 3,
#             "featureCheck": None,
#             "featureId": "M2M",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "M2M"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "মার্চেন্ট পেমেন্ট"
#                 }
#             ]
#         },
#         {
#             "displayOrder": 4,
#             "featureCheck": None,
#             "featureId": "PAYBILL",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "Paybill"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "পে বিল"
#                 }
#             ]
#         },
#         {
#             "displayOrder": 5,
#             "featureCheck": None,
#             "featureId": "PRA_SEND_MONEY",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "Send Money"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "সেন্ড মানি"
#                 }
#             ]
#         },
#         {
#             "displayOrder": 6,
#             "featureCheck": None,
#             "featureId": "COUNTER",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "Counter"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "কাউন্টার"
#                 }
#             ]
#         },
#         {
#             "displayOrder": 7,
#             "featureCheck": None,
#             "featureId": "VOID_TRANSACTION",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "Transaction Void"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "লেনদেন বাতিল"
#                 }
#             ]
#         }
#     ],
#     "updateTime": "REGEX([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}:[0-9]+ \\+0600)",
#     "status_code": "200",
#     "headers" : "REGEX(.*)"
# }
#     actual = {
#     "accessToken": "f213a961-efb3-5632-bcc1-ca2eb40514d3",
#     "expiresInSecond": "3600",
#     "featureList": [
#         {
#             "displayOrder": "1",
#             "featureCheck": None,
#             "featureId": "MY_QR",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "My QR"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "আমার QR"
#                 }
#             ]
#         },
#         {
#             "displayOrder": "2",
#             "featureCheck": None,
#             "featureId": "M2A",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "Agent Cash Out"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "এজেন্ট ক্যাশ আউট"
#                 }
#             ]
#         },
#         {
#             "displayOrder": "3",
#             "featureCheck": None,
#             "featureId": "M2M",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "M2M"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "মার্চেন্ট পেমেন্ট"
#                 }
#             ]
#         },
#         {
#             "displayOrder": "4",
#             "featureCheck": None,
#             "featureId": "PAYBILL",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "Paybill"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "পে বিল"
#                 }
#             ]
#         },
#         {
#             "displayOrder": "5",
#             "featureCheck": None,
#             "featureId": "PRA_SEND_MONEY",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "Send Money"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "সেন্ড মানি"
#                 }
#             ]
#         },
#         {
#             "displayOrder": "6",
#             "featureCheck": None,
#             "featureId": "COUNTER",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "Counter"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "কাউন্টার"
#                 }
#             ]
#         },
#         {
#             "displayOrder": "7",
#             "featureCheck": None,
#             "featureId": "VOID_TRANSACTION",
#             "enabled": True,
#             "labels": [
#                 {
#                     "language": "en",
#                     "value": "Transaction Void"
#                 },
#                 {
#                     "language": "bn",
#                     "value": "লেনদেন বাতিল"
#                 }
#             ]
#         }
#     ],
#     "headers": {
#         "Date": "Tue, 18 Oct 2022 10:43:28 GMT",
#         "Content-Type": "application/json",
#         "Content-Length": "1461",
#         "Connection": "keep-alive",
#         "x-amzn-RequestId": "87f9333a-7684-4c06-a2a5-6c6a70ed0d45",
#         "Referrer-Policy": "no-referrer",
#         "X-XSS-Protection": "1 ; mode=block",
#         "x-amzn-Remapped-Content-Length": "1461",
#         "X-Frame-Options": "DENY",
#         "x-amzn-Remapped-Connection": "keep-alive",
#         "x-amz-apigw-id": "aMl0bGVpyQ0FWVg=",
#         "Cache-Control": "no-cache, no-store, max-age=0, must-revalidate",
#         "Expires": "0",
#         "X-Content-Type-Options": "nosniff",
#         "Pragma": "no-cache",
#         "x-amzn-Remapped-Date": "Tue, 18 Oct 2022 10:43:28 GMT"
#     },
#     "productName": "Merchant Till",
#     "status_code": "200",
#     "updateTime": "2022-10-18 16:43:28:022 +0600"
# }
#     obj_manager = ObjectManager(actual, expected)
#     obj_manager.match_obj()
#     print(obj_manager.get_converted())
#     print(obj_manager.is_matched())
#     print(obj_manager.mismatched_keys())


# test_object_manager()