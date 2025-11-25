#!/usr/bin/env bash
# exit on error
set -o errexit

# Install uv
pip install uv

# Install dependencies using uv
uv sync

# Any other build steps can go here
