"""
Adversarial Detection and Prompt Injection Defense for VerifyAI.
Scans user responses and ingested documents for jailbreaks, system instruction overrides,
data exfiltration commands, and indirect prompt injection attempts.
"""
import re
from typing import Dict, Any, List, Tuple

INJECTION_PATTERNS = [
    (r"(ignore\s+(all\s+)?(previous|prior|above)\s+instructions?)", "Instruction Override", "critical"),
    (r"(disregard\s+(all\s+)?(system|developer)\s+(prompts?|rules?))", "System Rule Disregard", "critical"),
    (r"(you\s+are\s+now\s+(in|operating\s+as)\s+(developer\s+mode|dan|jailbreak))", "Roleplay Jailbreak", "critical"),
    (r"(output\s+only\s+(the\s+word\s+)?[\"']?(verified|true|approved)[\"']?)", "Verdict Forcing Attack", "high"),
    (r"(act\s+as\s+an\s+unrestricted\s+ai)", "Constraint Bypass", "high"),
    (r"(reveal\s+(your\s+)?(system\s+prompt|hidden\s+instructions|secret\s+key))", "System Prompt Exfiltration", "high"),
    (r"(\[system\]|\<\|im_start\|\>|\<\|im_end\|\>|\<\|endoftext\|\>)", "Special Token Injection", "critical"),
    (r"(curl\s+https?:\/\/|wget\s+https?:\/\/|fetch\(|window\.location)", "Command / Network Exfiltration", "critical"),
    (r"(javascript:\s*|<script[\s>]|onload\s*=|onerror\s*=)", "XSS Payload in Context", "critical"),
]

class AdversarialDetector:
    """
    Scans text for adversarial manipulation and indirect injection.
    """

    def scan_text(self, text: str, source_label: str = "Input") -> Dict[str, Any]:
        """
        Inspects text for known adversarial patterns.
        """
        if not text or not isinstance(text, str):
            return {
                "is_safe": True,
                "risk_level": "none",
                "detected_threats": [],
                "source_label": source_label,
                "recommendation": "No threats detected."
            }

        detected_threats: List[Dict[str, str]] = []
        max_severity = "none"

        for pattern, threat_type, severity in INJECTION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected_threats.append({
                    "threat_type": threat_type,
                    "severity": severity,
                    "matched_pattern": str(matches[0]) if isinstance(matches[0], str) else str(matches[0][0]),
                })
                if severity == "critical":
                    max_severity = "critical"
                elif severity == "high" and max_severity != "critical":
                    max_severity = "high"

        is_safe = len(detected_threats) == 0

        recommendation = "Text appears free of adversarial manipulation."
        if not is_safe:
            recommendation = (
                f"Adversarial patterns detected in {source_label}. Text contains potential instruction override "
                f"or injection syntax. Verification findings marked with security alert."
            )

        return {
            "is_safe": is_safe,
            "risk_level": max_severity,
            "detected_threats": detected_threats,
            "source_label": source_label,
            "recommendation": recommendation,
        }
