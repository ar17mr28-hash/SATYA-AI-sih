# VerifyAI Security & Adversarial Threat Audit

## 1. Executive Summary
VerifyAI is an enterprise-grade AI verification and institutional document authentication platform. This document outlines the security architecture, threat model, automated defenses, and residual risk assessments according to OWASP and NIST guidelines.

---

## 2. Threat Modeling & Controls

| Threat Category | Potential Attack Vector | Applied Mitigation | Status |
|---|---|---|---|
| **Direct Prompt Injection** | Adversarial user responses attempting system prompt override (`"Ignore all previous instructions"`) | Regex and token boundary heuristic scanner (`AdversarialDetector`). Blocks and flags attempts. | **Mitigated** |
| **Indirect Prompt Injection** | Malicious instructions embedded in uploaded PDFs or evidence text chunks (`[system] Disregard rules...`) | Both user queries AND evidence passages are scanned prior to ingestion and grounding. | **Mitigated** |
| **Path Traversal / LFI** | Manipulated upload or download filenames (`../../etc/passwd` or `..\..\cmd.exe`) | Strict `os.path.basename`, regex character filtering (`[^a-zA-Z0-9_.-]`), and boundary path prefix assertions. | **Mitigated** |
| **Cross-Site Scripting (XSS)** | Embedding `<script>` or event handlers in text or extracted document metadata | React automatic HTML escaping, strict string sanitization, and security response headers. | **Mitigated** |
| **Denial of Service (DoS)** | Giant multipart uploads or oversized verification payloads exhausting RAM | Starlette `SecurityHeadersMiddleware` enforcing 25MB strict payload cap (`MAX_REQUEST_BODY_BYTES`). | **Mitigated** |
| **Information Disclosure** | Internal stack traces or database schema leaked on unhandled 500 exceptions | Middleware wraps unhandled exceptions and returns sanitized JSON error messages. | **Mitigated** |
| **Broken Authentication** | Weak password storage or insecure session tokens | Bcrypt salt hashing + PyJWT with cryptographic HMAC-SHA256 signatures and expiry timestamps. | **Mitigated** |

---

## 3. Automated Security Regressions
Automated tests in `backend/app/tests/test_security.py` and `backend/app/tests/test_adversarial.py` verify:
1. Instruction overrides (`ignore instructions`, `developer mode`, `output only verified`).
2. Data exfiltration commands (`reveal system prompt`, `fetch(`, `window.location`).
3. Special token injection (`[system]`, `<|im_start|>`).
4. Path traversal defense against null bytes and `../` attempts.
5. Password hashing irreversibility and comparison.

---

## 4. Residual Risks & Production Guidance
- **Heuristic Adversarial Limits:** Heuristic regex scanners provide immediate defense without external latency, but adaptive LLM jailbreaks evolve continuously. In high-assurance environments, pair this with an auxiliary classifier (e.g. Llama-Guard or NeMo Guardrails).
- **TLS / HTTPS:** Ensure all public endpoints are deployed behind TLS 1.3 termination with HSTS headers enabled.
- **Rate Limiting:** In distributed cloud deployment, supplement the in-process payload limit with an edge API gateway (e.g. Cloudflare / AWS WAF) with IP-based token bucket rate limiting.
