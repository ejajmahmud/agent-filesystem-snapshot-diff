"""Tests for Agent Filesystem Snapshot Diff."""
import os
import tempfile
import unittest
from agent_filesystem_snapshot_diff.core import FilesystemSnapshotAuditor


class TestFilesystemSnapshotAuditor(unittest.TestCase):
    def test_diff_and_protected_violation(self):
        auditor = FilesystemSnapshotAuditor(protected_paths={".env", ".github/*"})
        res = auditor.diff_manifests(
            {"a.py": "111", ".env": "sec"},
            {"a.py": "222", ".env": "pwn", "b.py": "333"},
        )
        self.assertEqual(res["added"], ["b.py"])
        self.assertEqual(res["modified"], [".env", "a.py"])
        self.assertEqual(res["protected_violations"], [".env"])
        self.assertFalse(res["clean_scope"])

    def test_capture_real_temp_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "hello.txt")
            with open(p, "w", encoding="utf-8") as f:
                f.write("v1")
            s1 = FilesystemSnapshotAuditor.capture_directory(tmp)
            with open(p, "w", encoding="utf-8") as f:
                f.write("v2")
            s2 = FilesystemSnapshotAuditor.capture_directory(tmp)
            diff = FilesystemSnapshotAuditor().diff_manifests(s1, s2)
            self.assertEqual(diff["modified"], ["hello.txt"])
            self.assertTrue(diff["clean_scope"])
