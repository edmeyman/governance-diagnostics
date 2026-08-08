#!/usr/bin/env python3
"""Validate the committed v1.6.0 release artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "THE_FUMAN_MANIFESTO_v1.6.0.pdf"
COMPANION = ROOT / "COMPANION_NOTE_v1.6.0.pdf"
COMPANION_ALIAS = ROOT / "COMPANION_NOTE.pdf"

FERZ_SEPARATION_TERMS = (
    "grounding test",
    "authorization artifact",
    "pre-execution authorization",
    "runtime authorization boundary",
    "fail-closed governance",
    "effect-bearing action",
    "independently reconstructable",
    "observability versus authorization",
    "authorization boundary test",
    "reconstruction test",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pdf_text(reader: PdfReader) -> str:
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def check_pdf(
    path: Path,
    expected_pages: int,
    expected_title: str,
    required_terms: tuple[str, ...],
) -> PdfReader:
    require(path.exists(), f"Missing {path.name}")
    reader = PdfReader(path)
    require(len(reader.pages) == expected_pages, f"Unexpected page count in {path.name}")
    require(reader.metadata.title == expected_title, f"Incorrect title metadata in {path.name}")
    require(reader.metadata.author == "FERZ, Inc.", f"Incorrect author metadata in {path.name}")
    for page in reader.pages:
        require(
            tuple(float(value) for value in page.mediabox[2:]) == (612.0, 792.0),
            f"Non-letter page found in {path.name}",
        )
    text = pdf_text(reader)
    for term in required_terms:
        require(term in text, f"Missing required text in {path.name}: {term}")
    return reader


def main() -> int:
    main_reader = check_pdf(
        MAIN,
        25,
        "The Fuman Manifesto: A Governance Framework Diagnostic",
        (
            "Version 1.6.0",
            "PUBLIC DIAGNOSTIC EDITION",
            "Reader Notice",
            "tamper-proof ledger",
            "The framework does not prevent poor judgment",
            "Publication maintenance: reader notice, status, links, citation, metadata",
        ),
    )
    companion_reader = check_pdf(
        COMPANION,
        2,
        "The Fuman Manifesto Companion Note",
        (
            "satirical thought experiment",
            "closed loop",
            "separate from FERZ's technical standards",
            "https://github.com/edmeyman/governance-diagnostics",
            "https://ferz.ai",
        ),
    )

    combined = pdf_text(main_reader) + "\n" + pdf_text(companion_reader)
    for prohibited in (
        "CONFIDENTIAL DRAFT",
        "DRAFT FOR PUBLIC COMMENT",
        "ferzconsulting.com",
        "github.com/edmeyman/fuman-manifesto",
    ):
        require(prohibited not in combined, f"Superseded text remains: {prohibited}")

    for index, page in enumerate(main_reader.pages):
        if index == 1:
            continue
        require(len((page.extract_text() or "").strip()) > 80, f"Unexpected blank page: {index + 1}")

    require(COMPANION_ALIAS.exists(), "Missing COMPANION_NOTE.pdf alias")
    require(
        COMPANION_ALIAS.read_bytes() == COMPANION.read_bytes(),
        "COMPANION_NOTE.pdf is not identical to the current versioned note",
    )

    for path in (
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        ROOT / "CITATION.cff",
        ROOT / "RELEASE_NOTES_v1.6.0.md",
        ROOT / "sources" / "READER_NOTICE_v1.6.0.md",
        ROOT / "sources" / "COMPANION_NOTE_v1.6.0.md",
    ):
        require(path.exists(), f"Missing release file: {path.relative_to(ROOT)}")

    require(
        not (ROOT / "sources" / "DIAGNOSTIC_NOTE_v1.6.0.md").exists(),
        "Superseded diagnostic-note source remains",
    )

    public_text = combined + "\n" + "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "README.md",
            ROOT / "CHANGELOG.md",
            ROOT / "CITATION.cff",
            ROOT / "RELEASE_NOTES_v1.6.0.md",
            ROOT / "sources" / "README.md",
            ROOT / "sources" / "READER_NOTICE_v1.6.0.md",
            ROOT / "sources" / "COMPANION_NOTE_v1.6.0.md",
        )
    )
    public_text = public_text.lower()
    for term in FERZ_SEPARATION_TERMS:
        require(term not in public_text, f"FERZ technical terminology entered Fuman material: {term}")

    print("v1.6.0 validation passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
