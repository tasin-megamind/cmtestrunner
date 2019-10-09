
import json


mismatches = {}

def match_dict_obj(dict_1, dict_2):

    if type(dict_1) is not dict or type(dict_2) is not dict:
        return False

    if len(dict_2.keys()) > len(dict_1.keys()):
        temp = dict_1
        dict_1 = dict_2
        dict_2 = temp

    for key, val in dict_1.items():
        if (dict_2.get(key) != val):
            if not match_dict_obj(dict_1.get(key), dict_2.get(key)):
                mismatches[key] = [dict_1.get(key), dict_2.get(key)]
    
    if not mismatches:
        return True

    return False


dict_1 = {'a': 1, 'nested': {'b': {'f': 90}}, 'ok': 44}
dict_2 = {'a': 2, 'nested': {'b': 2}}

# print(match_dict_obj(dict_1, dict_2))

# print(mismatches)
dict_1 = json.dumps(dict_1, indent=4).split('\n')
dict_2 = json.dumps(dict_2, indent=4).split('\n')

if len(dict_1) > len(dict_2):
    dict_2 += [None] * (len(dict_1) - len(dict_2))
elif len(dict_2) > len(dict_1):
    dict_1 += [None] * (len(dict_2) - len(dict_1))

print(dict_1)
print(dict_2)
result = []
for index, item in enumerate(dict_1):
    if item != dict_2[index]:
        result.append(index)

print(result)