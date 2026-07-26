"""Download the reproducibility Parquet files from a GitHub Release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data_manifest.json"
OUTPUT_DIR = ROOT / "parquet"
CHUNK_SIZE = 8 * 1024 * 1024


def human_size(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GiB"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def valid_file(path: Path, metadata: dict) -> bool:
    if not path.exists() or path.stat().st_size != metadata["bytes"]:
        return False
    print(f"  verifying {path.name}...", flush=True)
    return sha256(path) == metadata["sha256"]


def download(url: str, destination: Path, expected_bytes: int) -> None:
    partial = destination.with_suffix(destination.suffix + ".part")
    partial.unlink(missing_ok=True)
    headers = {"User-Agent": "genesis-antifraud-case-downloader"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)
    started = time.time()
    downloaded = 0
    try:
        with urlopen(request) as response, partial.open("wb") as output:
            total = int(response.headers.get("Content-Length") or expected_bytes)
            while chunk := response.read(CHUNK_SIZE):
                output.write(chunk)
                downloaded += len(chunk)
                percent = downloaded / total * 100 if total else 0
                elapsed = max(time.time() - started, 0.1)
                speed = downloaded / elapsed
                print(
                    f"\r  {percent:5.1f}%  {human_size(downloaded)}"
                    f" / {human_size(total)}  {human_size(int(speed))}/s",
                    end="",
                    flush=True,
                )
    except (HTTPError, URLError) as error:
        partial.unlink(missing_ok=True)
        raise RuntimeError(
            f"Could not download {url}\n"
            "Check the repository name, the data-v1 release, and internet access."
        ) from error
    print()
    partial.replace(destination)


def parse_args() -> argparse.Namespace:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    parser = argparse.ArgumentParser(
        description="Download and verify Parquet assets for the anti-fraud case."
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", manifest["repository"]),
        help="GitHub repository in OWNER/REPOSITORY format.",
    )
    parser.add_argument(
        "--tag",
        default=manifest["release_tag"],
        help="GitHub Release tag containing the Parquet assets.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download files again even when the local hashes match.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Repository: {args.repo}")
    print(f"Release:    {args.tag}")
    for index, metadata in enumerate(manifest["files"], start=1):
        destination = OUTPUT_DIR / metadata["name"]
        print(
            f"[{index}/{len(manifest['files'])}] {metadata['name']} "
            f"({human_size(metadata['bytes'])})"
        )
        if not args.force and valid_file(destination, metadata):
            print("  OK — already downloaded")
            continue

        url = (
            f"https://github.com/{args.repo}/releases/download/"
            f"{quote(args.tag)}/{quote(metadata['name'])}"
        )
        download(url, destination, metadata["bytes"])
        if not valid_file(destination, metadata):
            destination.unlink(missing_ok=True)
            raise RuntimeError(
                f"SHA-256 or file size does not match for {metadata['name']}."
            )
        print("  OK")

    print("\nAll Parquet files are ready.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, RuntimeError) as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
