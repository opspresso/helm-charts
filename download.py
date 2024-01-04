#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import tarfile
import shutil


def get_charts(chart, version):
    os.popen(
        "helm pull '{}' --version {} --destination ./build/".format(chart, version)
    )


def main():
    os.makedirs("build", exist_ok=True)
    os.makedirs("charts", exist_ok=True)

    filepath = "versions.json"

    if os.path.exists(filepath):
        doc = None

        with open(filepath, "r") as file:
            doc = json.load(file)

            for k in doc["versions"]:
                chart = doc["versions"][k]["chart"]
                version = doc["versions"][k]["version"]

                name = chart.split("/")[1]

                chart_tgz = "./build/{}-{}.tgz".format(name, version)

                if os.path.exists(chart_tgz):
                    print("downloaded {}".format(chart_tgz))
                else:
                    print("downloading... {}".format(chart_tgz))
                    get_charts(chart, version)

                if os.path.exists(chart_tgz):
                    extract_path = "./charts/{}".format(name)

                    if os.path.exists(extract_path):
                        print("rmtree... {}".format(extract_path))
                        shutil.rmtree(extract_path)

                    os.makedirs(extract_path, exist_ok=True)

                    print("extract... {}".format(chart_tgz))

                    tar = tarfile.open(chart_tgz)
                    tar.extractall("./charts/")
                    tar.close()


if __name__ == "__main__":
    main()
