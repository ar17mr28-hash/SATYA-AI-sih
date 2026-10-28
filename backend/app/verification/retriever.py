"""
Evidence Retrieval and Chunking Module for VerifyAI.
Indexes source evidence from uploaded documents or plain text passages,
computes BM25-style lexical relevance and entity alignment,
and returns cited ground-truth excerpts.
"""
import math
import re
from typing import List, Dict, Any, Optional

class EvidenceChunk:
    def __init__(
        self,
        chunk_id: str,
        source_id: str,
        source_title: str,
        content: str,
        page_number: Optional[int] = 1,
        chunk_index: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.chunk_id = chunk_id
        self.source_id = source_id
        self.source_title = source_title
        self.content = content.strip()
        self.page_number = page_number or 1
        self.chunk_index = chunk_index
        self.metadata = metadata or {}
        # Pre-tokenized lower tokens for fast lookup
        self.tokens = self._tokenize(self.content)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z0-9_\-.]+\b", text.lower())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "source_id": self.source_id,
            "source_title": self.source_title,
            "content": self.content,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata,
        }

class RetrievedEvidence:
    def __init__(
        self,
        chunk: EvidenceChunk,
        relevance_score: float,
        matched_tokens: List[str],
        verbatim_snippet: str,
    ):
        self.chunk = chunk
        self.relevance_score = relevance_score
        self.matched_tokens = matched_tokens
        self.verbatim_snippet = verbatim_snippet

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk.chunk_id,
            "source_id": self.chunk.source_id,
            "source_title": self.chunk.source_title,
            "page_number": self.chunk.page_number,
            "relevance_score": round(self.relevance_score, 3),
            "matched_tokens": self.matched_tokens,
            "verbatim_snippet": self.verbatim_snippet,
        }

class EvidenceRetriever:
    """
    In-memory chunker and BM25-inspired lexical evidence retriever.
    Operates deterministically without external vector API costs or latency.
    """

    def __init__(self, chunk_size: int = 350, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks: List[EvidenceChunk] = []
        self.doc_freqs: Dict[str, int] = {}
        self.total_docs: int = 0
        self.avg_doc_len: float = 0.0

    def add_document(
        self,
        source_id: str,
        source_title: str,
        text: str,
        page_number: Optional[int] = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[EvidenceChunk]:
        """
        Chunks and indexes a document.
        """
        if not text or not isinstance(text, str):
            return []

        # Split text into paragraphs or sliding windows
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        new_chunks = []
        chunk_idx = len(self.chunks)

        for p in paragraphs:
            # If paragraph is within reasonable size, use as one chunk
            if len(p) <= self.chunk_size * 2:
                chunk = EvidenceChunk(
                    chunk_id=f"CHK-{chunk_idx:04d}",
                    source_id=source_id,
                    source_title=source_title,
                    content=p,
                    page_number=page_number,
                    chunk_index=chunk_idx,
                    metadata=metadata,
                )
                new_chunks.append(chunk)
                self.chunks.append(chunk)
                chunk_idx += 1
            else:
                # Sliding window split
                words = p.split()
                step = self.chunk_size // 5  # approximate words per chunk
                overlap_words = self.chunk_overlap // 5
                i = 0
                while i < len(words):
                    window = " ".join(words[i : i + step])
                    chunk = EvidenceChunk(
                        chunk_id=f"CHK-{chunk_idx:04d}",
                        source_id=source_id,
                        source_title=source_title,
                        content=window,
                        page_number=page_number,
                        chunk_index=chunk_idx,
                        metadata=metadata,
                    )
                    new_chunks.append(chunk)
                    self.chunks.append(chunk)
                    chunk_idx += 1
                    i += max(1, step - overlap_words)

        self._rebuild_index()
        return new_chunks

    def _rebuild_index(self):
        self.total_docs = len(self.chunks)
        if self.total_docs == 0:
            return

        self.doc_freqs = {}
        total_len = 0
        for chunk in self.chunks:
            total_len += len(chunk.tokens)
            unique_tokens = set(chunk.tokens)
            for t in unique_tokens:
                self.doc_freqs[t] = self.doc_freqs.get(t, 0) + 1

        self.avg_doc_len = total_len / self.total_docs

    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.05) -> List[RetrievedEvidence]:
        """
        Retrieves top relevant evidence chunks for a query or claim.
        Returns empty list if no chunks or query is empty.
        """
        if not query or not self.chunks:
            return []

        query_tokens = [t for t in EvidenceChunk._tokenize(query) if len(t) > 2]
        if not query_tokens:
            return []

        # BM25 scoring parameters
        k1 = 1.5
        b = 0.75

        scored: List[tuple] = []

        for chunk in self.chunks:
            score = 0.0
            matched = []
            chunk_len = len(chunk.tokens)
            if chunk_len == 0:
                continue

            chunk_token_counts = {}
            for t in chunk.tokens:
                chunk_token_counts[t] = chunk_token_counts.get(t, 0) + 1

            for q in query_tokens:
                if q in chunk_token_counts:
                    matched.append(q)
                    tf = chunk_token_counts[q]
                    df = self.doc_freqs.get(q, 1)
                    # Safe IDF
                    idf = math.log(1.0 + (self.total_docs - df + 0.5) / (df + 0.5))
                    idf = max(idf, 0.2)

                    # Term saturation
                    denom = tf + k1 * (1.0 - b + b * (chunk_len / (self.avg_doc_len or 1.0)))
                    score += idf * (tf * (k1 + 1.0)) / denom

            # Numerical or entity match boost
            query_lower = query.lower()
            numbers_in_query = re.findall(r"\b\d+(?:\.\d+)?\b", query)
            for num in numbers_in_query:
                if num in chunk.content:
                    score += 1.5

            if matched:
                overlap_ratio = len(set(matched)) / len(set(query_tokens))
                score += overlap_ratio * 2.0

            if score >= min_score and matched:
                snippet = self._extract_best_snippet(chunk.content, matched)
                scored.append((score, chunk, matched, snippet))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for s, chunk, matched, snippet in scored[:top_k]:
            overlap_ratio = len(set(matched)) / len(set(query_tokens))
            # Blended relevance score (0.0 to 1.0)
            norm_score = min(1.0, 0.3 * min(1.0, s / 4.0) + 0.7 * overlap_ratio)
            results.append(
                RetrievedEvidence(
                    chunk=chunk,
                    relevance_score=norm_score,
                    matched_tokens=list(set(matched)),
                    verbatim_snippet=snippet,
                )
            )

        return results

    def _extract_best_snippet(self, content: str, matched_tokens: List[str], max_len: int = 220) -> str:
        """
        Extracts a compact, verbatim snippet highlighting matched keywords.
        """
        sentences = re.split(r"(?<=[.!?])\s+", content)
        best_sentence = content[:max_len]
        max_matches = 0

        for s in sentences:
            s_lower = s.lower()
            count = sum(1 for t in matched_tokens if t in s_lower)
            if count > max_matches:
                max_matches = count
                best_sentence = s

        if len(best_sentence) > max_len:
            return best_sentence[:max_len].strip() + "..."
        return best_sentence.strip()
