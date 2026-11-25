"""Core SHA-256 filesystem snapshot and protected-path mutation auditor."""
import fnmatch
import hashlib
import os
from typing import Any, Dict, List, Set


class FilesystemSnapshotAuditor:
    """Snapshots directory hashes and audits post-execution agent file mutations."""

    def __init__(self, protected_paths: Set[str] = None):
        self.protected_paths = set(protected_paths or {".env", ".git/*", ".github/workflows/*"})

    @staticmethod
    def capture_directory(root_dir: str) -> Dict[str, str]:
        snap: Dict[str, str] = {}
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            for fname in filenames:
                full = os.path.join(dirpath, fname)
                rel = os.path.relpath(full, root_dir).replace("\\", "/")
                h = hashlib.sha256()
                with open(full, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        h.update(chunk)
                snap[rel] = h.hexdigest()
        return snap

    def _is_protected(self, rel_path: str) -> bool:
        return any(fnmatch.fnmatch(rel_path, pat) for pat in self.protected_paths)

    def diff_manifests(self, before: Dict[str, str], after: Dict[str, str]) -> Dict[str, Any]:
        before_keys = set(before.keys())
        after_keys = set(after.keys())

        added = sorted(after_keys - before_keys)
        deleted = sorted(before_keys - after_keys)
        modified = sorted(k for k in (before_keys & after_keys) if before[k] != after[k])

        all_changed = added + deleted + modified
        violations = sorted(p for p in all_changed if self._is_protected(p))

        return {
            "added": added,
            "modified": modified,
            "deleted": deleted,
            "protected_violations": violations,
            "clean_scope": len(violations) == 0,
        }
