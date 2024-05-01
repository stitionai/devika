#!/bin/sh

# Activate Miniconda environment
eval "$(conda shell.bash activate "$VENV_NAME")"

echo current directory is: $(pwd)

if [ -n ${DEBUG} ]; then 
  set -eux;
  nvidia-smi
  which python3
  pip show transformers
fi

echo "Upating Playwright Chromium browser\nPlease wait..."
# Not found if installed at build stage
playwright install --with-deps chromium > /dev/null

python3 -m devika

