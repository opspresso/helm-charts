#!/bin/bash
set -eux

SRCROOT="$(cd "$(dirname "$0")/.." && pwd)"
GIT_PUSH=${GIT_PUSH:-false}

rm -rf $SRCROOT/build && git clone -b gh-pages git@github.com:opspresso/helm-charts.git $SRCROOT/build

helm repo add stable https://kubernetes-charts.storage.googleapis.com
helm repo add opspresso https://opspresso.github.io/helm-charts

for dir in $(find $SRCROOT/charts -mindepth 1 -maxdepth 1 -type d);
do
    rm -rf $dir/charts

    name=$(basename $dir)

    if [ $(helm dep list $dir 2>/dev/null| wc -l) -gt 1 ]
    then
        # Bug with Helm subcharts with hyphen on them
        # https://github.com/argoproj/argo-helm/pull/270#issuecomment-608695684
        if [ "$name" == "argo-cd" ]
        then
            echo "Restore ArgoCD RedisHA subchart"
            git checkout $dir
        fi
        echo "Processing chart dependencies"
        helm --debug dep build $dir
    fi

    echo "Processing $dir"
    helm --debug package $dir
done

cp $SRCROOT/*.tgz build/
cd $SRCROOT/build && helm repo index .

cd $SRCROOT/build && git status

if [ "$GIT_PUSH" == "true" ]
then
    cd $SRCROOT/build && git add . && git commit -m "Publish charts" && git push git@github.com:opspresso/helm-charts.git gh-pages
fi
