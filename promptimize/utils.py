import yaml


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


class CustomDumper(yaml.Dumper):
    def represent_scalar(self, tag, value, style=None):
        if style is None and "\n" in value:
            style = '>'
        return super().represent_scalar(tag, value, style)

CustomDumper.add_representer(str, CustomDumper.represent_scalar)
