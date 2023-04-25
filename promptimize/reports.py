import yaml
from box import Box

import pandas as pd

from promptimize import utils


class Report:
    """Report objects interacting with the filesystem / databases and data structures"""

    version = "0.1.0"

    def __init__(self, path=None, data=None):
        self.data = Box()
        if data:
            self.data = Box(data)
        self.path = path

    def write(self, path=None, style="yaml"):
        """write the report to the filesystem"""
        path = path or self.path
        with open(path, "w") as f:
            f.write(utils.serialize_object(self.data.to_dict(), highlighted=False, style=style))

    def merge(self, report):
        """merge in another report into this one"""
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
        """list the prompts in this report"""
        if self.data:
            return self.data.prompts
        return {}

    @property
    def failed_keys(self):
        """return the list of prompt keys that have not suceeded"""
        keys = set()
        for p in self.prompts.values():
            if p.execution.get("score", 0) < 1:
                keys.add(p.key)
        return keys

    @classmethod
    def from_path(cls, path):
        """load a report object from a path in the filesystem"""
        try:
            with open(path, "r") as f:
                report = cls(path, yaml.safe_load(f))
            return report
        except FileNotFoundError:
            return None

    @classmethod
    def from_suite(cls, suite):
        """load a report object from a suite instance"""
        report = cls(data=suite.to_dict())
        return report

    def get_prompt(self, prompt_key):
        """get a specific prompt data structure from the report"""
        return self.prompts.get(prompt_key)

    def prompt_df(self):
        """make a flat pandas dataframe out of the prompts in the reports"""
        prompts = [p for p in self.prompts.values() if p.execution]
        return pd.json_normalize(prompts)

    def print_summary(self, groupby="category"):
        """print the summary from the report"""
        if groupby:
            self.print_summary(groupby=None)

        df = self.prompt_df()

        df["score"] = df["weight"] * df["execution.score"]

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
