#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json


def get_charts(chart):
    txt = os.popen("helm search repo '{}' -o json".format(chart)).read()

    return json.loads(txt)


def main():
    filepath = "versions.json"

    if os.path.exists(filepath):
        doc = None

        with open(filepath, "r") as file:
            doc = json.load(file)

            for k in doc["versions"]:
                chart = doc["versions"][k]["chart"]

                old_ver = doc["versions"][k]["version"]
                new_ver = ""

                # search
                json = get_charts(chart)

                for one in json:
                    if one["name"] == chart:
                        new_ver = one["version"]

                # replace
                if new_ver != "":
                    if new_ver != old_ver:
                        print("{:50} {:10} -> {:10}".format(chart, old_ver, new_ver))
                    else:
                        print("{:50} {:10}".format(chart, old_ver))

                    doc["versions"][k]["version"] = new_ver

        if doc != None:
            with open(filepath, "w") as file:
                json.dump(doc, file, sort_keys=True, indent=2)


if __name__ == "__main__":
    main()
