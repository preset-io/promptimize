import yaml
from box import Box

import pandas as pd
from tabulate import tabulate

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
            for p in report.prompts.values():
                p.execution.test_results_avg = (
                    1 if p.execution.get("is_identical", False) is True else 0
                )
            return report
        except FileNotFoundError:
            return None

    @classmethod
    def from_suite(cls, suite):
        report = cls(data=suite.to_dict())
        return report

    def get_prompt(self, prompt_key):
        return self.prompts.get(prompt_key)

    def prompt_df(self):
        return pd.json_normalize(self.prompts.values())

    def print_summary(self, style="yaml"):
        df = self.prompt_df()
        weigthed_results = df["weight"] * df["execution.test_results_avg"]

        d = {
            "prompts": len(df),
            "weigthed_results": float(weigthed_results.sum()),
            "total_weight": float(df["weight"].sum()),
            "score": float(weigthed_results.sum() / df["weight"].sum()),
        }
        print(utils.serialize_object(d, highlighted=True, style=style))

        pt = df.pivot_table(
            index="prompt_kwargs.db_id",
            columns="execution.is_identical",
            values="key",
            aggfunc="count",
            fill_value=0,
        )
        print(tabulate(pt, headers="keys", showindex=True))
