#!/bin/bash

# Clean up the build/html directory
rm -rf build/html

# Build the documentation
make html

# Change to the build/html directory
cd build/html
touch .nojekyll

# Initialize a new Git repository
git init

# Add the generated files to the repository
git add .

# Commit the changes
git commit -a -m "Initial commit"

# Add the GitHub Pages remote repository
git remote add origin https://github.com/preset-io/promptimize.git

# Push the changes to the GitHub Pages repository
git push -f origin main:gh-pages

# Return to the original directory
cd ../..
