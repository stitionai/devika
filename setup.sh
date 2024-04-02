#!/bin/bash

pip3 install -r requirements.txt
playwright install
python3 -m playwright install-deps
cd ui/
bun install
