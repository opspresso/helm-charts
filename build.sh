#!/bin/bash
set -eux

GITHUB_PUSH=${GITHUB_PUSH:-false}

SHELL_DIR=$(dirname $0)

USERNAME=${CIRCLE_PROJECT_USERNAME:-opspresso}
REPONAME=${CIRCLE_PROJECT_REPONAME:-helm-charts}

GIT_USERNAME="bot"
GIT_USEREMAIL="bot@nalbam.com"

rm -rf ${SHELL_DIR}/build

if [ "${GITHUB_PUSH}" == "true" ]; then
  git clone -b gh-pages git@github.com:${USERNAME}/${REPONAME}.git ${SHELL_DIR}/build
else
  mkdir ${SHELL_DIR}/build
fi

for dir in $(find ${SHELL_DIR}/charts -mindepth 1 -maxdepth 1 -type d);
do
    rm -rf $dir/charts

    name=$(basename $dir)

    if [ $(helm dep list $dir 2>/dev/null| wc -l) -gt 1 ]; then
        echo "Processing chart dependencies"
        helm --debug dep build $dir
    fi

    echo "Processing $dir"
    helm --debug package $dir
done

mv -f *.tgz ${SHELL_DIR}/build/

pushd ${SHELL_DIR}/build

helm repo index .

if [ "${GITHUB_PUSH}" == "true" ]; then
    git config --global user.name "${GIT_USERNAME}"
    git config --global user.email "${GIT_USEREMAIL}"

    git add .
    git commit -m "Publish charts"

    git push -q https://${GITHUB_TOKEN}@github.com/${USERNAME}/${REPONAME}.git gh-pages
fi

popd
