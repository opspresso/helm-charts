#!/bin/sh

set -eu

rm -rf .charts

ALL_CHARTS=$(ls charts)

# Create a copy of each README.md files before running helm-docs
for chart in $ALL_CHARTS; do
  mkdir -p .charts/$chart
  cp charts/$chart/README.md .charts/$chart/README.md
done

# Run helm-docs to generate all README.md files from the template
helm-docs --log-level warning --template-files ./ci/README.md.gotmpl

# Check all README.md files for changes after running helm-docs
set +e
for chart in $ALL_CHARTS; do
  echo "Checking charts/$chart/README.md..."
  diff -s charts/$chart/README.md .charts/$chart/README.md > /dev/null
  if [ $? -eq 1 ]; then
    echo "🔴 Error: file charts/$chart/README.md needs to be updated: "
    diff charts/$chart/README.md .charts/$chart/README.md
    echo "See main repo README.md for instructions"
    rm -rf .charts
    exit 1
  fi
done

rm -rf .charts

echo "✅ All chart README.md files are up to date"

exit 0
