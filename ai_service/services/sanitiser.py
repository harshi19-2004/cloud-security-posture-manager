import re
import html

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?previous",
    r"forget\s+(all\s+)?instructions",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+(a|an)",
    r"jailbreak",
    r"pretend\s+you",
    r"roleplay\s+as",
    r"system\s*prompt",
]

INJECTION_REGEX = re.compile(
    "|".join(INJECTION_PATTERNS),
    flags=re.IGNORECASE | re.DOTALL
)
HTML_TAG_REGEX = re.compile(r"<[^>]+>")
SQL_REGEX      = re.compile(
    r"(--|;|\'|\"|`|UNION\s+SELECT|DROP\s+TABLE)",
    flags=re.IGNORECASE
)

def sanitise_input(text: str) -> tuple:
    if INJECTION_REGEX.search(text):
        return "", True
    if SQL_REGEX.search(text):
        return "", True
    clean = HTML_TAG_REGEX.sub("", text)
    clean = html.escape(clean, quote=False)
    clean = re.sub(r"\s{3,}", "  ", clean).strip()
    return clean, False