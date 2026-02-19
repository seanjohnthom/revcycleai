#!/usr/bin/env python3
"""
Weekly RCM Trend Carousel
Generates a branded LinkedIn document post (PDF) every Friday
summarizing the top 5 RCM trends of the week.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "carousels"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand colors
NAVY       = colors.HexColor('#0D1F37')
BLUE       = colors.HexColor('#1D4ED8')
TEAL       = colors.HexColor('#1F4B43')
LIGHT_BLUE = colors.HexColor('#EFF6FF')
LIGHT_GRAY = colors.HexColor('#F4F4F5')
MID_GRAY   = colors.HexColor('#E4E4E7')
DARK_GRAY  = colors.HexColor('#52525B')
WHITE      = colors.white
BLACK      = colors.HexColor('#09090B')

# Slide size: 1:1 square (LinkedIn optimal for documents)
SLIDE_W = 7.5 * inch
SLIDE_H = 7.5 * inch


def load_weekly_trends():
    """Load trend data from engine output. Falls back to sample data."""
    trends_file = BASE_DIR / "output" / "trends.json"
    if trends_file.exists():
        with open(trends_file) as f:
            data = json.load(f)
        trends = data.get("trends", [])
        # Sort by score, take top 5
        trends = sorted(trends, key=lambda x: x.get("score", 0), reverse=True)[:5]
        return trends
    # Fallback sample data
    return [
        {
            "title": "CMS Finalizes New Prior Auth Rules for MA Plans",
            "summary": "Starting January 2027, Medicare Advantage plans must respond to prior auth requests within 7 calendar days for standard and 72 hours for expedited requests.",
            "source": "CMS.gov",
            "urgency": "high",
            "monetization_tags": ["axlow", "revcycleai"]
        },
        {
            "title": "UHC Expands Prior Auth Requirements — 1,300 New Codes",
            "summary": "UnitedHealthcare is adding 1,300 CPT codes to its prior authorization list. Effective April 1 for commercial and Medicare Advantage members.",
            "source": "UHC Provider",
            "urgency": "high",
            "monetization_tags": ["axlow"]
        },
        {
            "title": "Denial Rates Hit 5-Year High Across Hospital Systems",
            "summary": "Commercial payer denial rates increased to 11.1% in 2025, with initial denial rates rising 23% since 2016. Appeals success rates remain under 40%.",
            "source": "Becker's Hospital Review",
            "urgency": "medium",
            "monetization_tags": ["axlow", "revcycleai"]
        },
        {
            "title": "BCBS Implementing New Timely Filing Deadlines — Multiple States",
            "summary": "Blue Cross Blue Shield affiliates in TX, IL, and NC are reducing timely filing windows for professional claims from 180 to 120 days effective Q2 2026.",
            "source": "RevCycle Intelligence",
            "urgency": "medium",
            "monetization_tags": ["axlow", "payormap"]
        },
        {
            "title": "Zelis Network Expansion — 600+ New Dental Contracts",
            "summary": "Zelis has finalized leased network agreements covering 600 additional dental practices, effective immediately for Cigna and Aetna dental plans in 12 states.",
            "source": "Zelis",
            "urgency": "medium",
            "monetization_tags": ["payormap"]
        },
    ]


def urgency_color(urgency):
    if urgency == "high":
        return colors.HexColor('#DC2626')
    elif urgency == "medium":
        return colors.HexColor('#D97706')
    return colors.HexColor('#16A34A')


def urgency_label(urgency):
    labels = {"high": "🔴 HIGH IMPACT", "medium": "🟡 WATCH", "low": "🟢 FYI"}
    return labels.get(urgency, "📌 TREND")


def build_weekly_carousel(trends=None, week_label=None):
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab not installed. Run: pip install reportlab")

    if trends is None:
        trends = load_weekly_trends()

    if week_label is None:
        today = datetime.now()
        # Get the Monday of this week
        monday = today - timedelta(days=today.weekday())
        week_label = f"Week of {monday.strftime('%B %-d, %Y')}"

    timestamp = datetime.now().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"rcm-weekly-{timestamp}.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=(SLIDE_W, SLIDE_H),
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.4*inch,
        bottomMargin=0.4*inch,
    )

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    story = []

    # ── SLIDE 1: COVER ────────────────────────────────────────────────────────
    # Dark navy background via a full-width table
    cover_text = [
        [Paragraph(
            f'<font size="11" color="white">RevCycle<b>AI</b> &nbsp; · &nbsp; {week_label}</font>',
            S('cov_sub', fontName='Helvetica', fontSize=11, textColor=WHITE, leading=16)
        )],
        [Spacer(1, 0.15*inch)],
        [Paragraph(
            '<font size="32" color="white"><b>This Week in</b></font>',
            S('cov_h1a', fontName='Helvetica-Bold', fontSize=32, textColor=WHITE, leading=38, alignment=TA_LEFT)
        )],
        [Paragraph(
            '<font size="32"><b>Revenue Cycle</b></font>',
            S('cov_h1b', fontName='Helvetica-Bold', fontSize=32, textColor=colors.HexColor('#60A5FA'), leading=38, alignment=TA_LEFT)
        )],
        [Spacer(1, 0.1*inch)],
        [Paragraph(
            f'Top {len(trends)} trends RCM leaders are watching right now',
            S('cov_body', fontName='Helvetica', fontSize=13, textColor=colors.HexColor('#CBD5E1'), leading=18)
        )],
        [Spacer(1, 0.5*inch)],
        [Paragraph(
            '→ Swipe for this week\'s signals',
            S('cov_cta', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#93C5FD'), leading=16)
        )],
    ]

    cover_table = Table(cover_text, colWidths=[SLIDE_W - inch])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 0.3*inch),
        ('RIGHTPADDING', (0,0), (-1,-1), 0.3*inch),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    # Wrap cover in a full-bleed table
    outer = Table([[cover_table]], colWidths=[SLIDE_W - inch])
    outer.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING', (0,0), (-1,-1), 0.35*inch),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0.35*inch),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(outer)

    # ── SLIDES 2–6: ONE TREND PER PAGE ────────────────────────────────────────
    for i, trend in enumerate(trends, 1):
        story.append(_trend_slide(i, trend, len(trends), S, week_label))

    # ── SLIDE 7: CTA / CLOSING ────────────────────────────────────────────────
    story.append(_cta_slide(S, week_label))

    doc.build(story)
    print(f"✅ Carousel saved: {output_path}")
    return str(output_path)


def _trend_slide(num, trend, total, S, week_label):
    title = trend.get("title", "RCM Update")
    summary = trend.get("summary", "")
    source = trend.get("source", "")
    urgency = trend.get("urgency", "medium")
    tags = trend.get("monetization_tags", [])

    urg_color = urgency_color(urgency)
    urg_lbl = urgency_label(urgency)

    tag_str = ""
    if "axlow" in tags:
        tag_str += " <b>→ Axlow</b>"
    if "payormap" in tags:
        tag_str += " <b>→ PayorMap</b>"

    # Header bar as its own table
    header_inner = Table(
        [[
            Paragraph(
                f'<font size="9" color="white">{week_label} · {num} of {total}</font>',
                S(f'sm_{num}', fontName='Helvetica', fontSize=9, textColor=WHITE)
            ),
            Paragraph(
                '<font size="13" color="white"><b>RevCycleAI</b></font>',
                S(f'logo_{num}', fontName='Helvetica-Bold', fontSize=13, textColor=WHITE, alignment=1)
            )
        ]],
        colWidths=[3.8*inch, 2.2*inch]
    )
    header_inner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (0,0), 14),
        ('RIGHTPADDING', (-1,-1), (-1,-1), 14),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    content = [
        [header_inner],
        [Spacer(1, 0.2*inch)],
        [Paragraph(urg_lbl, S(f'urg_{num}', fontName='Helvetica-Bold', fontSize=10,
                              textColor=urg_color, leading=14))],
        [Spacer(1, 0.08*inch)],
        [Paragraph(title, S(f'ttl_{num}', fontName='Helvetica-Bold', fontSize=18,
                            textColor=BLACK, leading=24))],
        [Spacer(1, 0.15*inch)],
        [HRFlowable(width="100%", thickness=1, color=MID_GRAY)],
        [Spacer(1, 0.15*inch)],
        [Paragraph(summary, S(f'bod_{num}', fontName='Helvetica', fontSize=13,
                              textColor=DARK_GRAY, leading=20))],
        [Spacer(1, 0.2*inch)],
        [Paragraph(f'Source: {source}',
                   S(f'src_{num}', fontName='Helvetica-Oblique', fontSize=9,
                     textColor=colors.HexColor('#A1A1AA'), leading=13))],
    ]

    if tag_str:
        content.append([Spacer(1, 0.1*inch)])
        content.append([Paragraph(
            tag_str.strip(),
            S(f'tag_{num}', fontName='Helvetica-Bold', fontSize=10, textColor=TEAL, leading=14)
        )])

    t = Table(content, colWidths=[SLIDE_W - inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), WHITE),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return t


def _cta_slide(S, week_label):
    content = [
        [Spacer(1, 0.3*inch)],
        [Paragraph(
            '<b><font size="26" color="white">Stay ahead of</font></b>',
            S('cta_h1', fontName='Helvetica-Bold', fontSize=26, textColor=WHITE,
              leading=32, alignment=TA_CENTER)
        )],
        [Paragraph(
            '<b><font size="26" color="#60A5FA">every payor change.</font></b>',
            S('cta_h2', fontName='Helvetica-Bold', fontSize=26,
              textColor=colors.HexColor('#60A5FA'), leading=32, alignment=TA_CENTER)
        )],
        [Spacer(1, 0.25*inch)],
        [Paragraph(
            'Free weekly RCM intelligence — payor changes, prior auth\nupdates, denial trends, and benchmarks. Every Tuesday.',
            S('cta_body', fontName='Helvetica', fontSize=13, textColor=colors.HexColor('#CBD5E1'),
              leading=20, alignment=TA_CENTER)
        )],
        [Spacer(1, 0.3*inch)],
        [Table([[
            Paragraph('revcycleai.com/newsletter',
                     S('cta_link', fontName='Helvetica-Bold', fontSize=14,
                       textColor=WHITE, leading=18, alignment=TA_CENTER))
        ]], colWidths=[3.5*inch],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), TEAL),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ROUNDEDCORNERS', [6]),
        ]))],
        [Spacer(1, 0.3*inch)],
        [Paragraph(
            f'RevCycleAI · {week_label}',
            S('cta_footer', fontName='Helvetica', fontSize=9,
              textColor=colors.HexColor('#64748B'), leading=14, alignment=TA_CENTER)
        )],
    ]

    t = Table(content, colWidths=[SLIDE_W - inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0.5*inch),
        ('RIGHTPADDING', (0,0), (-1,-1), 0.5*inch),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    return t


if __name__ == "__main__":
    print("Generating weekly carousel...")
    path = build_weekly_carousel()
    print(f"Done: {path}")
