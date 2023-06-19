#!/bin/bash

# FIRST! manually update the setup.py with the version number
# export PROMPTIMIZE_VERSION=0.2.3

git commit -a -m "Version $PROMPTIMIZE_VERSION"
git tag $PROMPTIMIZE_VERSION
git push origin $PROMPTIMIZE_VERSION
python setup.py sdist bdist_wheel
twine upload dist/promptimize-$PROMPTIMIZE_VERSION*
