#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json


def get_charts(name):
    txt = os.popen("helm search repo '{}' -o json".format(name)).read()

    return json.loads(txt)


def main():
    filepath = "versions.json"

    if os.path.exists(filepath):
        doc = None

        with open(filepath, "r") as file:
            doc = json.load(file)

            for k in doc["versions"]:
                name = doc["versions"][k]["chart"]

                old_ver = doc["versions"][k]["version"]
                old_app = ""
                if "app_version" in doc["versions"][k]:
                    old_app = doc["versions"][k]["app_version"]

                new_ver = ""
                new_app = ""

                # search
                charts = get_charts(name)

                for one in charts:
                    if one["name"] == name:
                        new_ver = one["version"]
                        new_app = one["app_version"]

                # replace
                if new_ver != "":
                    doc["versions"][k]["version"] = new_ver
                    doc["versions"][k]["app_version"] = new_app

                    old_txt = old_ver + " (" + old_app + ")"
                    new_txt = new_ver + " (" + new_app + ")"

                    if new_ver != old_ver or new_app != old_app:
                        print("{:45} {:20} -> {:20}".format(name, old_txt, new_txt))
                    else:
                        print("{:45} {:20}".format(name, old_txt))

        if doc != None:
            with open(filepath, "w") as file:
                json.dump(doc, file, sort_keys=True, indent=2)


if __name__ == "__main__":
    main()
