#!/usr/bin/env bash

CUR_DIR="$(dirname "${BASH_SOURCE[0]}")"

OUTPUT_DIR="${CUR_DIR}/output"
if [ -d "$OUTPUT_DIR" ]; then
	rm -rf "$OUTPUT_DIR"
fi

mkdir "$OUTPUT_DIR"

echo "Copying static directories..."
cp -R "${CUR_DIR}/site/static/css" "$OUTPUT_DIR"
cp -R "${CUR_DIR}/site/static/images" "$OUTPUT_DIR"

echo "Generating html..."
cd "$CUR_DIR/site/html_generators"
pipenv run python3 generate_list.py -d
pipenv run python3 generate_people_list.py
