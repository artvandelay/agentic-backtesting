"""Term extraction utilities for diff text."""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z\-']+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def ngrams(tokens: Iterable[str], n: int) -> Iterable[str]:
    tokens_list = list(tokens)
    for i in range(len(tokens_list) - n + 1):
        yield " ".join(tokens_list[i : i + n])


def extract_terms(text: str, max_n: int = 4) -> Counter[str]:
    tokens = tokenize(text)
    counts: Counter[str] = Counter()
    for n in range(1, max_n + 1):
        counts.update(ngrams(tokens, n))
    return counts
