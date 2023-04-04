from setuptools import setup, find_packages

# Read the contents of the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='promptimize',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'promptimize=promptimize:cli',
            'p9e=promptimize:cli',
        ],
    },
    author='Maxime Beauchemin',
    author_email='maximebeauchemin@gmail.com',
    description='A python framework to generate and evaluate prompts for GPT at scale',
)
