#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import yaml


GRAY = "\033[90m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_chart_version(chart, name):
    txt = os.popen("helm search repo '{}' -o json".format(chart)).read()

    charts = json.loads(txt)

    new_ver = ""
    new_app = ""

    for one in charts:
        if one["name"] == chart:
            new_ver = one["version"]
            new_app = one["app_version"]
            break

    return new_ver, new_app


def get_oci_version(chart, name):
    txt = os.popen("helm show chart oci://{}/{}".format(chart, name)).read()

    docs = yaml.unsafe_load(txt)

    new_ver = docs["version"]
    new_app = docs["appVersion"]

    return new_ver, new_app


def get_latest_version(chart, name, type="https"):
    if type == "oci":
        new_ver, new_app = get_oci_version(chart, name)
    else:
        new_ver, new_app = get_chart_version(chart, name)

    return new_ver, new_app


def print_version(name, old_ver, old_app, new_ver, new_app, is_fixed=False):
    old_txt = old_ver
    if old_app != "":
        old_txt = old_ver + " (" + old_app + ")"

    new_txt = new_ver
    if new_app != "":
        new_txt = new_ver + " (" + new_app + ")"

    if new_ver != old_ver or new_app != old_app:
        if is_fixed:
            print(
                "{:45} {:20} -- {}{:20}{}".format(name, old_txt, GRAY, new_txt, RESET)
            )
        else:
            print("{:45} {:20} -> {:20}".format(name, old_txt, new_txt))
    else:
        print("{:45} {:20}".format(name, old_txt))


def main():
    filepath = "versions.json"

    if os.path.exists(filepath):
        doc = None

        with open(filepath, "r") as file:
            doc = json.load(file)

            for k in doc["versions"]:
                chart = doc["versions"][k]["chart"]

                old_ver = doc["versions"][k]["version"]
                old_app = ""
                if "app_version" in doc["versions"][k]:
                    old_app = doc["versions"][k]["app_version"]

                new_ver = ""
                new_app = ""

                is_fixed = False

                if (
                    "fixed" in doc["versions"][k]
                    and doc["versions"][k]["fixed"] == True
                ):
                    is_fixed = True

                type = "https"
                if "type" in doc["versions"][k]:
                    type = doc["versions"][k]["type"]

                # latest version
                new_ver, new_app = get_latest_version(chart, k, type)

                # replace
                if new_ver != "":
                    if is_fixed != True:
                        doc["versions"][k]["version"] = new_ver
                        doc["versions"][k]["app_version"] = new_app

                print_version(k, old_ver, old_app, new_ver, new_app, is_fixed)

        if doc != None:
            with open(filepath, "w") as file:
                json.dump(doc, file, sort_keys=True, indent=2)


if __name__ == "__main__":
    main()
