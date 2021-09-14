#!/bin/bash
set -eux

GITHUB_PUSH=${GITHUB_PUSH:-false}

SHELL_DIR=$(dirname $0)

USERNAME=${CIRCLE_PROJECT_USERNAME:-opspresso}
REPONAME=${CIRCLE_PROJECT_REPONAME:-helm-charts}

GIT_USERNAME="bot"
GIT_USEREMAIL="bot@nalbam.com"

rm -rf ${SHELL_DIR}/build

ALL_CHARTS=$(ls charts)

# Create a copy of each README.md files before running helm-docs
for chart in $ALL_CHARTS; do
  mkdir -p .charts/$chart
  cp charts/$chart/README.md .charts/$chart/README.md
done

# Run helm-docs to generate all README.md files from the template
helm-docs --log-level warning --template-files ./README.md.gotmpl

for chart in $ALL_CHARTS; do
  echo "Checking charts/$chart/README.md..."
  diff -s charts/$chart/README.md .charts/$chart/README.md > /dev/null
  if [ $? -eq 1 ]; then
    GITHUB_PUSH="true"
  fi
done

if [ "${GITHUB_PUSH}" == "true" ]; then
  git config --global user.name "${GIT_USERNAME}"
  git config --global user.email "${GIT_USEREMAIL}"

  git add .
  git commit -m "Publish charts"

  git push -q https://${GITHUB_TOKEN}@github.com/${USERNAME}/${REPONAME}.git gh-pages
fi
