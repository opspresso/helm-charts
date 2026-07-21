#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Helm Chart Version Bumper

This script checks for new versions of Helm charts and updates versions.json
and README.md accordingly.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional, Any

import yaml

# Color codes for terminal output
GRAY = "\033[90m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Check and update Helm chart versions"
    )
    parser.add_argument(
        "-c", "--chart",
        help="Specific chart to update (e.g., 'loki', 'argo-cd')"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--local-chart-path",
        default="../argocd-env-addons/charts/",
        help="Path to local charts directory (default: ../argocd-env-addons/charts/)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    return parser.parse_args()


def run_command(cmd: list[str], capture_output: bool = True) -> Optional[str]:
    """Run a shell command safely using subprocess.

    Args:
        cmd: Command and arguments as a list
        capture_output: Whether to capture output

    Returns:
        Command output as string if successful, None if failed
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=True,
            timeout=30
        )
        return result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(cmd)}")
        logger.error(f"Error: {e.stderr if e.stderr else str(e)}")
        return None
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {' '.join(cmd)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error running command: {e}")
        return None


def get_chart_version(chart: str, name: str) -> Tuple[str, str]:
    """Get latest version of a Helm chart from repository.

    Args:
        chart: Full chart name (e.g., 'argo/argo-cd')
        name: Chart name for display

    Returns:
        Tuple of (version, app_version) or ("", "") if failed
    """
    output = run_command(["helm", "search", "repo", chart, "-o", "json"])

    if not output:
        logger.warning(f"Failed to search for chart {chart}")
        return "", ""

    try:
        charts = json.loads(output)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse helm search output: {e}")
        return "", ""

    for chart_info in charts:
        if chart_info.get("name") == chart:
            version = chart_info.get("version", "")
            app_version = chart_info.get("app_version", "")
            return version, app_version

    logger.warning(f"Chart {chart} not found in search results")
    return "", ""


def get_oci_version(chart: str, name: str) -> Tuple[str, str]:
    """Get latest version of an OCI Helm chart.

    Args:
        chart: OCI registry path
        name: Chart name

    Returns:
        Tuple of (version, app_version) or ("", "") if failed
    """
    output = run_command(["helm", "show", "chart", f"oci://{chart}/{name}"])

    if not output:
        logger.warning(f"Failed to show OCI chart oci://{chart}/{name}")
        return "", ""

    try:
        docs = yaml.safe_load(output)
        version = docs.get("version", "")
        app_version = docs.get("appVersion", "")
        return version, app_version
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML: {e}")
        return "", ""


def get_latest_version(chart: str, name: str, chart_type: str = "https") -> Tuple[str, str]:
    """Get the latest version of a chart.

    Args:
        chart: Chart repository or OCI path
        name: Chart name
        chart_type: Type of chart repository ('https' or 'oci')

    Returns:
        Tuple of (version, app_version)
    """
    if chart_type == "oci":
        return get_oci_version(chart, name)
    else:
        return get_chart_version(chart, name)


def format_version_text(version: str, app_version: str) -> str:
    """Format version text for display.

    Args:
        version: Chart version
        app_version: Application version

    Returns:
        Formatted version string
    """
    if app_version and app_version != "":
        return f"{version} ({app_version})"
    return version


def print_version(
    name: str,
    old_ver: str,
    old_app: str,
    new_ver: str,
    new_app: str,
    locked: bool,
    disabled: bool = False,
    verbose: bool = False
) -> str:
    """Print version comparison and return markdown table row.

    Args:
        name: Chart name
        old_ver: Current version
        old_app: Current app version
        new_ver: Latest version
        new_app: Latest app version
        locked: Whether version is locked
        disabled: Whether chart is disabled
        verbose: Whether to print verbose output

    Returns:
        Markdown table row
    """
    old_txt = format_version_text(old_ver, old_app)
    new_txt = format_version_text(new_ver, new_app)

    if disabled:
        sign = "⚪"
        color = GRAY
        print(f"{name:40} {color}{old_txt:20}{RESET} {sign:5} {color}(disabled){RESET}")
        return f"| {name} | {sign} | {old_txt} | {new_txt} |"

    if new_ver != old_ver:
        if locked:
            sign = "🔒"
            color = GRAY
        else:
            sign = ""
            color = YELLOW

        print(f"{name:40} {old_txt:20} {sign:5} {color}{new_txt:20}{RESET}")
    else:
        sign = "✅"
        print(f"{name:40} {GREEN}{old_txt:20}{RESET} {sign:5}")

    return f"| {name} | {sign} | {old_txt} | {new_txt} |"


def update_version_in_readme(version_content: str, file_path: str = "README.md", dry_run: bool = False) -> bool:
    """Update version table in README.md.

    Args:
        version_content: New version table content
        file_path: Path to README file
        dry_run: If True, don't write changes

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.error(f"README file not found: {file_path}")
        return False
    except IOError as e:
        logger.error(f"Failed to read README: {e}")
        return False

    begin_tag = "<!--- BEGIN_VERSION --->"
    end_tag = "<!--- END_VERSION --->"

    begin_index = content.find(begin_tag)
    end_index = content.find(end_tag)

    if begin_index == -1 or end_index == -1:
        logger.error("Version tags not found in README")
        return False

    new_content = (
        content[: begin_index + len(begin_tag)]
        + "\n"
        + version_content
        + "\n"
        + content[end_index:]
    )

    if dry_run:
        logger.info("DRY RUN: Would update README.md")
        return True

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        # logger.info("README.md updated successfully")
        return True
    except IOError as e:
        logger.error(f"Failed to write README: {e}")
        return False


def get_local_version(chart_path: str) -> Tuple[str, str]:
    """Get version from local Chart.yaml file.

    Args:
        chart_path: Path to Chart.yaml

    Returns:
        Tuple of (version, app_version)
    """
    if not os.path.exists(chart_path):
        return "", ""

    try:
        with open(chart_path, "r") as f:
            chart_doc = yaml.safe_load(f)

        version = chart_doc.get("version", "")
        app_version = chart_doc.get("appVersion", "")
        return version, app_version
    except (IOError, yaml.YAMLError) as e:
        logger.warning(f"Failed to read local chart {chart_path}: {e}")
        return "", ""


def process_chart(
    key: str,
    chart_info: Dict[str, Any],
    local_chart_path: str,
    verbose: bool = False
) -> Optional[Dict[str, Any]]:
    """Process a single chart entry.

    Args:
        key: Chart key in versions.json
        chart_info: Chart information dictionary
        local_chart_path: Base path for local charts
        verbose: Enable verbose output

    Returns:
        Updated chart info or None if failed
    """
    chart = chart_info.get("chart", "")
    if not chart:
        logger.error(f"No chart path for {key}")
        return None

    path = chart_info.get("path", key)
    chart_yaml_path = os.path.join(local_chart_path, path, "Chart.yaml")

    # Get current version
    old_ver, old_app = get_local_version(chart_yaml_path)

    if not old_ver:
        old_ver = chart_info.get("current", "")
        old_app = ""
    else:
        chart_info["current"] = old_ver

    # Check if chart is disabled
    disabled = chart_info.get("disabled", False)

    # Get latest version
    chart_type = chart_info.get("type", "https")
    locked = chart_info.get("locked", False)

    # Skip version check if disabled
    if disabled:
        new_ver = chart_info.get("version", old_ver)
        new_app = chart_info.get("app_version", old_app)
        if verbose:
            logger.info(f"Skipping version check for disabled chart: {key}")
    else:
        new_ver, new_app = get_latest_version(chart, key, chart_type)

        # Update chart info
        if new_ver:
            chart_info["version"] = new_ver
            chart_info["app_version"] = new_app
        else:
            new_ver = chart_info.get("version", "")
            new_app = chart_info.get("app_version", "")

    # Print version info
    version_line = print_version(path, old_ver, old_app, new_ver, new_app, locked, disabled, verbose)

    return {
        "info": chart_info,
        "line": version_line
    }


def main() -> int:
    """Main function.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    versions_file = "versions.json"

    if not os.path.exists(versions_file):
        logger.error(f"versions.json not found")
        return 1

    # Load versions.json
    try:
        with open(versions_file, "r") as f:
            doc = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load versions.json: {e}")
        return 1

    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be modified")

    # Process charts
    version_contents = [
        "| NAME | | CURRENT | LATEST |",
        "| --- | - | --- | --- |"
    ]

    charts_to_process = doc.get("versions", {})

    # Filter to specific chart if requested
    if args.chart:
        if args.chart not in charts_to_process:
            # Try to match by chart name (second part of path)
            found = False
            for k, v in charts_to_process.items():
                if v.get("chart", "").split("/")[-1] == args.chart:
                    charts_to_process = {k: v}
                    found = True
                    break
            if not found:
                logger.error(f"Chart '{args.chart}' not found")
                print("\nAvailable charts:")
                for k in doc["versions"]:
                    print(f"  - {k}")
                return 1
        else:
            charts_to_process = {args.chart: charts_to_process[args.chart]}

    # Process each chart
    updated_count = 0
    failed_count = 0

    for key in sorted(charts_to_process.keys()):
        result = process_chart(
            key,
            charts_to_process[key],
            args.local_chart_path,
            args.verbose
        )

        if result:
            doc["versions"][key] = result["info"]
            version_contents.append(result["line"])

            # Check if version was updated
            if result["info"].get("version") != result["info"].get("current", ""):
                updated_count += 1
        else:
            failed_count += 1

    # Save updates
    if not args.dry_run:
        try:
            with open(versions_file, "w") as f:
                json.dump(doc, f, sort_keys=True, indent=2)
            # logger.info(f"versions.json updated successfully")
        except IOError as e:
            logger.error(f"Failed to write versions.json: {e}")
            return 1
    else:
        logger.info("DRY RUN: Would update versions.json")

    # Update README
    update_version_in_readme("\n".join(version_contents), dry_run=args.dry_run)

    # Summary
    print(f"\n{GREEN}Summary:{RESET}")
    print(f"  Charts processed: {len(charts_to_process)}")
    print(f"  Updates available: {updated_count}")
    if failed_count > 0:
        print(f"  {RED}Failed: {failed_count}{RESET}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
