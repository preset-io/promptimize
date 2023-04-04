import json
import yaml


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


class CustomDumper(yaml.Dumper):
    pass


def custom_scalar_representer(dumper, data):
    # data = data.replace('\\n', '\n')  # Replace escaped newline characters with actual newline characters
    style = None
    if "\n" in data:
        style = ">"
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style)
yaml.add_representer(str, custom_scalar_representer, Dumper=CustomDumper)


def try_to_json_parse(s):
    obj = None
    try:
        obj = json.loads(s)
    except Exception as e:
        print('o'*80)
        print(s)
        print('o'*80)
        print(e)
        print('o'*80)
    return obj

