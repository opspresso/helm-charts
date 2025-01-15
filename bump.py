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


def print_version(name, old_ver, old_app, new_ver, new_app, locked):
    sign = ""

    old_txt = old_ver
    if old_app != "":
        old_txt = old_ver + " (" + old_app + ")"

    new_txt = new_ver
    if new_app != "":
        new_txt = new_ver + " (" + new_app + ")"

    if new_ver != old_ver:
        if locked:
            sign = "🔒"
        print(
            "{:40} {:10} {:5} {}{:20}{}".format(
                name, old_txt, sign, YELLOW, new_txt, RESET
            )
        )
    else:
        sign = "✅"
        print("{:40} {}{:10}{} {:5}".format(name, YELLOW, old_txt, RESET, sign))

    version_line = "| {} | {} | {} | {} |".format(name, sign, old_txt, new_txt)

    return version_line


def update_version_in_readme(version_content, file_path="README.md"):
    # file_path = "README.md"

    # 파일을 읽어들입니다.
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # 시작 및 종료 태그를 정의합니다.
    begin_tag = "<!--- BEGIN_VERSION --->"
    end_tag = "<!--- END_VERSION --->"

    # 시작 및 종료 태그의 위치를 찾습니다.
    begin_index = content.find(begin_tag)
    end_index = content.find(end_tag)

    # 태그가 존재하는지 확인합니다.
    if begin_index == -1 or end_index == -1:
        raise ValueError("BEGIN_VERSION 또는 END_VERSION 태그를 찾을 수 없습니다.")

    # 새로운 콘텐츠를 삽입합니다.
    new_content = (
        content[: begin_index + len(begin_tag)]
        + "\n"
        + version_content
        + "\n"
        + content[end_index:]
    )

    # 파일에 새로운 내용을 씁니다.
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_content)


def get_local_version(chart_path):
    version = ""
    app_version = ""

    if os.path.exists(chart_path):
        with open(chart_path, "r") as file:
            chart_doc = yaml.unsafe_load(file)

            if "version" in chart_doc:
                version = chart_doc["version"]

            if "appVersion" in chart_doc:
                app_version = chart_doc["appVersion"]

    return version, app_version


def main():
    file_path = "versions.json"

    if os.path.exists(file_path):
        doc = None

        version_contents = []
        version_contents.append("| NAME | | CURRENT | LATEST |")
        version_contents.append("| --- | - | --- | --- |")

        with open(file_path, "r") as file:
            doc = json.load(file)

            for k in doc["versions"]:
                chart = doc["versions"][k]["chart"]

                if "path" in doc["versions"][k]:
                    path = doc["versions"][k]["path"]
                else:
                    path = k

                chart_path = "../argocd-env-addons/charts/" + path + "/Chart.yaml"

                old_ver, old_app = get_local_version(chart_path)

                new_ver = ""
                new_app = ""

                type = "https"
                if "type" in doc["versions"][k]:
                    type = doc["versions"][k]["type"]

                if "locked" in doc["versions"][k]:
                    locked = doc["versions"][k]["locked"]
                else:
                    locked = False

                # latest version
                new_ver, new_app = get_latest_version(chart, k, type)

                # replace
                if new_ver != "":
                    doc["versions"][k]["version"] = new_ver
                    doc["versions"][k]["app_version"] = new_app

                version_line = print_version(
                    path, old_ver, old_app, new_ver, new_app, locked
                )

                version_contents.append(version_line)

        if doc != None:
            with open(file_path, "w") as file:
                json.dump(doc, file, sort_keys=True, indent=2)

        update_version_in_readme("\n".join(version_contents))
        update_version_in_readme(
            "\n".join(version_contents), "../argocd-env-addons/README.md"
        )


if __name__ == "__main__":
    main()
