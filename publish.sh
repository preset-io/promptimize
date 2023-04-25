#!/bin/bash
git tag $PROMPTIMIZE_VERSION
git push origin $PROMPTIMIZE_VERSION
python setup.py sdist bdist_wheel
twine upload dist/promptimize-$PROMPTIMIZE_VERSION*
