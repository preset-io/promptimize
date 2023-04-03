import jinja2

environment = jinja2.Environment()


def process_template(template_as_string, **kwargs):
    template = environment.from_string(template_as_string)
    return template.render(**kwargs)
