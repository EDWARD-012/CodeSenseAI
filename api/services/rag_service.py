"""
RAG service for CodeSense AI.

Provides lightweight file-based retrieval of coding knowledge snippets.
Uses keyword-based scoring to find relevant documents.
"""

import json
import logging
import os
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

# Module-level cache for RAG documents (loaded once per process)
_rag_docs_cache = None
_review_rules_cache = None


def _load_json_file(filepath: str) -> list | dict:
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f'Failed to load RAG file {filepath}: {e}')
        return []


def get_rag_docs() -> list[dict]:
    """
    Load and cache RAG documents from data/rag-docs.json.
    Each document: { id, title, tags, content }
    """
    global _rag_docs_cache
    if _rag_docs_cache is None:
        filepath = Path(settings.BASE_DIR) / 'data' / 'rag-docs.json'
        _rag_docs_cache = _load_json_file(str(filepath))
        logger.info(f'Loaded {len(_rag_docs_cache)} RAG documents.')
    return _rag_docs_cache


def get_review_rules() -> list[dict]:
    """
    Load and cache review rules from data/code-review-rules.json.
    """
    global _review_rules_cache
    if _review_rules_cache is None:
        filepath = Path(settings.BASE_DIR) / 'data' / 'code-review-rules.json'
        _review_rules_cache = _load_json_file(str(filepath))
        logger.info(f'Loaded {len(_review_rules_cache)} review rules.')
    return _review_rules_cache


def _extract_keywords(text: str) -> set[str]:
    """
    Extract lowercase keywords from text.
    Filters out very short words and common stop words.
    """
    stop_words = {
        'the', 'a', 'an', 'is', 'it', 'in', 'on', 'at', 'to', 'for',
        'of', 'and', 'or', 'not', 'with', 'from', 'by', 'as', 'be',
        'this', 'that', 'are', 'was', 'were', 'has', 'have', 'had',
        'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should',
        'may', 'might', 'if', 'then', 'else', 'when', 'while', 'def',
        'return', 'import', 'class', 'function', 'var', 'let', 'const',
    }

    words = text.lower().split()
    # Keep alphanumeric words with length >= 3
    keywords = set()
    for word in words:
        cleaned = ''.join(c for c in word if c.isalnum() or c == '_')
        if len(cleaned) >= 3 and cleaned not in stop_words:
            keywords.add(cleaned)
    return keywords


def _score_document(doc: dict, query_keywords: set[str]) -> float:
    """
    Score a RAG document against query keywords.
    Higher score = more relevant.
    """
    score = 0.0

    # Title match (weighted 3x)
    title_keywords = _extract_keywords(doc.get('title', ''))
    title_overlap = query_keywords & title_keywords
    score += len(title_overlap) * 3.0

    # Tags match (weighted 2x)
    tags = doc.get('tags', [])
    tag_set = set(t.lower() for t in tags)
    tag_overlap = query_keywords & tag_set
    score += len(tag_overlap) * 2.0

    # Content match (weighted 1x)
    content_keywords = _extract_keywords(doc.get('content', ''))
    content_overlap = query_keywords & content_keywords
    score += len(content_overlap) * 1.0

    return score


def retrieve(
    code: str = '',
    language: str = '',
    review_mode: str = '',
    question: str = '',
    top_k: int = 3
) -> list[dict]:
    """
    Retrieve the most relevant RAG documents for the given context.

    Args:
        code: Source code being reviewed.
        language: Programming language.
        review_mode: Type of review (e.g., bugs, security).
        question: User's chat question.
        top_k: Number of top documents to return.

    Returns:
        List of top-k relevant documents.
    """
    if not getattr(settings, 'ENABLE_RAG', True):
        return []

    docs = get_rag_docs()
    if not docs:
        return []

    # Build combined query text
    query_parts = []
    if language:
        query_parts.append(language)
    if review_mode:
        query_parts.append(review_mode)
    if question:
        query_parts.append(question)
    if code:
        # Take first 500 chars of code for keyword matching
        query_parts.append(code[:500])

    query_text = ' '.join(query_parts)
    query_keywords = _extract_keywords(query_text)

    if not query_keywords:
        return docs[:top_k]  # Fallback: return first k docs

    # Score and rank documents
    scored_docs = []
    for doc in docs:
        score = _score_document(doc, query_keywords)
        if score > 0:
            scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)

    return [doc for _, doc in scored_docs[:top_k]]


def format_rag_context(documents: list[dict]) -> str:
    """
    Format retrieved documents into a prompt-friendly context string.
    """
    if not documents:
        return ''

    parts = ['--- REFERENCE CONTEXT ---']
    for i, doc in enumerate(documents, 1):
        title = doc.get('title', 'Untitled')
        content = doc.get('content', '')
        parts.append(f'\n[Reference {i}: {title}]\n{content}')
    parts.append('\n--- END REFERENCE CONTEXT ---')

    return '\n'.join(parts)
