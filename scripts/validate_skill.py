#!/usr/bin/env python3
"""Validate the SP Data360 Mastery skill before it is published.

Checks:
  * SKILL.md frontmatter (name, description) and size limits
  * every relative Markdown link resolves; every reference file is linked from SKILL.md
  * publication safety: credentials, Data 360 tenant hosts, org and record IDs,
    and customer terms supplied privately (BANNED_TERMS env var or .customer-terms.txt)
  * Marketing Cloud Personalization (MCP) pages are cited only in references/sp-vs-mcp.md
    or under a heading that mentions MCP
  * each reference file carries inline citations

Exit code 0 when no errors are found (warnings are allowed unless --strict).
Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
SKILL_FILE = ROOT / "SKILL.md"
REFERENCES_DIR = ROOT / "references"
DEFAULT_TERMS_FILE = ROOT / ".customer-terms.txt"
MCP_COMPARISON_FILE = Path("references/sp-vs-mcp.md")
EXPECTED_NAME = "sp-data360-mastery"

SKILL_MAX_LINES = 500
REFERENCE_WARN_LINES = 500
REFERENCE_MAX_LINES = 600
MIN_CITATIONS_PER_REFERENCE = 10
DESCRIPTION_MAX_CHARS = 1024

TEXT_SUFFIXES = {".md", ".yml", ".yaml", ".py", ".txt", ".json"}
SKIP_DIRS = {".git", "__pycache__"}

LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
INLINE_CODE_PATTERN = re.compile(r"`[^`]*`")
CITATION_PATTERN = re.compile(r"\[src\]\(https?://[^)\s]+\)")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)")
FRONTMATTER_KEY = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")

SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Slack token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    "Private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}
ORG_IDENTIFIER_PATTERNS = {
    "Data 360 tenant host": re.compile(r"\b[a-z0-9]{16,}\.c360a\.salesforce\.com\b", re.IGNORECASE),
    "Salesforce org ID": re.compile(r"\b00D[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?\b"),
    "Personalization record ID": re.compile(r"\b(?:9pp|9pb|0Wl)(?!X+\b)[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?\b"),
}
MCP_SOURCE_URL = re.compile(
    r"https?://[^\s)\]]*(?:docs/marketing/personalization/|id=mktg\.mc_pers_)",
    re.IGNORECASE,
)

Finding = Tuple[str, str, int, str]


class Report:
    def __init__(self) -> None:
        self.findings: List[Finding] = []

    def error(self, path: Path, line: int, message: str) -> None:
        self.findings.append(("ERROR", rel(path), line, message))

    def warn(self, path: Path, line: int, message: str) -> None:
        self.findings.append(("WARN", rel(path), line, message))

    def count(self, level: str) -> int:
        return sum(1 for finding in self.findings if finding[0] == level)

    def print(self) -> None:
        for level, path, line, message in sorted(self.findings, key=lambda f: (f[1], f[2], f[0])):
            location = f"{path}:{line}" if line else path
            print(f"{level:<5}  {location}  {message}")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_lines(path: Path) -> List[str]:
    return path.read_text(encoding="utf-8").splitlines()


def parse_frontmatter(lines: List[str]) -> Tuple[Dict[str, str], int]:
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with a '---' frontmatter block")
    end = next((i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None)
    if end is None:
        raise ValueError("frontmatter block is not closed with '---'")

    fields: Dict[str, str] = {}
    key = None
    block: List[str] = []
    for line in lines[1:end]:
        match = FRONTMATTER_KEY.match(line)
        if match and not line[:1].isspace():
            if key is not None:
                fields[key] = " ".join(block).strip()
            key, value = match.group(1), match.group(2).strip()
            block = [] if value in (">", ">-", "|", "|-") else [value.strip("\"'")]
        elif key is not None:
            block.append(line.strip())
    if key is not None:
        fields[key] = " ".join(block).strip()
    return fields, end


def check_skill_file(report: Report) -> None:
    if not SKILL_FILE.exists():
        report.error(SKILL_FILE, 0, "SKILL.md is missing")
        return
    lines = read_lines(SKILL_FILE)
    try:
        fields, _ = parse_frontmatter(lines)
    except ValueError as exc:
        report.error(SKILL_FILE, 1, str(exc))
        return

    name = fields.get("name", "")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        report.error(SKILL_FILE, 1, "name must be 1-64 lowercase letters, digits or hyphens")
    elif name != EXPECTED_NAME:
        report.error(SKILL_FILE, 1, f"name must be '{EXPECTED_NAME}' (install folder name)")

    description = fields.get("description", "")
    if not description:
        report.error(SKILL_FILE, 1, "description is required")
    elif len(description) > DESCRIPTION_MAX_CHARS:
        report.error(SKILL_FILE, 1, f"description exceeds {DESCRIPTION_MAX_CHARS} characters")
    elif re.match(r"^(I|You|We)\b", description):
        report.warn(SKILL_FILE, 1, "description should be written in the third person")
    if "Salesforce Personalization" not in description:
        report.warn(SKILL_FILE, 1, "description should name 'Salesforce Personalization' for discovery")
    if fields.get("disable-model-invocation", "").lower() == "true":
        report.warn(SKILL_FILE, 1, "disable-model-invocation is true; the skill will not auto-load")

    if len(lines) > SKILL_MAX_LINES:
        report.error(SKILL_FILE, 0, f"SKILL.md has {len(lines)} lines (limit {SKILL_MAX_LINES})")


def iter_markdown_files() -> Iterable[Path]:
    yield from sorted(p for p in ROOT.rglob("*.md") if not SKIP_DIRS.intersection(p.parts))


def prose_lines(path: Path) -> Iterable[Tuple[int, str]]:
    """Yield (line number, text) outside fenced code blocks, with inline code removed."""
    in_fence = False
    for number, line in enumerate(read_lines(path), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, INLINE_CODE_PATTERN.sub("", line)


def check_links(report: Report) -> None:
    for path in iter_markdown_files():
        for number, line in prose_lines(path):
            for target in LINK_PATTERN.findall(line):
                if re.match(r"^(https?:|mailto:|#)", target):
                    continue
                file_part = target.split("#", 1)[0]
                if file_part and not (path.parent / file_part).exists():
                    report.error(path, number, f"broken link: {target}")


def check_reference_coverage(report: Report) -> None:
    if not REFERENCES_DIR.is_dir():
        report.error(REFERENCES_DIR, 0, "references/ directory is missing")
        return
    skill_links = set()
    if SKILL_FILE.exists():
        for _, line in prose_lines(SKILL_FILE):
            skill_links.update(t.split("#", 1)[0] for t in LINK_PATTERN.findall(line))

    for path in sorted(REFERENCES_DIR.glob("*.md")):
        relative = f"references/{path.name}"
        if relative not in skill_links:
            report.error(path, 0, "reference file is not linked from SKILL.md")
        lines = read_lines(path)
        if len(lines) > REFERENCE_MAX_LINES:
            report.error(path, 0, f"{len(lines)} lines (limit {REFERENCE_MAX_LINES})")
        elif len(lines) > REFERENCE_WARN_LINES:
            report.warn(path, 0, f"{len(lines)} lines (target {REFERENCE_WARN_LINES} or fewer)")
        citations = sum(len(CITATION_PATTERN.findall(line)) for line in lines)
        if citations < MIN_CITATIONS_PER_REFERENCE:
            report.warn(path, 0, f"only {citations} [src](url) citations")


def check_mcp_citations(report: Report) -> None:
    candidates = [SKILL_FILE] + sorted(REFERENCES_DIR.glob("*.md"))
    for path in candidates:
        if not path.exists() or path.relative_to(ROOT) == MCP_COMPARISON_FILE:
            continue
        heading = ""
        for number, line in enumerate(read_lines(path), start=1):
            match = HEADING_PATTERN.match(line)
            if match and len(match.group(1)) <= 3:
                heading = match.group(2)
            if MCP_SOURCE_URL.search(line) and "MCP" not in heading:
                report.error(
                    path,
                    number,
                    "cites a Marketing Cloud Personalization page outside an MCP section",
                )


def load_customer_terms(terms_file: Path) -> List[str]:
    raw: List[str] = []
    env_value = os.environ.get("BANNED_TERMS", "")
    raw.extend(re.split(r"[,\n]", env_value))
    if terms_file.exists():
        raw.extend(read_lines(terms_file))
    return sorted({term.strip() for term in raw if term.strip() and not term.strip().startswith("#")})


def iter_text_files(exclude: Path) -> Iterable[Path]:
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or SKIP_DIRS.intersection(path.parts) or path == exclude:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"CODEOWNERS", ".gitignore"}:
            yield path


def check_publication_safety(report: Report, terms_file: Path) -> int:
    terms = load_customer_terms(terms_file)
    term_patterns = [
        (term, re.compile(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", re.IGNORECASE))
        for term in terms
    ]
    for path in iter_text_files(exclude=terms_file):
        for number, line in enumerate(read_lines(path), start=1):
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    report.error(path, number, f"possible {label}")
            for label, pattern in ORG_IDENTIFIER_PATTERNS.items():
                if pattern.search(line):
                    report.error(path, number, f"possible {label}; use a placeholder")
            for term, pattern in term_patterns:
                if pattern.search(line):
                    report.error(path, number, "customer or project term found (see private terms list)")
    return len(terms)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument(
        "--terms-file",
        type=Path,
        default=DEFAULT_TERMS_FILE,
        help="file with customer terms to block, one per line (default: .customer-terms.txt)",
    )
    args = parser.parse_args()

    report = Report()
    check_skill_file(report)
    check_links(report)
    check_reference_coverage(report)
    check_mcp_citations(report)
    term_count = check_publication_safety(report, args.terms_file.resolve())

    report.print()
    errors, warnings = report.count("ERROR"), report.count("WARN")
    print(f"\n{errors} error(s), {warnings} warning(s); {term_count} private customer term(s) checked.")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
