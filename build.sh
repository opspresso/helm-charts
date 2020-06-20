#!/bin/bash
set -eux

GIT_PUSH=${GIT_PUSH:-false}

SHELL_DIR=$(dirname $0)

rm -rf ${SHELL_DIR}/build

if [ "${GIT_PUSH}" == "true" ]; then
  git clone -b gh-pages git@github.com:opspresso/helm-charts.git ${SHELL_DIR}/build
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

if [ "${GIT_PUSH}" == "true" ]; then
    git add
    git commit -m "Publish charts"
    git push git@github.com:opspresso/helm-charts.git gh-pages
fi

popd
