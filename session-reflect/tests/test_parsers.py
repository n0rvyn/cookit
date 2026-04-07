#!/usr/bin/env python3
"""Unit tests for session parsers: verify output matches unified schema."""

import json
import os
import sys
import unittest

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from parse_claude_session import parse_claude_session
from parse_codex_session import parse_codex_session

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CLAUDE_SAMPLE = os.path.join(TEST_DATA_DIR, "claude-sample.jsonl")
CODEX_SAMPLE = os.path.join(TEST_DATA_DIR, "codex-sample.jsonl")

REQUIRED_TOP_KEYS = {
    "session_id", "source", "project", "project_path", "branch", "model",
    "time", "turns", "tokens", "tools", "files", "quality",
    "session_dna", "user_prompts", "task_summary", "corrections",
    "prompt_assessments", "process_gaps",
}

REQUIRED_TIME_KEYS = {"start", "end", "duration_min"}
REQUIRED_TURNS_KEYS = {"user", "assistant"}
REQUIRED_TOKENS_KEYS = {"input", "output", "cache_read", "cache_create", "cache_hit_rate"}
REQUIRED_TOOLS_KEYS = {"distribution", "total_calls", "sequence"}
REQUIRED_FILES_KEYS = {"read", "edited", "created"}
REQUIRED_QUALITY_KEYS = {"repeated_edits", "bash_errors", "build_attempts", "build_failures"}


class TestSchemaCompliance(unittest.TestCase):
    """Both parsers must produce identical schema structure."""

    def _check_schema(self, result, source_name):
        """Verify a parsed result matches the unified schema."""
        # Top-level keys
        self.assertEqual(
            set(result.keys()), REQUIRED_TOP_KEYS,
            f"{source_name}: top-level keys mismatch"
        )

        # Nested object keys
        self.assertEqual(set(result["time"].keys()), REQUIRED_TIME_KEYS)
        self.assertEqual(set(result["turns"].keys()), REQUIRED_TURNS_KEYS)
        self.assertEqual(set(result["tokens"].keys()), REQUIRED_TOKENS_KEYS)
        self.assertEqual(set(result["tools"].keys()), REQUIRED_TOOLS_KEYS)
        self.assertEqual(set(result["files"].keys()), REQUIRED_FILES_KEYS)
        self.assertEqual(set(result["quality"].keys()), REQUIRED_QUALITY_KEYS)

        # Type checks
        self.assertIsInstance(result["session_id"], str)
        self.assertIn(result["source"], ("claude-code", "codex"))
        self.assertIsInstance(result["tools"]["distribution"], dict)
        self.assertIsInstance(result["tools"]["total_calls"], int)
        self.assertIsInstance(result["tools"]["sequence"], list)
        self.assertIsInstance(result["files"]["read"], list)
        self.assertIsInstance(result["files"]["edited"], list)
        self.assertIsInstance(result["files"]["created"], list)
        self.assertIsInstance(result["user_prompts"], list)
        self.assertIsInstance(result["corrections"], list)
        self.assertIsInstance(result["prompt_assessments"], list)
        self.assertIsInstance(result["process_gaps"], list)
        self.assertIn(
            result["session_dna"],
            ("explore", "build", "fix", "chat", "mixed")
        )

    def test_claude_schema(self):
        result = parse_claude_session(CLAUDE_SAMPLE)
        self._check_schema(result, "claude-code")

    def test_codex_schema(self):
        result = parse_codex_session(CODEX_SAMPLE)
        self._check_schema(result, "codex")

    def test_schemas_have_identical_keys(self):
        claude = parse_claude_session(CLAUDE_SAMPLE)
        codex = parse_codex_session(CODEX_SAMPLE)
        self.assertEqual(sorted(claude.keys()), sorted(codex.keys()))
        self.assertEqual(sorted(claude["time"].keys()), sorted(codex["time"].keys()))
        self.assertEqual(sorted(claude["tokens"].keys()), sorted(codex["tokens"].keys()))
        self.assertEqual(sorted(claude["tools"].keys()), sorted(codex["tools"].keys()))


class TestClaudeParser(unittest.TestCase):
    """Claude Code parser produces correct values from sample data."""

    @classmethod
    def setUpClass(cls):
        cls.result = parse_claude_session(CLAUDE_SAMPLE)

    def test_source(self):
        self.assertEqual(self.result["source"], "claude-code")

    def test_session_id(self):
        self.assertEqual(self.result["session_id"], "test-session-001")

    def test_project(self):
        self.assertEqual(self.result["project"], "project-alpha")
        self.assertEqual(self.result["project_path"], "/Users/test/project-alpha")

    def test_branch(self):
        self.assertEqual(self.result["branch"], "main")

    def test_model(self):
        self.assertEqual(self.result["model"], "claude-opus-4-6")

    def test_duration(self):
        self.assertIsNotNone(self.result["time"]["duration_min"])
        self.assertGreater(self.result["time"]["duration_min"], 0)

    def test_turns(self):
        self.assertGreater(self.result["turns"]["user"], 0)
        self.assertGreater(self.result["turns"]["assistant"], 0)

    def test_tokens(self):
        self.assertGreater(self.result["tokens"]["input"], 0)
        self.assertGreater(self.result["tokens"]["output"], 0)
        self.assertIsNotNone(self.result["tokens"]["cache_hit_rate"])

    def test_tools(self):
        dist = self.result["tools"]["distribution"]
        self.assertIn("Read", dist)
        self.assertIn("Edit", dist)
        self.assertGreater(self.result["tools"]["total_calls"], 0)

    def test_files(self):
        self.assertIn("/Users/test/project-alpha/auth.py", self.result["files"]["read"])
        self.assertIn("/Users/test/project-alpha/auth.py", self.result["files"]["edited"])

    def test_repeated_edits(self):
        # auth.py edited 3 times (Edit called 3 times on it)
        repeated = self.result["quality"]["repeated_edits"]
        self.assertIn("/Users/test/project-alpha/auth.py", repeated)

    def test_user_prompts(self):
        self.assertGreater(len(self.result["user_prompts"]), 0)
        self.assertIn("login bug", self.result["user_prompts"][0])


class TestCodexParser(unittest.TestCase):
    """Codex parser produces correct values from sample data."""

    @classmethod
    def setUpClass(cls):
        cls.result = parse_codex_session(CODEX_SAMPLE)

    def test_source(self):
        self.assertEqual(self.result["source"], "codex")

    def test_session_id(self):
        self.assertEqual(self.result["session_id"], "test-codex-001")

    def test_project(self):
        self.assertEqual(self.result["project"], "project-beta")
        self.assertEqual(self.result["project_path"], "/Users/test/project-beta")

    def test_branch(self):
        self.assertEqual(self.result["branch"], "feature-x")

    def test_model(self):
        self.assertEqual(self.result["model"], "gpt-5.4")

    def test_duration(self):
        self.assertIsNotNone(self.result["time"]["duration_min"])
        self.assertGreater(self.result["time"]["duration_min"], 0)

    def test_turns(self):
        self.assertGreater(self.result["turns"]["user"], 0)
        self.assertGreater(self.result["turns"]["assistant"], 0)

    def test_tokens_from_event_msg(self):
        # Codex tokens come from last token_count event
        self.assertEqual(self.result["tokens"]["input"], 30000)
        self.assertEqual(self.result["tokens"]["output"], 1600)  # 1200 + 400 reasoning
        self.assertEqual(self.result["tokens"]["cache_read"], 25000)

    def test_tools(self):
        dist = self.result["tools"]["distribution"]
        self.assertIn("exec_command", dist)
        self.assertIn("apply_patch", dist)
        self.assertEqual(self.result["tools"]["total_calls"], 2)

    def test_user_prompts(self):
        self.assertGreater(len(self.result["user_prompts"]), 0)
        self.assertIn("error handling", self.result["user_prompts"][0])


if __name__ == "__main__":
    unittest.main()
