#!/usr/bin/env bash

CUR_DIR="$(realpath "$(dirname "${BASH_SOURCE[0]}")")"
cd "$CUR_DIR/site/html_generators"

pipenv run python3 generate_list.py -d
pipenv run python3 generate_people_list.py
