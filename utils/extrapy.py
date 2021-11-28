
def format_string(string):
    return string.replace('_', ' ').lower().title()


def add_to_list_elements(list, prefix='', suffix=''):
    for i, element in enumerate(list):
        list[i] = str(prefix) + element + str(suffix)
    return list
