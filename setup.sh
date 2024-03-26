#!/bin/bash

pip3 install -r requirements.txt
cargo install code2prompt
playwright install
python3 -m playwright install-deps
cd ui/
npm install
