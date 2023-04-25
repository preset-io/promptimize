from setuptools import setup, find_packages

# Read the contents of the requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Read the contents of the README.md file
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="promptimize",
    version="0.2.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "promptimize=promptimize:cli",
            "p9e=promptimize:cli",
        ],
    },
    author="Maxime Beauchemin",
    author_email="maximebeauchemin@gmail.com",
    description="A python toolkit to generate and evaluate prompts for GPT at scale",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="Apache License, Version 2.0",
    license_file="LICENSE",
)
