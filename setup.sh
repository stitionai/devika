#!/bin/bash

# This script is used to install the project in development mode or normal mode
function install_normal {
    pip3 install .
    playwright install
    python3 -m playwright install-deps
    cd ui/ || exit 1
    npm install
}

function install_dev {
    pip3 install -e ".[dev]"
    pre-commit install
    playwright install
    python3 -m playwright install-deps
    cd ui/ || exit 1
    npm install
}

if [ "$1" == "--dev" ]; then
    printf '\033[0;32m%s\033[0m\n' "Installing in development mode"
    install_dev
else
    printf '\033[0;31m%s\033[0m\n' "Installing in normal mode"
    install_normal
fi
