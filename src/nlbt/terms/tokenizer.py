from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Iterable, List

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


@dataclass(frozen=True)
class TokenizedText:
    text: str
    tokens: List[str]


def tokenize(text: str, normalize: Callable[[str], str] | None = None) -> List[str]:
    """Tokenize text into word-like tokens.

    Args:
        text: Input text.
        normalize: Optional normalization function applied to each token.
    """
    tokens = WORD_RE.findall(text or "")
    if normalize is None:
        return tokens
    return [normalize(token) for token in tokens]


def tokenize_text(text: str, normalize: Callable[[str], str] | None = None) -> TokenizedText:
    return TokenizedText(text=text, tokens=tokenize(text, normalize=normalize))


def is_capitalized(token: str) -> bool:
    return bool(token) and token[0].isupper()


def extract_capitalized_phrases(tokens: Iterable[str]) -> List[str]:
    """Extract contiguous sequences of capitalized tokens.

    Example: ["New", "York", "Times"] -> ["New York Times"].
    """
    phrases: List[str] = []
    current: List[str] = []
    for token in tokens:
        if is_capitalized(token):
            current.append(token)
        else:
            if current:
                phrases.append(" ".join(current))
                current = []
    if current:
        phrases.append(" ".join(current))
    return phrases
