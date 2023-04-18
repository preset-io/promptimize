import yaml
from box import Box

from promptimize import utils


class Report:
    version = "0.1.0"

    def __init__(self, path=None, data=None):
        self.data = Box()
        if data:
            self.data = Box(data)
        self.path = path

    def write(self, path=None, style="yaml"):
        path = path or self.path
        with open(path, "w") as f:
            f.write(
                utils.serialize_object(
                    self.data.to_dict(), highlighted=False, style=style
                )
            )

    def merge(self, report):
        all_keys = set(report.prompts.keys()) | set(self.prompts.keys())
        for k in all_keys:
            a = report.prompts.get(k)
            b = self.prompts.get(k)
            if a and b:
                print(f"KEY_______{k}")
                if a.execution.get("run_at", "") > b.execution.get("run_at", ""):
                    self.prompts[k] = a
                else:
                    self.prompts[k] = b

            if not a:
                self.prompts[k] = b
            elif not b:
                self.prompts[k] = a

    @property
    def prompts(self):
        if self.data:
            return self.data.prompts
        return {}

    @classmethod
    def from_path(cls, path):
        try:
            with open(path, "r") as f:
                report = cls(path, yaml.safe_load(f))
            return report
        except FileNotFoundError:
            return None

    @classmethod
    def from_suite(cls, suite):
        report = cls(data=suite.to_dict())
        return report

    def get_prompt(self, prompt_key):
        return self.prompts.get(prompt_key)
