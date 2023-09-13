#!/usr/bin/env bash
# exit on error
set -o errexit
poetry install

sudo apt install python3-tk -y  