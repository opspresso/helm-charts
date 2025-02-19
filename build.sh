#!/bin/bash

GITHUB_PUSH=${GITHUB_PUSH:-false}

SHELL_DIR=$(dirname $0)

USERNAME=${CIRCLE_PROJECT_USERNAME:-opspresso}
REPONAME=${CIRCLE_PROJECT_REPONAME:-helm-charts}

GIT_USERNAME="nalbam-bot"
GIT_USEREMAIL="bot@nalbam.com"

while read LINE; do
  helm repo add ${LINE}
done <${SHELL_DIR}/repos.txt

for dir in $(find ${SHELL_DIR}/charts -mindepth 1 -maxdepth 1 -type d); do
  echo
  echo "Processing $dir"

  rm -rf $dir/charts

  name=$(basename $dir)

  if [ $(helm dep list $dir 2>/dev/null | wc -l) -gt 1 ]; then
    echo "Processing chart dependencies"
    helm --debug dep build $dir
  fi

  helm --debug package $dir
done

cp README.md ${SHELL_DIR}/build/
mv -f *.tgz ${SHELL_DIR}/build/

echo
pushd ${SHELL_DIR}/build

helm repo index .

if [ "${GITHUB_PUSH}" == "true" ]; then
  echo
  echo "Pushing to GitHub..."

  git config --global user.name "${GIT_USERNAME}"
  git config --global user.email "${GIT_USEREMAIL}"

  git add .
  git commit -m "Publish charts"

  git push -q https://${GITHUB_TOKEN}@github.com/${USERNAME}/${REPONAME}.git gh-pages
fi

popd
