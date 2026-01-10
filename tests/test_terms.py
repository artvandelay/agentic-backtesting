#!/usr/bin/env python3
"""Tests for term tokenization and n-gram extraction."""

import sys
sys.path.insert(0, 'src')

from nlbt.terms import extract_diff_terms, tokenize_diff


print("Testing term tokenization and n-gram extraction")
print("=" * 50)

added_text = "the article mentions New York Times and OpenAI research."
removed_text = "removed old version of beta api."

print("\n✓ Test 1: Tokenize added/removed text")
result = tokenize_diff(added_text, removed_text)
assert result.added.tokens == [
    "the",
    "article",
    "mentions",
    "New",
    "York",
    "Times",
    "and",
    "OpenAI",
    "research",
]
assert result.removed.tokens == ["removed", "old", "version", "of", "beta", "api"]
print("  Tokens extracted")

print("\n✓ Test 2: N-gram and proper noun extraction")
term_diff = extract_diff_terms(added_text, removed_text)
added_ngrams = set(term_diff.added.ngrams)
added_proper = set(term_diff.added.proper_nouns)

assert "new york" in added_ngrams
assert "new york times" in added_ngrams
assert "openai" in added_ngrams
assert "openai research" in added_ngrams

assert "New York Times" in added_proper
assert "OpenAI" in added_proper
print("  N-grams and proper nouns captured")

print("\n" + "=" * 50)
print("✅ Term tests passed!")
