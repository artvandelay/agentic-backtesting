from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List

from .tokenizer import extract_capitalized_phrases, tokenize


@dataclass(frozen=True)
class TermCandidates:
    tokens: List[str]
    ngrams: List[str]
    proper_nouns: List[str]


def generate_ngrams(
    tokens: Iterable[str],
    min_n: int = 1,
    max_n: int = 4,
    normalize: Callable[[str], str] | None = str.lower,
) -> List[str]:
    """Generate n-grams from tokens.

    Args:
        tokens: Input token sequence.
        min_n: Minimum n-gram size.
        max_n: Maximum n-gram size.
        normalize: Optional normalization function applied per token.
    """
    token_list = list(tokens)
    if normalize is not None:
        token_list = [normalize(token) for token in token_list]
    ngrams: List[str] = []
    count = len(token_list)
    for n in range(min_n, max_n + 1):
        for start in range(0, max(count - n + 1, 0)):
            ngrams.append(" ".join(token_list[start : start + n]))
    return ngrams


def extract_term_candidates(
    text: str,
    min_n: int = 1,
    max_n: int = 4,
    normalize: Callable[[str], str] | None = str.lower,
) -> TermCandidates:
    tokens = tokenize(text)
    ngrams = generate_ngrams(tokens, min_n=min_n, max_n=max_n, normalize=normalize)
    proper_nouns = extract_capitalized_phrases(tokens)
    return TermCandidates(tokens=tokens, ngrams=ngrams, proper_nouns=proper_nouns)
