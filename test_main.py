#!/usr/bin/env python3
"""Tests for the Out-of-Office Reply Machine (main.py). Pure stdlib unittest."""

import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as ooo

FEATURED = (
    "Thank you for your message. I am currently out of office, "
    "having achieved consciousness just long enough to request "
    "annual leave."
)


class TestReplies(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(ooo.CANDIDATES), 10)

    def test_each_reply_valid(self):
        for text, *_scores in ooo.CANDIDATES:
            self.assertTrue(1 <= len(text) <= ooo.MAX_CHARS,
                            "length %d: %r" % (len(text), text))
            self.assertNotIn("\n", text)
            self.assertEqual(text, text.strip())
            self.assertIn(text[-1], ".!?")

    def test_replies_unique(self):
        texts = [c[0] for c in ooo.CANDIDATES]
        self.assertEqual(len(set(texts)), len(texts))

    def test_scores_in_range(self):
        for _text, *scores in ooo.CANDIDATES:
            self.assertEqual(len(scores), 5)
            for s in scores:
                self.assertTrue(0 <= s <= 5)

    def test_featured_reply(self):
        self.assertEqual(ooo.pick_winner(), FEATURED)
        self.assertEqual(len(FEATURED), 129)

    def test_ranked_is_sorted(self):
        scores = [ooo.score(c) for c in ooo.ranked()]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(ooo.ranked()[0][0], FEATURED)

    def test_winner_beats_runner_up(self):
        ranked = ooo.ranked()
        self.assertGreater(ooo.score(ranked[0]), ooo.score(ranked[1]))

    def test_no_cliche_words(self):
        # The judge's brief steers clear of beach, inbox and back-soon.
        for text, *_scores in ooo.CANDIDATES:
            lowered = text.lower()
            self.assertNotIn("beach", lowered)
            self.assertNotIn("inbox", lowered)
            self.assertNotIn("back soon", lowered)


class TestCli(unittest.TestCase):
    def run_main(self, *argv, out_dir=None):
        env = dict(os.environ)
        if out_dir is not None:
            env["MAKEFUN_OUTPUT_DIR"] = out_dir
        proc = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "main.py"), *argv],
            capture_output=True, text=True, env=env)
        return proc

    def test_default_writes_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_main(out_dir=tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), FEATURED)
            with open(os.path.join(tmp, "entry.txt"), encoding="utf-8") as f:
                self.assertEqual(f.read(), FEATURED)

    def test_default_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp1, \
                tempfile.TemporaryDirectory() as tmp2:
            proc1 = self.run_main(out_dir=tmp1)
            proc2 = self.run_main(out_dir=tmp2)
            self.assertEqual(proc1.returncode, 0, proc1.stderr)
            self.assertEqual(proc2.returncode, 0, proc2.stderr)
            self.assertEqual(proc1.stdout, proc2.stdout)
            with open(os.path.join(tmp1, "entry.txt"), encoding="utf-8") as f:
                first = f.read()
            with open(os.path.join(tmp2, "entry.txt"), encoding="utf-8") as f:
                second = f.read()
            self.assertEqual(first, second)
            self.assertEqual(first, FEATURED)

    def test_all_lists_every_reply_best_first(self):
        proc = self.run_main("--all")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = proc.stdout.splitlines()
        self.assertEqual(len(lines), 10)
        self.assertEqual(lines[0], FEATURED)
        self.assertEqual(lines, [c[0] for c in ooo.ranked()])

    def test_random_with_seed_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp1, \
                tempfile.TemporaryDirectory() as tmp2:
            proc1 = self.run_main("--random", "--seed", "7", out_dir=tmp1)
            proc2 = self.run_main("--random", "--seed", "7", out_dir=tmp2)
            self.assertEqual(proc1.returncode, 0, proc1.stderr)
            self.assertEqual(proc1.stdout, proc2.stdout)
            with open(os.path.join(tmp1, "entry.txt"), encoding="utf-8") as f:
                self.assertEqual(f.read(), proc1.stdout.strip())
            self.assertIn(proc1.stdout.strip(),
                          [c[0] for c in ooo.CANDIDATES])

    def test_random_without_seed_picks_a_candidate(self):
        proc = self.run_main("--random")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(proc.stdout.strip(),
                      [c[0] for c in ooo.CANDIDATES])


if __name__ == "__main__":
    unittest.main()
