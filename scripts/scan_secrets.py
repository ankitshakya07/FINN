import os
import re
from pathlib import Path

ROOT = Path(r"c:\Users\Ankit kumar\Downloads\finn_scaffold\finn")
EXCLUDE_DIRS = {".git", ".venv", ".venv-finn", "node_modules", ".next", "wheelhouse", "cdp-profile", "chrome-profile", "chrome-profile-desktop", "edge-profile", "__pycache__", ".pytest_cache", ".pytest_tmp"}

PATTERNS = [
    (r"(?i)(api[_-]?key|secret|password|auth[_-]?token|bearer|access[_-]?token)\s*[:=]\s*['\"]([^'\"]+)['\"]", "Key/Token Assignment"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (r"ghp_[0-9A-Za-z]{36}", "GitHub Personal Access Token"),
    (r"github_pat_[0-9A-Za-z_]{82}", "GitHub Fine-Grained Token"),
    (r"sk-[0-9A-Za-z]{32,}", "OpenAI/Generic Secret Key"),
]

findings = []

for p in ROOT.rglob("*"):
    if not p.is_file():
        continue
    if any(ex in p.parts for ex in EXCLUDE_DIRS):
        continue
    if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".ico", ".pdf", ".zip", ".whl", ".db", ".pyc", ".woff", ".woff2"}:
        continue
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
        
    for pat, desc in PATTERNS:
        for m in re.finditer(pat, content):
            matched_str = m.group(0)
            # Filter obvious false positives like empty strings, placeholders, or code defaults
            val = m.group(2) if m.groups() and len(m.groups()) >= 2 else matched_str
            if val in {"", "true", "false", "None", "null", "your-api-key-here", "your_secret_key", "change-this-in-production-use-a-strong-secret-key-32-chars-min", "change-me", "sqlite:///./test.db"}:
                continue
            if "REDACTED" in val or "example" in val.lower() or "placeholder" in val.lower():
                continue
            findings.append((p.relative_to(ROOT), desc, val[:4] + "..." if len(val) > 4 else "..."))

print(f"Scanned files in {ROOT}")
print(f"Total potential secret findings: {len(findings)}")
for fpath, desc, masked in findings:
    print(f"  {fpath}: {desc} (Value starts with: {masked})")

