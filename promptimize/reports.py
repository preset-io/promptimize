import yaml
from box import Box

import pandas as pd

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

    @property
    def failed_keys(self):
        keys = set()
        for p in self.prompts.values():
            if p.execution.get("test_results_avg", 0) < 1:
                keys.add(p.key)
        return keys

    @classmethod
    def from_path(cls, path):
        try:
            with open(path, "r") as f:
                report = cls(path, yaml.safe_load(f))
            # report.fix_stuff()
            return report
        except FileNotFoundError:
            return None

    @classmethod
    def from_suite(cls, suite):
        report = cls(data=suite.to_dict())
        return report

    def fix_stuff(self):
        # DELETEME
        for p in self.prompts.values():
            if (
                p.execution.get("is_identical")
                and p.execution.get("test_results_avg") == 0
            ):
                p.execution.test_results_avg = 1
        self.write()

    def get_prompt(self, prompt_key):
        return self.prompts.get(prompt_key)

    def prompt_df(self):
        prompts = [p for p in self.prompts.values() if p.execution]
        return pd.json_normalize(prompts)

    def print_summary(self, groupby=None):

        if groupby:
            self.print_summary(groupby=None)

        df = self.prompt_df()
        weigthed_results = df["weight"] * df["execution.test_results_avg"]

        df["score"] = df["weight"] * df["execution.test_results_avg"]

        if groupby:
            df = df[[groupby, "weight", "score"]].groupby(groupby).sum()
        else:
            df = df.agg({"weight": "sum", "score": "sum"}).to_frame().T
        df["perc"] = (df["score"] / df["weight"]) * 100
        df = df.sort_values(by="weight", ascending=False)
        headers = []
        if groupby:
            headers = "keys"
        else:
            df = df.T
        print(utils.trabulate(df, headers=headers))
