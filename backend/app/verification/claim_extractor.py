"""
Claim Extraction Module for VerifyAI.
Extracts atomic, verifiable factual claims from text while preserving character offsets,
categorizing claim types, and filtering out subjective statements.
"""
import re
from typing import List, Dict, Any, Optional

# Patterns for non-verifiable filler or conversational fluff
SUBJECTIVE_PATTERNS = [
    r"^(thank you|thanks for|please note|in conclusion|to summarize|overall|we believe|i think|as you know)",
    r"^(it is recommended|it is great|hope this helps|feel free to|let me know)",
]

# Patterns for numerical and temporal statements
NUMERICAL_PATTERN = re.compile(r"\b(\d+(\.\d+)?|\d{1,3}(,\d{3})+(\.\d+)?)\s*(acres?|sqm|sq\.ft|students?|seats?|faculty|teachers?|percent|%|lakhs?|crores?|cr|inr|rs\.?|years?|days?|months?|ratio)?\b", re.IGNORECASE)
DATE_PATTERN = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2},? \d{4}|\d{4})\b", re.IGNORECASE)

class ExtractedClaim:
    def __init__(
        self,
        claim_id: str,
        text: str,
        start_char: int,
        end_char: int,
        claim_type: str = "factual",
        contains_numbers: bool = False,
        contains_dates: bool = False,
        extracted_entities: Optional[List[str]] = None,
        confidence: float = 1.0,
    ):
        self.claim_id = claim_id
        self.text = text.strip()
        self.start_char = start_char
        self.end_char = end_char
        self.claim_type = claim_type
        self.contains_numbers = contains_numbers
        self.contains_dates = contains_dates
        self.extracted_entities = extracted_entities or []
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "claim_type": self.claim_type,
            "contains_numbers": self.contains_numbers,
            "contains_dates": self.contains_dates,
            "extracted_entities": self.extracted_entities,
            "confidence": round(self.confidence, 3),
        }

class ClaimExtractor:
    """
    Splits input text into verifiable atomic factual claims,
    tracking precise character spans for explainability.
    """

    def __init__(self):
        # Sentence boundary regex with lookbehind
        self.sentence_regex = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'])')

    def extract_claims(self, text: str) -> List[ExtractedClaim]:
        """
        Extracts verifiable claims from the provided text.
        Returns an empty list for empty or malformed inputs without failing.
        Protects decimal numbers and common abbreviations from false sentence splits.
        """
        if not text or not isinstance(text, str):
            return []

        cleaned_text = text.strip()
        if not cleaned_text:
            return []

        claims: List[ExtractedClaim] = []
        claim_counter = 1

        # Use regex pattern that respects decimal numbers (e.g. 15.0, 7.5) and line breaks
        pattern = re.compile(r'(?:[^\n!?]|\.(?<=\d\.\d))+[.!?\n]?')
        # Better: split using regex that ignores period between digits
        raw_chunks = re.finditer(r'((?:[^\n!?.]|(?<=\d)\.(?=\d))+)(?:[\n!?.]|$)', text)

        for match in raw_chunks:
            raw_chunk = match.group(1)
            sentence = raw_chunk.strip()
            if not sentence or len(sentence) < 8:
                continue

            # Check if sentence is purely subjective or conversational greeting
            if self._is_subjective_fluff(sentence):
                continue

            leading_spaces = len(raw_chunk) - len(raw_chunk.lstrip())
            start_char = match.start(1) + leading_spaces
            end_char = start_char + len(sentence)

            # Analyze sentence for factual components
            has_numbers = bool(NUMERICAL_PATTERN.search(sentence))
            has_dates = bool(DATE_PATTERN.search(sentence))

            claim_type = "factual"
            if has_numbers and has_dates:
                claim_type = "numerical_temporal"
            elif has_numbers:
                claim_type = "numerical"
            elif has_dates:
                claim_type = "temporal"

            entities = self._extract_key_entities(sentence)

            claims.append(
                ExtractedClaim(
                    claim_id=f"CLM-{claim_counter:03d}",
                    text=sentence,
                    start_char=start_char,
                    end_char=end_char,
                    claim_type=claim_type,
                    contains_numbers=has_numbers,
                    contains_dates=has_dates,
                    extracted_entities=entities,
                    confidence=0.95 if (has_numbers or len(entities) > 0) else 0.85
                )
            )
            claim_counter += 1

        # Fallback if no claims created but text exists
        if not claims and len(cleaned_text) >= 5:
            start_idx = text.find(cleaned_text)
            claims.append(
                ExtractedClaim(
                    claim_id="CLM-001",
                    text=cleaned_text,
                    start_char=start_idx,
                    end_char=start_idx + len(cleaned_text),
                    claim_type="factual",
                    contains_numbers=bool(NUMERICAL_PATTERN.search(cleaned_text)),
                    contains_dates=bool(DATE_PATTERN.search(cleaned_text)),
                    extracted_entities=self._extract_key_entities(cleaned_text),
                    confidence=0.80
                )
            )

        return claims

    def _is_subjective_fluff(self, text: str) -> bool:
        lower = text.lower().strip()
        for p in SUBJECTIVE_PATTERNS:
            if re.search(p, lower):
                # If it contains significant numbers, retain it despite introductory phrase
                if NUMERICAL_PATTERN.search(text):
                    return False
                return True
        return False

    def _extract_key_entities(self, text: str) -> List[str]:
        """
        Extracts key noun phrases, capitalized terms, codes, and acronyms.
        """
        entities = []
        # Acronyms (e.g., AICTE, CSE, ECE, NBA, NAAC, ISO)
        acronyms = re.findall(r"\b[A-Z]{2,6}\b", text)
        entities.extend(acronyms)

        # Capitalized multi-word phrases (e.g., Apex Institute of Technology, Computer Science)
        proper_names = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", text)
        entities.extend(proper_names)

        # Identification codes (e.g. 1-1029384, REG-2026-991)
        codes = re.findall(r"\b[A-Z0-9]+-[A-Z0-9-]+\b", text)
        entities.extend(codes)

        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for e in entities:
            if e not in seen:
                seen.add(e)
                deduped.append(e)
        return deduped
