import re

# canonical name -> regex patterns, matched against lowercased text.
SKILL_KEYWORDS: dict[str, list[str]] = {
    "Python": [r"\bpython\d?\b"],
    "JavaScript": [r"\bjavascript\b", r"\becmascript\b"],
    "TypeScript": [r"\btypescript\b"],
    "React": [r"\breact(?:\.?js)?\b(?!\s+to\b)"],
    "Next.js": [r"\bnext\.?js\b"],
    "Vue": [r"\bvue(?:\.?js)?\b"],
    "Angular": [r"\bangular(?:js)?\b"],
    "Node.js": [r"\bnode\.?js\b"],
    "Django": [r"\bdjango\b"],
    "FastAPI": [r"\bfast\s?api\b"],
    "Flask": [r"\bflask\b"],
    "Go": [r"\bgolang\b", r"\bgo (?:programming|language|developer|engineer)\b"],
    "Rust": [r"\brust\b"],
    "Java": [r"\bjava\b(?!\s*script)"],
    "Kotlin": [r"\bkotlin\b"],
    "Swift": [r"\bswift(?:ui)?\b(?!-)"],
    "C++": [r"(?<![\w+])c\+\+"],
    "C#": [r"(?<!\w)c#"],
    ".NET": [r"(?<![\w.])\.net\b", r"\basp\.net\b"],
    "PHP": [r"\bphp\b"],
    "Ruby": [r"\bruby\b"],
    "Rails": [r"\brails\b"],
    "SQL": [r"\bsql\b"],
    "PostgreSQL": [r"\bpostgres(?:ql)?\b"],
    "MySQL": [r"\bmysql\b"],
    "MongoDB": [r"\bmongo(?:db)?\b"],
    "Redis": [r"\bredis\b"],
    "GraphQL": [r"\bgraph\s?ql\b"],
    "REST": [r"\brestful\b", r"\brest\s?apis?\b"],
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "AWS": [r"\baws\b", r"\bamazon web services\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle cloud\b"],
    "Azure": [r"\bazure\b"],
    "Terraform": [r"\bterraform\b"],
    "Git": [r"\bgit\b"],
    "Linux": [r"\blinux\b"],
    "Machine Learning": [r"\bmachine[\s-]learning\b", r"\bml\b"],
    "Data Science": [r"\bdata scien(?:ce|tists?)\b"],
    "Figma": [r"\bfigma\b"],
}

_COMPILED: dict[str, list[re.Pattern[str]]] = {
    name: [re.compile(p) for p in patterns] for name, patterns in SKILL_KEYWORDS.items()
}


def extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    return sorted(
        name for name, patterns in _COMPILED.items() if any(p.search(lowered) for p in patterns)
    )
