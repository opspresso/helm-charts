#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Helm Chart Downloader

This script downloads Helm charts based on versions.json configuration
and extracts them to the charts directory.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Download Helm charts based on versions.json"
    )
    parser.add_argument(
        "-c", "--chart",
        default=None,
        help="Specific chart name to download (e.g., 'loki', 'argo-cd'). If not specified, downloads all charts."
    )
    parser.add_argument(
        "-v", "--version",
        default=None,
        help="Specific version to download. If not specified, uses version from versions.json"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be downloaded without actually downloading"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Download charts in parallel (faster but uses more resources)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Maximum number of parallel downloads (default: 5)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    return parser.parse_args()


def run_command(cmd: List[str], timeout: int = 120) -> Tuple[bool, str]:
    """Run a shell command safely using subprocess.

    Args:
        cmd: Command and arguments as a list
        timeout: Command timeout in seconds

    Returns:
        Tuple of (success, output/error message)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed: {' '.join(cmd)}\n"
        if e.stderr:
            error_msg += f"Error: {e.stderr}"
        return False, error_msg
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout}s: {' '.join(cmd)}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def helm_pull(chart: str, version: str, destination: str = "./build/") -> bool:
    """Download a Helm chart using helm pull command.

    Args:
        chart: Full chart path (e.g., 'argo/argo-cd')
        version: Chart version to download
        destination: Directory to save the chart

    Returns:
        True if successful, False otherwise
    """
    cmd = ["helm", "pull", chart, "--version", version, "--destination", destination]

    success, output = run_command(cmd)

    if not success:
        logger.error(f"Failed to pull chart {chart}:{version}")
        logger.error(output)
        return False

    return True


def extract_chart(chart_tgz: str, extract_path: str, force: bool = True) -> bool:
    """Extract a chart archive to the specified directory.

    Args:
        chart_tgz: Path to the .tgz file
        extract_path: Directory to extract to
        force: Whether to overwrite existing directory

    Returns:
        True if successful, False otherwise
    """
    try:
        # Remove existing directory if force is True
        if force and os.path.exists(extract_path):
            logger.debug(f"Removing existing directory: {extract_path}")
            shutil.rmtree(extract_path)

        # Create parent directory if needed
        os.makedirs(os.path.dirname(extract_path), exist_ok=True)

        # Extract the archive
        logger.debug(f"Extracting {chart_tgz} to {os.path.dirname(extract_path)}")
        with tarfile.open(chart_tgz) as tar:
            tar.extractall(os.path.dirname(extract_path))

        return True
    except Exception as e:
        logger.error(f"Failed to extract {chart_tgz}: {e}")
        return False


def download_and_extract_chart(
    chart_path: str,
    version: str,
    name: str,
    dry_run: bool = False,
    verbose: bool = False
) -> bool:
    """Download and extract a single Helm chart.

    Args:
        chart_path: Full chart path (e.g., 'argo/argo-cd')
        version: Chart version to download
        name: Chart name for local storage
        dry_run: If True, only preview actions
        verbose: Enable verbose output

    Returns:
        True if successful, False otherwise
    """
    chart_tgz = f"./build/{name}-{version}.tgz"
    extract_path = f"./charts/{name}"

    if dry_run:
        print(f"  {YELLOW}[DRY RUN]{RESET} Would download {chart_path} version {version}")
        print(f"  {YELLOW}[DRY RUN]{RESET} Would save to {chart_tgz}")
        print(f"  {YELLOW}[DRY RUN]{RESET} Would extract to {extract_path}")
        return True

    # Check if already downloaded
    if os.path.exists(chart_tgz):
        if verbose:
            print(f"  {GREEN}✓{RESET} Already downloaded: {chart_tgz}")
    else:
        print(f"  Downloading {name} version {version}...")
        if not helm_pull(chart_path, version):
            print(f"  {RED}✗{RESET} Failed to download {name}")
            return False
        print(f"  {GREEN}✓{RESET} Downloaded {name}")

    # Extract the chart
    if os.path.exists(chart_tgz):
        if verbose:
            print(f"  Extracting {chart_tgz}...")

        if extract_chart(chart_tgz, extract_path):
            print(f"  {GREEN}✓{RESET} Extracted {name}")
            return True
        else:
            print(f"  {RED}✗{RESET} Failed to extract {name}")
            return False

    return False


def process_single_chart(
    chart_key: str,
    chart_info: Dict[str, Any],
    version_override: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = False
) -> Tuple[str, bool]:
    """Process a single chart download.

    Args:
        chart_key: Chart key from versions.json
        chart_info: Chart information dictionary
        version_override: Override version from versions.json
        dry_run: If True, only preview actions
        verbose: Enable verbose output

    Returns:
        Tuple of (chart_name, success)
    """
    chart_path = chart_info.get("chart", "")
    if not chart_path:
        logger.error(f"No chart path defined for {chart_key}")
        return chart_key, False

    version = version_override if version_override else chart_info.get("version", "")
    if not version:
        logger.error(f"No version defined for {chart_key}")
        return chart_key, False

    # Extract chart name from path
    name = chart_path.split("/")[-1]

    if verbose or not dry_run:
        print(f"\nProcessing {name}:")

    success = download_and_extract_chart(
        chart_path,
        version,
        name,
        dry_run=dry_run,
        verbose=verbose
    )

    return name, success


def load_versions_config(filepath: str = "versions.json") -> Optional[Dict[str, Any]]:
    """Load and validate versions.json configuration.

    Args:
        filepath: Path to versions.json file

    Returns:
        Loaded configuration or None if failed
    """
    if not os.path.exists(filepath):
        logger.error(f"{filepath} not found")
        return None

    try:
        with open(filepath, "r") as f:
            doc = json.load(f)

        if "versions" not in doc:
            logger.error("Invalid versions.json: missing 'versions' key")
            return None

        return doc
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {filepath}: {e}")
        return None
    except IOError as e:
        logger.error(f"Failed to read {filepath}: {e}")
        return None


def find_chart_in_config(
    chart_name: str,
    versions_config: Dict[str, Any]
) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Find a chart in the versions configuration.

    Args:
        chart_name: Name of the chart to find
        versions_config: Versions configuration dictionary

    Returns:
        Tuple of (key, chart_info) or None if not found
    """
    versions = versions_config.get("versions", {})

    # Direct key match
    if chart_name in versions:
        return chart_name, versions[chart_name]

    # Try to match by chart name (last part of chart path)
    for key, info in versions.items():
        chart_path = info.get("chart", "")
        if chart_path.split("/")[-1] == chart_name:
            return key, info

    return None


def main() -> int:
    """Main function.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Create directories
    os.makedirs("build", exist_ok=True)
    os.makedirs("charts", exist_ok=True)

    # Load configuration
    config = load_versions_config()
    if not config:
        return 1

    if args.dry_run:
        print(f"{YELLOW}DRY RUN MODE - No files will be downloaded{RESET}\n")

    # Determine which charts to process
    charts_to_process = []

    if args.chart:
        # Process specific chart
        result = find_chart_in_config(args.chart, config)

        if not result:
            logger.error(f"Chart '{args.chart}' not found in versions.json")
            print("\nAvailable charts:")
            for key in sorted(config["versions"].keys()):
                print(f"  - {key}")
            return 1

        key, chart_info = result
        charts_to_process.append((key, chart_info))

        print(f"Downloading {args.chart}")
        if args.version:
            print(f"Using version override: {args.version}")
    else:
        # Process all charts
        print("Downloading all charts from versions.json")
        charts_to_process = list(config["versions"].items())

    # Process charts
    total = len(charts_to_process)
    successful = 0
    failed = 0

    if args.parallel and not args.dry_run and total > 1:
        # Parallel processing
        print(f"\nUsing parallel downloads (max {args.max_workers} workers)")

        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            futures = {}

            for key, chart_info in charts_to_process:
                future = executor.submit(
                    process_single_chart,
                    key,
                    chart_info,
                    args.version,
                    args.dry_run,
                    args.verbose
                )
                futures[future] = key

            for future in as_completed(futures):
                name, success = future.result()
                if success:
                    successful += 1
                else:
                    failed += 1
    else:
        # Sequential processing
        for key, chart_info in charts_to_process:
            name, success = process_single_chart(
                key,
                chart_info,
                args.version,
                args.dry_run,
                args.verbose
            )

            if success:
                successful += 1
            else:
                failed += 1

    # Print summary
    print(f"\n{GREEN}Summary:{RESET}")
    print(f"  Total charts: {total}")
    print(f"  Successful: {successful}")
    if failed > 0:
        print(f"  {RED}Failed: {failed}{RESET}")

    if args.dry_run:
        print(f"\n{YELLOW}This was a dry run. No files were actually downloaded.{RESET}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
