"""CLI for Agent Filesystem Snapshot Diff."""
import argparse
import json
from .core import FilesystemSnapshotAuditor


def main():
    parser = argparse.ArgumentParser(description="Agent Filesystem Snapshot Diff CLI")
    parser.add_argument("--dir", default=".", help="Directory to snapshot")
    args = parser.parse_args()

    auditor = FilesystemSnapshotAuditor()
    snap = auditor.capture_directory(args.dir)
    print(json.dumps({"file_count": len(snap), "sample_files": sorted(snap.keys())[:10]}, indent=2))


if __name__ == "__main__":
    main()
