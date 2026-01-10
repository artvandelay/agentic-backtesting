from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .ngrams import TermCandidates, extract_term_candidates
from .tokenizer import TokenizedText, tokenize_text


@dataclass(frozen=True)
class DiffTerms:
    added: TermCandidates
    removed: TermCandidates


@dataclass(frozen=True)
class DiffTokens:
    added: TokenizedText
    removed: TokenizedText


def tokenize_diff(
    added_text: str,
    removed_text: str,
    normalize: Callable[[str], str] | None = None,
) -> DiffTokens:
    return DiffTokens(
        added=tokenize_text(added_text, normalize=normalize),
        removed=tokenize_text(removed_text, normalize=normalize),
    )


def extract_diff_terms(
    added_text: str,
    removed_text: str,
    min_n: int = 1,
    max_n: int = 4,
    normalize: Callable[[str], str] | None = str.lower,
) -> DiffTerms:
    return DiffTerms(
        added=extract_term_candidates(added_text, min_n=min_n, max_n=max_n, normalize=normalize),
        removed=extract_term_candidates(
            removed_text, min_n=min_n, max_n=max_n, normalize=normalize
        ),
    )
