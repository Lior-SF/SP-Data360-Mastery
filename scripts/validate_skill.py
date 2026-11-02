#!/usr/bin/env python3
"""Validate the SP Data360 Mastery skill before it is published.

Checks:
  * SKILL.md frontmatter (name, description) and size limits
  * every relative Markdown link resolves, including #fragments (GitHub-style slugs);
    every reference file is linked from SKILL.md and listed in the README,
    CONTRIBUTING and the issue template
  * cross-references such as `decisioning.md §1.6` (also in backticks, and the
    shorthands `web §` and `data §` for the field guides) point at real numbered headings
  * publication safety, in every text file: credentials, tenant hosts, org and record
    IDs, email addresses, and customer terms supplied privately (BANNED_TERMS env var,
    ~/.config/sp-data360-mastery/customer-terms.txt, .customer-terms.txt or --terms-file)
  * Marketing Cloud Personalization (MCP) pages are cited only in references/sp-vs-mcp.md,
    under a heading (level 1-3) that mentions MCP, or on a line that mentions MCP
  * each reference file has at most 500 lines and at least 10 official `[src]` citations
    (help.salesforce.com or developer.salesforce.com; other hosts must be labelled)

Exit code 0 when no errors are found (warnings are allowed unless --strict).
Use --require-terms to fail when no private customer terms were loaded.
Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
SKILL_FILE = ROOT / "SKILL.md"
REFERENCES_DIR = ROOT / "references"
USER_TERMS_FILE = Path.home() / ".config" / "sp-data360-mastery" / "customer-terms.txt"
REPO_TERMS_FILE = ROOT / ".customer-terms.txt"  # fallback; git-ignored
DEFAULT_TERMS_FILES = [USER_TERMS_FILE, REPO_TERMS_FILE]
MCP_COMPARISON_FILE = Path("references/sp-vs-mcp.md")
EXPECTED_NAME = "sp-data360-mastery"

SKILL_MAX_LINES = 500
REFERENCE_MAX_LINES = 500
MIN_CITATIONS_PER_REFERENCE = 10
DESCRIPTION_MAX_CHARS = 1024

SKIP_DIRS = {".git", "__pycache__"}
OFFICIAL_CITATION_HOSTS = {"help.salesforce.com", "developer.salesforce.com"}
SECONDARY_LABELS = ("(workshop source)", "(third-party)")
FIELD_GUIDE_ALIAS = "field-guide-"  # `web §1.1` means field-guide-web.md, `data §1` field-guide-data.md
HISTORIC_MARKER = "since renumbered"  # lines with this marker skip the section check
ZERO_WIDTH = re.compile("[\u200b\u200c\u200d\u2060\ufeff]")

# A link target may contain one level of balanced parentheses and an optional "title".
URL_BODY = r"(?:[^()\s]|\([^()\s]*\))+"
LINK_PATTERN = re.compile(r"\[[^\]]*\]\((" + URL_BODY + r')(?:\s+"[^"]*")?\)')
INLINE_CODE_PATTERN = re.compile(r"`[^`]*`")
CITATION_PATTERN = re.compile(r"\[src\]\((https?://" + URL_BODY + r")\)")
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
    "Salesforce tenant host": re.compile(
        r"\b[a-z0-9-]+\.(?:sandbox\.)?(?:my\.salesforce\.com|my\.site\.com|lightning\.force\.com"
        r"|my\.salesforce-sites\.com|salesforce-setup\.com)\b",
        re.IGNORECASE,
    ),
}
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)\b")
EMAIL_ALLOWED_DOMAINS = {"example.com", "example.org", "example.net"}
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


def prose_lines(path: Path, keep_code: bool = False) -> Iterable[Tuple[int, str]]:
    """Yield (line number, text) outside fenced code blocks, with inline code removed
    (kept when keep_code is true)."""
    in_fence = False
    for number, line in enumerate(read_lines(path), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, line if keep_code else INLINE_CODE_PATTERN.sub("", line)


def slugify(heading: str) -> str:
    """GitHub-style anchor slug for a heading."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.replace("`", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


_ANCHOR_CACHE: Dict[Path, Set[str]] = {}


def anchors_of(path: Path) -> Set[str]:
    path = path.resolve()
    if path not in _ANCHOR_CACHE:
        seen: Dict[str, int] = {}
        found: Set[str] = set()
        in_fence = False
        for line in read_lines(path):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            match = None if in_fence else HEADING_PATTERN.match(line)
            if match:
                slug = slugify(match.group(2))
                count = seen.get(slug, 0)
                seen[slug] = count + 1
                found.add(slug if count == 0 else f"{slug}-{count}")
        _ANCHOR_CACHE[path] = found
    return _ANCHOR_CACHE[path]


def check_links(report: Report) -> None:
    for path in iter_markdown_files():
        for number, line in prose_lines(path):
            for target in LINK_PATTERN.findall(line):
                if re.match(r"^(https?:|mailto:)", target):
                    continue
                file_part, _, fragment = target.partition("#")
                resolved = path if not file_part else (path.parent / file_part)
                if not resolved.exists():
                    report.error(path, number, f"broken link: {target}")
                elif fragment and resolved.suffix == ".md":
                    if unquote(fragment).lower() not in anchors_of(resolved):
                        report.error(path, number, f"broken anchor: {target}")


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
        citations = 0
        for number, line in enumerate(lines, start=1):
            for url in CITATION_PATTERN.findall(line):
                host = (urlparse(url).hostname or "").lower()
                if host in OFFICIAL_CITATION_HOSTS:
                    citations += 1
                elif not any(label in line for label in SECONDARY_LABELS):
                    report.warn(path, number, f"[src] to {host} needs a (workshop source) or (third-party) label")
        if citations < MIN_CITATIONS_PER_REFERENCE:
            report.warn(path, 0, f"only {citations} official [src](url) citations")


def check_mcp_citations(report: Report) -> None:
    candidates = [SKILL_FILE, ROOT / "README.md", ROOT / "CONTRIBUTING.md"] + sorted(REFERENCES_DIR.glob("*.md"))
    for path in candidates:
        if not path.exists() or path.relative_to(ROOT) == MCP_COMPARISON_FILE:
            continue
        heading = ""
        for number, line in enumerate(read_lines(path), start=1):
            match = HEADING_PATTERN.match(line)
            if match and len(match.group(1)) <= 3:
                heading = match.group(2)
            if MCP_SOURCE_URL.search(line) and "MCP" not in heading and "MCP" not in line:
                report.error(
                    path,
                    number,
                    "cites a Marketing Cloud Personalization page without labeling it MCP",
                )


def check_reference_listings(report: Report) -> None:
    """Every reference file must appear in the README, CONTRIBUTING and the issue template."""
    listings = [
        ROOT / "README.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "incorrect-fact.yml",
    ]
    for listing in listings:
        if not listing.exists():
            continue
        text = "\n".join(read_lines(listing))
        for path in sorted(REFERENCES_DIR.glob("*.md")):
            if f"references/{path.name}" not in text:
                report.error(listing, 0, f"does not list references/{path.name}")


def heading_numbers(path: Path) -> set:
    numbers = set()
    for line in read_lines(path):
        match = HEADING_PATTERN.match(line)
        if match:
            number = re.match(r"(\d+(?:\.\d+)*)[.\s]", match.group(2) + " ")
            if number:
                numbers.add(number.group(1))
    return numbers


def check_section_references(report: Report) -> None:
    """A cross-reference such as `decisioning.md §1.6, §7.3` must point at real numbered headings.

    Also checked: names in backticks (`references/x.md` §2), ranges (§2.1–§2.3) and the
    shorthands `web §1.1` / `data §2` for field-guide-web.md / field-guide-data.md.
    Lines marked "since renumbered" (historic changelog entries) are skipped.
    """
    references = {p.stem: p for p in REFERENCES_DIR.glob("*.md")}
    headings = {stem: heading_numbers(path) for stem, path in references.items()}
    section_run = r"((?:§\s*\d+(?:\.\d+)*(?:\s*(?:,|and|–|—|-)\s*)?)+)"
    patterns = [
        re.compile(r"\]\((?:\.\./|references/)?([\w-]+)\.md(?:#[^)]*)?\)[^§\n]{0,40}?" + section_run),
        re.compile(r"(?<![\w-])(?:references/)?([\w-]+?)(?:\.md)?`?\s*" + section_run),
    ]
    reported: Set[Tuple[str, int, str]] = set()
    for path in iter_markdown_files():
        for number, line in prose_lines(path, keep_code=True):
            if HISTORIC_MARKER in line:
                continue
            for pattern in patterns:
                for match in pattern.finditer(line):
                    stem = match.group(1)
                    if stem not in headings and FIELD_GUIDE_ALIAS + stem in headings:
                        stem = FIELD_GUIDE_ALIAS + stem
                    if stem not in headings:
                        continue
                    for section in re.findall(r"§\s*(\d+(?:\.\d+)*)", match.group(2)):
                        key = (rel(path), number, f"{stem}§{section}")
                        if section not in headings[stem] and key not in reported:
                            reported.add(key)
                            report.error(path, number, f"{stem}.md has no numbered heading §{section}")


def load_customer_terms(terms_files: List[Path]) -> List[str]:
    raw: List[str] = []
    raw.extend(re.split(r"[,\n]", os.environ.get("BANNED_TERMS", "")))
    for terms_file in terms_files:
        if terms_file.exists():
            raw.extend(read_lines(terms_file))
    return sorted({term.strip() for term in raw if term.strip() and not term.strip().startswith("#")})


def term_pattern(term: str) -> "re.Pattern[str]":
    """Match a term case-insensitively; any run of whitespace in the term matches whitespace, "_" or "-"."""
    words = [re.escape(word) for word in term.split()]
    return re.compile(r"(?<![A-Za-z0-9])" + r"[\s_-]+".join(words) + r"(?![A-Za-z0-9])", re.IGNORECASE)


def iter_text_files(exclude: Set[Path]) -> Iterable[Tuple[Path, str]]:
    """Yield every readable UTF-8 text file in the repository (binary files are skipped)."""
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or SKIP_DIRS.intersection(path.parts) or path.resolve() in exclude:
            continue
        try:
            yield path, ZERO_WIDTH.sub("", path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue


def check_publication_safety(report: Report, terms_files: List[Path]) -> int:
    terms = load_customer_terms(terms_files)
    term_patterns = [(term, term_pattern(term)) for term in terms]
    exclude = {f.resolve() for f in terms_files}
    for path, text in iter_text_files(exclude):
        for number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    report.error(path, number, f"possible {label}")
            for label, pattern in ORG_IDENTIFIER_PATTERNS.items():
                if pattern.search(line):
                    report.error(path, number, f"possible {label}; use a placeholder")
            for email in EMAIL_PATTERN.finditer(line):
                if email.group(1).lower() not in EMAIL_ALLOWED_DOMAINS:
                    report.error(path, number, "possible email address; remove it")
        flagged = set()
        for number, line in enumerate(text.splitlines(), start=1):
            for term, pattern in term_patterns:
                if pattern.search(line):
                    flagged.add(term)
                    report.error(path, number, "customer or project term found (see private terms list)")
        collapsed = re.sub(r"\s+", " ", text)  # catches terms wrapped across lines
        for term, pattern in term_patterns:
            if term not in flagged and pattern.search(collapsed):
                report.error(path, 0, "customer or project term found across a line break (see private terms list)")
    return len(terms)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument(
        "--terms-file",
        type=Path,
        action="append",
        help="file with customer terms to block, one per line; repeatable. Default: "
        f"{USER_TERMS_FILE} and then .customer-terms.txt in the repository (BANNED_TERMS is always read too)",
    )
    parser.add_argument(
        "--require-terms",
        action="store_true",
        help="fail when no private customer terms were loaded (used by CI when the BANNED_TERMS secret exists)",
    )
    args = parser.parse_args()
    terms_files = [f.resolve() for f in (args.terms_file or DEFAULT_TERMS_FILES)]

    report = Report()
    check_skill_file(report)
    check_links(report)
    check_reference_coverage(report)
    check_reference_listings(report)
    check_section_references(report)
    check_mcp_citations(report)
    term_count = check_publication_safety(report, terms_files)
    if args.require_terms and term_count == 0:
        report.error(ROOT, 0, "no private customer terms loaded (set BANNED_TERMS or create a terms file)")

    report.print()
    errors, warnings = report.count("ERROR"), report.count("WARN")
    print(f"\n{errors} error(s), {warnings} warning(s); {term_count} private customer term(s) checked.")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
