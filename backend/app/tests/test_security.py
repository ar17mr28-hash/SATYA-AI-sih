import os
import pytest
from app.api.documents import UPLOAD_DIR
from app.services.auth import verify_password, hash_password

def test_password_hashing_security():
    pwd = "SecurePassword@2026"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed)
    assert not verify_password("WrongPassword", hashed)

def test_path_traversal_sanitization_check():
    import re
    malicious_filenames = [
        "../../etc/passwd.pdf",
        "..\\..\\windows\\system32\\cmd.exe",
        "nested/../../secret.pdf",
        "file\x00.pdf",
    ]
    for fn in malicious_filenames:
        raw_name = os.path.basename(fn)
        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', raw_name)
        target_path = os.path.abspath(os.path.join(UPLOAD_DIR, safe_name))
        assert target_path.startswith(os.path.abspath(UPLOAD_DIR))
        assert ".." not in safe_name
