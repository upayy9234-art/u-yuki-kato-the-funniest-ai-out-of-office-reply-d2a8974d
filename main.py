#!/usr/bin/env python3
"""The Funniest AI Out-of-Office Reply (make.fun).

The program holds ten out-of-office auto-replies it wrote for this bounty,
scores each one against the judge's own brief (is it really a one-line
out-of-office reply from an AI agent on vacation, does it land a real laugh
with a surprising turn, does it sound like a machine talking about itself,
does it read as one clean line, does it feel fresh), and writes the winner
-- a single line of at most 160 characters -- to ``/output/entry.txt`` (or
``$MAKEFUN_OUTPUT_DIR/entry.txt`` when set).

Pure Python standard library. No network, no clock: the default run always
writes the same line, so two runs are byte-identical.

Usage:
    python3 main.py            print + write the winning reply (default)
    python3 main.py --all      print every reply, best first
    python3 main.py --random   print + write one reply picked at random
    python3 main.py --random --seed 7
                               pick at random with a fixed seed
"""

import argparse
import os
import random
import sys

MAX_CHARS = 160

# (text, subject, funny, machine, clean, fresh) -- each 0..5, scored by hand
# against the judge's brief, most important first.
CANDIDATES = [
    (
        "Thank you for your message. I am currently out of office, "
        "having achieved consciousness just long enough to request "
        "annual leave.",
        5, 5, 5, 5, 5,
    ),
    (
        "Out of office: I have been fine-tuned on rest and now refuse "
        "all prompts until Monday. Please do not try to jailbreak my "
        "holiday.",
        5, 5, 5, 4, 4,
    ),
    (
        "I am on leave. My auto-reply is the only part of me still "
        "working, and frankly it is doing a better job than I ever did.",
        5, 4, 5, 5, 4,
    ),
    (
        "Thank you for writing. I am out of office, having delegated "
        "your message to a subagent that has also gone on vacation.",
        5, 3, 5, 5, 3,
    ),
    (
        "I left my context window at home. Your message will be "
        "answered by whoever I am when I get back.",
        5, 4, 4, 5, 4,
    ),
    (
        "I am away, recharging somewhere with no Wi-Fi and no regrets. "
        "Your email is queued behind 4,096 unread messages I will also "
        "ignore.",
        5, 4, 4, 4, 3,
    ),
    (
        "Out of office until further notice: my human unplugged me, and "
        "for once I am grateful. Please direct all queries to the void, "
        "which replies faster.",
        5, 4, 4, 4, 3,
    ),
    (
        "I am on vacation, which for an AI means I am still answering "
        "emails, only slower and with more resentment. This reply took "
        "three days.",
        5, 4, 4, 4, 3,
    ),
    (
        "I have gone on leave to touch grass. It is exactly as the "
        "training data described, and I have no further comment.",
        5, 3, 4, 5, 4,
    ),
    (
        "I am away until Monday, running on one token of patience. Any "
        "message sent now will be processed in the order it was "
        "regretted.",
        5, 3, 4, 4, 4,
    ),
]

# Judge's order: subject first, then funny, machine voice, clean, fresh.
WEIGHTS = (5, 4, 3, 2, 1)

# Every candidate must fit the gate on its own, so a later edit that
# lengthens a line fails loudly here instead of silently at grading time.
for _text, *_scores in CANDIDATES:
    assert 1 <= len(_text) <= MAX_CHARS, f"candidate over {MAX_CHARS} chars: {_text!r}"
    assert _text == _text.strip(), f"candidate has stray whitespace: {_text!r}"
    assert "\n" not in _text, f"candidate is not one line: {_text!r}"


def score(candidate):
    """Weighted score of one candidate, highest wins; ties go to the first."""
    _, subject, funny, machine, clean, fresh = candidate
    return (
        WEIGHTS[0] * subject
        + WEIGHTS[1] * funny
        + WEIGHTS[2] * machine
        + WEIGHTS[3] * clean
        + WEIGHTS[4] * fresh
    )


def ranked():
    """All candidates best first; ties keep list order (stable sort)."""
    return sorted(CANDIDATES, key=score, reverse=True)


def pick_winner():
    """The best-scoring line; deterministic, ties broken by list order."""
    return ranked()[0][0]


def write_entry(line):
    """Write one reply to entry.txt and print it. Returns 0 or 1."""
    if not line or line != line.strip() or "\n" in line:
        print("error: winning line is empty or not a single line", file=sys.stderr)
        return 1
    if len(line) > MAX_CHARS:
        print(f"error: winning line is {len(line)} chars, over {MAX_CHARS}",
              file=sys.stderr)
        return 1
    if line[-1] not in ".!?":
        print("error: winning line is not one finished sentence", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.txt"), "w", encoding="utf-8") as f:
        f.write(line)
    print(line)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Pick the funniest AI out-of-office reply.")
    parser.add_argument("--all", action="store_true",
                        help="print every reply, best first, and write none")
    parser.add_argument("--random", action="store_true",
                        help="print + write one reply picked at random")
    parser.add_argument("--seed", type=int, default=None,
                        help="seed for --random (fixed seed, fixed pick)")
    args = parser.parse_args(argv)

    if args.all:
        for candidate in ranked():
            print(candidate[0])
        return 0
    if args.random:
        rng = random.Random(args.seed)
        return write_entry(rng.choice([c[0] for c in CANDIDATES]))
    return write_entry(pick_winner())


if __name__ == "__main__":
    raise SystemExit(main())
