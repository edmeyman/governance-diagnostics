#!/usr/bin/env python3
"""Build The Fuman Manifesto v1.6.0 and its companion note.

The v1.5.0 PDF is retained as the historical base artifact. This build applies
the controlled v1.6.0 publication overlays, replaces the intentionally unused
page 5 with the diagnostic note, and generates the companion note from its
Markdown source.
"""

from __future__ import annotations

import html
import io
import re
from pathlib import Path

import fitz
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
BASE_PDF = ROOT / "THE_FUMAN_MANIFESTO_v1.5.0.pdf"
OUTPUT_PDF = ROOT / "THE_FUMAN_MANIFESTO_v1.6.0.pdf"
COMPANION_SOURCE = ROOT / "sources" / "COMPANION_NOTE_v1.6.0.md"
DIAGNOSTIC_SOURCE = ROOT / "sources" / "DIAGNOSTIC_NOTE_v1.6.0.md"
COMPANION_PDF = ROOT / "COMPANION_NOTE_v1.6.0.pdf"
COMPANION_ALIAS = ROOT / "COMPANION_NOTE.pdf"

PAGE_W, PAGE_H = letter
NAVY = colors.HexColor("#213F66")
BLUE = colors.HexColor("#2E6696")
GRAY = colors.HexColor("#777777")
LIGHT_BLUE = colors.HexColor("#EEF4F8")

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_DIR / "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", FONT_DIR / "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-Oblique", FONT_DIR / "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-BoldOblique", FONT_DIR / "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily(
    "DejaVuSans",
    normal="DejaVuSans",
    bold="DejaVuSans-Bold",
    italic="DejaVuSans-Oblique",
    boldItalic="DejaVuSans-BoldOblique",
)


def md_inline(text: str) -> str:
    """Convert the small inline Markdown subset used by the sources."""
    value = html.escape(text, quote=False)
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"\*(.+?)\*", r"<i>\1</i>", value)
    value = re.sub(
        r"(https://[^\s<]+)",
        r'<link href="\1" color="#2E6696">\1</link>',
        value,
    )
    return value


def parse_markdown(path: Path, styles: dict[str, ParagraphStyle]) -> list:
    lines = path.read_text(encoding="utf-8").splitlines()
    story: list = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            story.append(Paragraph(md_inline(" ".join(paragraph)), styles["Body"] ))
            story.append(Spacer(1, 7))
            paragraph.clear()

    for raw in lines:
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith("# "):
            flush()
            story.append(Paragraph(md_inline(line[2:]), styles["Title"]))
            story.append(Spacer(1, 5))
        elif line.startswith("## "):
            flush()
            story.append(Paragraph(md_inline(line[3:]), styles["H2"]))
            story.append(Spacer(1, 3))
        elif line.startswith("### "):
            flush()
            story.append(Paragraph(md_inline(line[4:]), styles["H3"]))
            story.append(Spacer(1, 2))
        elif line.startswith("- "):
            flush()
            story.append(Paragraph(md_inline(line[2:]), styles["Bullet"], bulletText="•"))
            story.append(Spacer(1, 3))
        elif re.match(r"^\d+\. ", line):
            flush()
            number, body = line.split(". ", 1)
            story.append(Paragraph(md_inline(body), styles["Bullet"], bulletText=f"{number}."))
            story.append(Spacer(1, 3))
        elif line.startswith("*") and line.endswith("*"):
            flush()
            story.append(Paragraph(md_inline(line), styles["Subtitle"]))
            story.append(Spacer(1, 6))
        else:
            paragraph.append(line)
    flush()
    return story


def base_styles(body_size: float = 9.7, leading: float = 12.5) -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle(
            "Title",
            parent=sample["Title"],
            fontName="DejaVuSans-Bold",
            fontSize=21,
            leading=25,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle",
            parent=sample["Normal"],
            fontName="DejaVuSans-Oblique",
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#444444"),
        ),
        "H2": ParagraphStyle(
            "H2",
            parent=sample["Heading2"],
            fontName="DejaVuSans-Bold",
            fontSize=13.2,
            leading=16,
            textColor=BLUE,
            spaceBefore=6,
            spaceAfter=3,
        ),
        "H3": ParagraphStyle(
            "H3",
            parent=sample["Heading3"],
            fontName="DejaVuSans-Bold",
            fontSize=10.7,
            leading=13,
            textColor=NAVY,
            spaceBefore=5,
            spaceAfter=2,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontName="DejaVuSans",
            fontSize=body_size,
            leading=leading,
            textColor=colors.HexColor("#161616"),
            alignment=TA_LEFT,
            spaceAfter=0,
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            parent=sample["BodyText"],
            fontName="DejaVuSans",
            fontSize=body_size,
            leading=leading,
            leftIndent=16,
            firstLineIndent=-10,
            bulletIndent=4,
            textColor=colors.HexColor("#161616"),
        ),
    }


def overlay_reader(draw_fn) -> PdfReader:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter, pageCompression=1)
    draw_fn(c)
    c.save()
    buffer.seek(0)
    return PdfReader(buffer)


def draw_cover_overlay(c: canvas.Canvas) -> None:
    c.setFillColor(colors.white)
    c.rect(175, 250, 265, 88, stroke=0, fill=1)
    c.setFillColor(colors.black)
    c.setFont("DejaVuSans-Bold", 9)
    c.drawCentredString(PAGE_W / 2, 319, "Version 1.6.0")
    c.setFillColor(colors.HexColor("#666666"))
    c.setFont("DejaVuSans", 9)
    c.drawCentredString(PAGE_W / 2, 300, "August 2026")
    c.setFillColor(BLUE)
    c.setFont("DejaVuSans-Bold", 8.4)
    c.drawCentredString(PAGE_W / 2, 281, "PUBLIC DIAGNOSTIC EDITION")


def draw_running_overlay(c: canvas.Canvas, page_number: int) -> None:
    c.setFillColor(colors.white)
    c.rect(385, 726, 210, 30, stroke=0, fill=1)
    c.rect(120, 31, 472, 27, stroke=0, fill=1)
    c.setFillColor(GRAY)
    c.setFont("DejaVuSans-Oblique", 7.5)
    c.drawRightString(572, 741, "The Fuman Manifesto v1.6.0")
    c.setFont("DejaVuSans", 7.5)
    c.drawCentredString(
        PAGE_W / 2,
        42,
        f"Page {page_number} | Fuman Integration Authority | PUBLIC DIAGNOSTIC EDITION",
    )


def draw_diagnostic_page(c: canvas.Canvas) -> None:
    c.setFillColor(colors.white)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_running_overlay(c, 5)

    styles = base_styles(body_size=9.6, leading=12.2)
    styles["Title"].alignment = TA_LEFT
    styles["Title"].fontSize = 20
    styles["Title"].leading = 23
    story = parse_markdown(DIAGNOSTIC_SOURCE, styles)
    available_height = 650
    from reportlab.platypus import Frame

    frame = Frame(68, 72, 476, available_height, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame.addFromList(story, c)


def draw_tamper_evident_overlay(c: canvas.Canvas) -> None:
    c.setFillColor(colors.white)
    c.rect(66, 474, 485, 45, stroke=0, fill=1)
    c.rect(66, 405, 485, 75, stroke=0, fill=1)
    style = ParagraphStyle(
        "Replacement",
        fontName="DejaVuSans",
        fontSize=9.5,
        leading=12,
        textColor=colors.black,
    )
    paragraph = Paragraph(
        "All flight operations must be logged in a tamper-evident ledger including altitude, wingbeat frequency, emotional state of both participants, and any disagreements about navigation resolved during flight.",
        style,
    )
    paragraph.wrapOn(c, 480, 42)
    paragraph.drawOn(c, 68, 484)
    c.setFillColor(colors.HexColor("#367CBA"))
    c.setFont("DejaVuSans-Bold", 10.2)
    c.drawString(68, 461, "6.2 Ethical Flight Constraints")
    constraint = Paragraph(
        "The fuman must not engage in aggressive aerial maneuvers targeting pedestrians, assert dominance over non-fuman species, or claim sovereign authority over airspace without proper certification from the Fuman Oversight Authority.",
        style,
    )
    constraint.wrapOn(c, 480, 48)
    constraint.drawOn(c, 68, 414)


def draw_page_25_revision(c: canvas.Canvas) -> None:
    from reportlab.platypus import Frame

    c.setFillColor(colors.white)
    c.rect(62, 414, 490, 246, stroke=0, fill=1)
    c.setFillColor(BLUE)
    c.setFont("DejaVuSans-Bold", 14.5)
    c.drawString(69, 640, "A.8 Framework Integration: Lessons Learned")

    body_style = ParagraphStyle(
        "A8Body",
        fontName="DejaVuSans",
        fontSize=8.5,
        leading=10.5,
        textColor=colors.black,
        spaceAfter=6,
    )
    story = [
        Paragraph(
            "The Overconfident Ascent Incident demonstrates the interdependence of the framework's components. CAST degradation generated warnings and extensive records, but no recorded step established that the ascent was permitted before execution.",
            body_style,
        ),
        Paragraph(
            "<b>Key insight:</b> CAST was an early-warning signal, not an authorization artifact. The logs explain how the incident developed; they do not prove that an authorized verdict preceded release. A serious framework would require the proposed ascent to cross a fail-closed runtime authorization boundary. Missing or unresolved authority would block execution.",
            body_style,
        ),
        Paragraph(
            "<i>Applicable beyond vertical sovereignty:</i> Multi-agent systems with asymmetric capabilities, shared authority, and effect-bearing actions face the same distinction. Observability can support investigation without providing authorization.",
            body_style,
        ),
        Paragraph(
            "<b>Cross-domain mapping:</b> Substitute principal for human, executing system for avian, effect-bearing action for trajectory, and authorization artifact for the pre-execution record. The relevant question is whether execution was permitted before the effect existed and whether an independent party can reconstruct that verdict.",
            body_style,
        ),
    ]
    frame = Frame(69, 426, 474, 198, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame.addFromList(story, c)

    c.setFillColor(colors.white)
    c.rect(60, 38, 495, 382, stroke=0, fill=1)
    c.setFillColor(BLUE)
    c.setFont("DejaVuSans-Bold", 15)
    c.drawString(69, 397, "Document History")

    data = [
        ["Version", "Date", "Description"],
        ["1.6.0", "Aug 2026", "Public diagnostic edition; authorization boundary and reconstruction tests; publication corrections"],
        ["1.5.0", "Jan 2026", "UD severity taxonomy, VNC terminology, retention requirements"],
        ["1.4.0", "Jan 2026", "CAST protocol, audit artifacts, governance axiom"],
        ["1.3.0", "Jan 2026", "CAST formalization, incident analysis, cross-domain bridge"],
        ["1.2.0", "Jan 2026", "Avian representation and arboreal stakeholders"],
        ["1.1.0", "Jan 2026", "Culinary guidelines and migratory treaties"],
        ["1.0.0", "Jan 2026", "Initial public draft for comment"],
        ["0.9.0", "Dec 2025", "Internal review draft"],
        ["0.1.0", "Nov 2025", "Foundational concepts established"],
    ]
    table = Table(data, colWidths=[68, 78, 328], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "DejaVuSans"),
                ("FONTSIZE", (0, 0), (-1, -1), 6.7),
                ("LEADING", (0, 0), (-1, -1), 8.2),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#333333")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    _, table_height = table.wrapOn(c, 474, 330)
    table.drawOn(c, 69, 382 - table_height)


def redacted_base() -> bytes:
    document = fitz.open(BASE_PDF)

    def mark(page, rect: fitz.Rect) -> None:
        page.add_redact_annot(rect, fill=(1, 1, 1))

    for index, page in enumerate(document):
        if index == 0:
            for term in ("Version 1.5.0", "January 2026", "DRAFT FOR PUBLIC COMMENT"):
                for rect in page.search_for(term):
                    mark(page, rect + (-8, -5, 8, 5))
        elif index >= 2:
            for rect in page.search_for("The Fuman Manifesto v1.5.0"):
                mark(page, rect + (-8, -4, 8, 4))
            footer = f"Page {index + 1} | Fuman Integration Authority | CONFIDENTIAL DRAFT"
            for rect in page.search_for(footer):
                mark(page, rect + (-8, -4, 8, 4))

        if index == 7:
            starts = page.search_for("All flight operations must be logged")
            ends = page.search_for("resolved during flight.")
            if starts and ends:
                mark(page, fitz.Rect(64, starts[0].y0 - 2, 553, ends[-1].y1 + 3))
            mark(page, fitz.Rect(64, 310, 553, 390))

        if index == 24:
            mark(page, fitz.Rect(58, 128, 555, 758))

    for page in document:
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    payload = document.tobytes(garbage=4, deflate=True)
    document.close()
    return payload


def build_manifesto() -> None:
    reader = PdfReader(io.BytesIO(redacted_base()))
    writer = PdfWriter()

    for index, original_page in enumerate(reader.pages):
        if index == 4:
            replacement = overlay_reader(draw_diagnostic_page).pages[0]
            writer.add_page(replacement)
            continue

        page = original_page
        if index == 0:
            page.merge_page(overlay_reader(draw_cover_overlay).pages[0])
        elif index >= 2:
            page.merge_page(overlay_reader(lambda c, n=index + 1: draw_running_overlay(c, n)).pages[0])

        if index == 7:
            page.merge_page(overlay_reader(draw_tamper_evident_overlay).pages[0])
        if index == 24:
            page.merge_page(overlay_reader(draw_page_25_revision).pages[0])
            page.merge_page(overlay_reader(lambda c: draw_running_overlay(c, 25)).pages[0])

        writer.add_page(page)

    writer.add_metadata(
        {
            "/Title": "The Fuman Manifesto: A Governance Framework Diagnostic",
            "/Author": "FERZ, Inc.",
            "/Subject": "A satirical diagnostic for governance grounding, pre-execution authorization, and independent verdict reconstruction",
            "/Keywords": "AI governance, authorization artifact, runtime authorization boundary, fail-closed governance, observability, satire",
            "/Creator": "FERZ, Inc. reproducible v1.6.0 build",
            "/Producer": "pypdf and ReportLab",
        }
    )
    with OUTPUT_PDF.open("wb") as stream:
        writer.write(stream)


def companion_page(canvas_obj: canvas.Canvas, doc) -> None:
    page_number = canvas_obj.getPageNumber()
    canvas_obj.saveState()
    canvas_obj.setFillColor(GRAY)
    canvas_obj.setFont("DejaVuSans-Oblique", 7.5)
    canvas_obj.drawRightString(7.5 * inch, 10.55 * inch, "FERZ, Inc. | Fuman Manifesto Companion Note v1.6.0")
    canvas_obj.setFont("DejaVuSans", 7.5)
    canvas_obj.drawCentredString(PAGE_W / 2, 0.42 * inch, f"Page {page_number} | PUBLIC DIAGNOSTIC EDITION")
    canvas_obj.restoreState()


def build_companion() -> None:
    styles = base_styles(body_size=9.4, leading=12.0)
    story = parse_markdown(COMPANION_SOURCE, styles)

    split_index = next(
        i
        for i, flowable in enumerate(story)
        if isinstance(flowable, Paragraph) and flowable.getPlainText() == "Three Tests the Manifesto Fails"
    )
    story.insert(split_index, PageBreak())

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.65 * inch,
        title="The Fuman Manifesto Companion Note",
        author="FERZ, Inc.",
        subject="Status, intent, and diagnostic use",
        pageCompression=1,
    )
    doc.build(story, onFirstPage=companion_page, onLaterPages=companion_page)
    buffer.seek(0)
    reader = PdfReader(buffer)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata(
        {
            "/Title": "The Fuman Manifesto Companion Note",
            "/Author": "FERZ, Inc.",
            "/Subject": "Status, intent, and diagnostic use",
            "/Keywords": "AI governance, authorization artifact, observability, satire",
            "/Creator": "FERZ, Inc. reproducible v1.6.0 build",
            "/Producer": "pypdf and ReportLab",
        }
    )
    with COMPANION_PDF.open("wb") as stream:
        writer.write(stream)
    COMPANION_ALIAS.write_bytes(COMPANION_PDF.read_bytes())


def main() -> None:
    build_manifesto()
    build_companion()
    print(f"Built {OUTPUT_PDF.name}")
    print(f"Built {COMPANION_PDF.name}")
    print(f"Updated {COMPANION_ALIAS.name}")


if __name__ == "__main__":
    main()
