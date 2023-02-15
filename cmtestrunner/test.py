import re


def object_modifier(obj, keys, value):
    temp = [obj]
    set_value = True
    for index, key in enumerate(keys):
        if re.match(r'^.*\[[0-9]+\]$', key):
            list_index = int(re.match(r'^(.*)\[([0-9]+)\]$', key)[2])
            attr = re.match(r'^(.*)(\[([0-9]+)\])$', key)[1]
            
            if len(temp[index].get(attr)) <= list_index:
                raise Exception('value is not replaceble in given object')

            if type(temp[index].get(attr)) is list and len(temp[index].get(attr)) > int(list_index):
                temp[index][attr][list_index] = object_modifier(temp[index].get(attr)[list_index], keys[index+1:], value)
                set_value = False
                break
        else:
            temp.append(temp[index].get(key))


    if set_value:
        temp[-1] = value

    count = len(temp) - 1
    while(count):
        temp[count-1][keys[count-1]] = temp[count]
        count-=1
    return temp[0]


def replace_attribute_value(obj, attributes):
    key_val = attributes.split('=')
    keys = key_val[0].split('.')
    value = key_val[1]
    return object_modifier(obj, keys, value)


obj = {
    'a':{
        'b': {
            'c': [2, 5, {
                'd': 8,
                'e': {
                    'f': [3, 6, 7, {
                        'g': 55,
                        'h': [{
                            'k':1
                        }]
                    }],
                    'm': 66
                }
            }, 7]
        }
    }
}

result = replace_attribute_value(obj, 'a.b.c[2].e.m=577777')
print(result)