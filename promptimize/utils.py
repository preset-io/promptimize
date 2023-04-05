import json
import yaml
import hashlib
import json

from pygments import highlight
from pygments.lexers import YamlLexer, JsonLexer
from pygments.formatters import TerminalFormatter


def is_numeric(value):
    """that'd be nice if we had this in the std lib..."""
    return isinstance(value, (int, float, complex))


def is_iterable(obj):
    """that'd be nice if we had this in the std lib..."""
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def str_presenter(dumper, data):
    """
    Some hack to get yaml output to use look good for multiline,
    which is common in this package

    from: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
    """
    if len(data.splitlines()) > 1 or "\n" in data:
        text_list = [line.rstrip() for line in data.splitlines()]
        fixed_data = "\n".join(text_list)
        return dumper.represent_scalar("tag:yaml.org,2002:str", fixed_data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


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


def to_yaml(data, highlighted=True):
    data = yaml.dump(output, sort_keys=False)
    if highlighted:
        data = highlight(data, YamlLexer(), TerminalFormatter())
    return data


def to_json(data, highlighted=True):
    data = json.dumps(output, indent=2)
    highlighted = highlight(data, JsonLexer(), TerminalFormatter())
