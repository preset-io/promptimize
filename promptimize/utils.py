import json
import yaml
import hashlib


def is_numeric(value):
    return isinstance(value, (int, float, complex))


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def str_presenter(dumper, data):
    """https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data"""
    if len(data.splitlines()) > 1 or '\n' in data:
        text_list = [line.rstrip() for line in data.splitlines()]
        fixed_data = "\n".join(text_list)
        return dumper.represent_scalar('tag:yaml.org,2002:str', fixed_data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
yaml.add_representer(str, str_presenter)


def try_to_json_parse(s):
    obj = None
    try:
        obj = json.loads(s)
    except Exception as e:
        raise Exception("Not JSON")
    return obj


def short_hash(text, length=8):
    # Create a SHA-256 hash of the input string
    hash_object = hashlib.sha256(text.encode())

    # Convert the hash to a hexadecimal string
    hex_hash = hash_object.hexdigest()

    # Take a substring of the hex hash for a shorter version
    return hex_hash[:length]
