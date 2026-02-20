#!/usr/bin/env python3
"""
Build: UHC/Optum Prior Authorization Guide — Substance Use Disorder Treatment
For Axlow knowledge base
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime

# ── Colors ──────────────────────────────────────────────────────────────────
NAVY       = colors.HexColor('#0D1F37')
TEAL       = colors.HexColor('#1A6B5E')
BLUE       = colors.HexColor('#1D4ED8')
AMBER      = colors.HexColor('#D97706')
RED        = colors.HexColor('#DC2626')
GREEN      = colors.HexColor('#16A34A')
LIGHT_GRAY = colors.HexColor('#F4F4F5')
MID_GRAY   = colors.HexColor('#E4E4E7')
DARK_GRAY  = colors.HexColor('#52525B')
BLACK      = colors.HexColor('#09090B')

OUTPUT = '/Users/shackleton/.openclaw/workspace/axlow/UHC_Optum_SUD_Prior_Auth_Guide.pdf'

def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        leftMargin=0.85*inch,
        rightMargin=0.85*inch,
        topMargin=0.85*inch,
        bottomMargin=0.85*inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    h1 = S('H1', fontSize=22, leading=28, textColor=NAVY, fontName='Helvetica-Bold', spaceAfter=4)
    h2 = S('H2', fontSize=14, leading=18, textColor=NAVY, fontName='Helvetica-Bold', spaceBefore=16, spaceAfter=6)
    h3 = S('H3', fontSize=11, leading=15, textColor=TEAL, fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4)
    body = S('Body', fontSize=9.5, leading=14, textColor=BLACK, fontName='Helvetica', spaceAfter=4)
    body_sm = S('BodySm', fontSize=8.5, leading=13, textColor=DARK_GRAY, fontName='Helvetica', spaceAfter=3)
    label = S('Label', fontSize=8, leading=11, textColor=DARK_GRAY, fontName='Helvetica-Bold', spaceAfter=2, textTransform='uppercase')
    callout = S('Callout', fontSize=9, leading=13, textColor=NAVY, fontName='Helvetica', spaceAfter=4,
                borderColor=BLUE, borderWidth=1, borderPadding=(8,10,8,10), backColor=colors.HexColor('#EFF6FF'))
    warn = S('Warn', fontSize=9, leading=13, textColor=colors.HexColor('#92400E'), fontName='Helvetica',
             spaceAfter=4, backColor=colors.HexColor('#FFFBEB'), borderColor=AMBER, borderWidth=1,
             borderPadding=(8,10,8,10))
    sub = S('Sub', fontSize=8, leading=12, textColor=DARK_GRAY, fontName='Helvetica-Oblique', spaceAfter=12)

    story = []

    # ── HEADER ───────────────────────────────────────────────────────────────
    story.append(Paragraph("UnitedHealthcare / Optum", label))
    story.append(Paragraph("Prior Authorization Guide", h1))
    story.append(Paragraph("Substance Use Disorder &amp; Opioid Treatment Programs", 
        S('Sub2', fontSize=15, leading=20, textColor=TEAL, fontName='Helvetica-Bold', spaceAfter=4)))
    story.append(Paragraph(
        f"Prepared for Axlow Knowledge Base &nbsp;·&nbsp; Updated {datetime.now().strftime('%B %Y')} &nbsp;·&nbsp; Based on Optum published clinical guidelines &amp; UHC provider policy",
        sub))
    story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=14))

    story.append(Paragraph(
        "⚠️  Always verify current requirements at <b>providerexpress.com</b> before submitting. Policies update quarterly. This guide reflects standard commercial plan requirements — Medicare Advantage, Medicaid, and self-insured employer plans may differ.",
        warn))

    # ── SECTION 1: ADMINISTRATIVE ────────────────────────────────────────────
    story.append(Paragraph("1. Administrative Overview", h2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=8))

    admin_data = [
        ['Item', 'Detail'],
        ['Behavioral Health Administrator', 'Optum (formerly United Behavioral Health / UBH)'],
        ['Provider Portal', 'providerexpress.com'],
        ['PA Phone Line', '1-888-778-1478 (Optum Behavioral Health)'],
        ['Urgent/Concurrent Auth Phone', '1-888-778-1478 — state "urgent" at prompt'],
        ['PA Submission Method', 'Online (preferred) via providerexpress.com, or phone'],
        ['Timely Filing — Commercial', '180 days from date of service'],
        ['Timely Filing — Medicare Advantage', '365 days from date of service'],
        ['Retroactive Auth Window', '24–72 hours for emergencies; not guaranteed'],
        ['Clinical Criteria Standard', 'ASAM Criteria (American Society of Addiction Medicine)'],
        ['Diagnosis Coding Standard', 'DSM-5 / ICD-10-CM (F10–F19 range for SUD)'],
    ]

    t = Table(admin_data, colWidths=[2.2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0,0), (-1,-1), 0.4, MID_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # ── SECTION 2: WHAT REQUIRES PA ─────────────────────────────────────────
    story.append(Paragraph("2. Services Requiring Prior Authorization", h2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=8))

    story.append(Paragraph("2.1  Outpatient SUD Services", h3))
    out_data = [
        ['HCPCS/CPT', 'Service Description', 'PA Required?', 'Notes'],
        ['H0001', 'Alcohol/Drug Assessment', 'No', 'First assessment; ongoing may vary'],
        ['H0004', 'Individual Counseling', 'No (first 30 visits)', 'PA required beyond 30 on most plans'],
        ['H0005', 'Group Counseling', 'No (first 30 visits)', 'PA required beyond 30'],
        ['H0014', 'Ambulatory Detoxification', 'YES', 'Requires ASAM Level 1 justification'],
        ['H0015', 'IOP — Intensive Outpatient', 'YES', 'PA required at admission + concurrent review'],
        ['H0020', 'Alcohol/Drug Non-OTP Treatment', 'YES', 'See OTP section for OTP-specific billing'],
        ['H0035', 'Partial Hospitalization (PHP)', 'YES', 'PA required; concurrent review every 7 days'],
        ['T1006', 'Habilitation, Per Diem', 'YES', 'Residential; ASAM 3.1–3.7 documentation required'],
    ]
    t2 = Table(out_data, colWidths=[1.0*inch, 2.4*inch, 1.1*inch, 2.2*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0,0), (-1,-1), 0.4, MID_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        # Color-code PA required cells
        ('TEXTCOLOR', (2,2), (2,2), GREEN),
        ('TEXTCOLOR', (2,3), (2,3), GREEN),
        ('TEXTCOLOR', (2,4), (2,4), RED),
        ('TEXTCOLOR', (2,5), (2,5), RED),
        ('TEXTCOLOR', (2,6), (2,6), RED),
        ('TEXTCOLOR', (2,7), (2,7), RED),
        ('TEXTCOLOR', (2,8), (2,8), RED),
        ('FONTNAME', (2,4), (2,8), 'Helvetica-Bold'),
    ]))
    story.append(t2)
    story.append(Spacer(1, 10))

    story.append(Paragraph("2.2  Residential &amp; Inpatient SUD Services", h3))
    res_data = [
        ['HCPCS/CPT', 'Service Description', 'PA Required?', 'ASAM Level'],
        ['H0016', 'Medically Managed Detox (Residential)', 'YES', '3.7 — High-intensity medically managed'],
        ['H0018', 'Residential SUD Treatment', 'YES', '3.1 / 3.3 / 3.5 — Clinically managed'],
        ['H0019', 'Therapeutic Living / Long-Term Residential', 'YES', '3.1 / 3.3'],
        ['S9475', 'Ambulatory Detox (Home)', 'YES', '1.0 — Outpatient'],
        ['99281–99285', 'ED Evaluation (SUD crisis)', 'No (Emergent)', 'Notify within 24 hrs of admission'],
    ]
    t3 = Table(res_data, colWidths=[1.2*inch, 2.5*inch, 1.1*inch, 1.95*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0,0), (-1,-1), 0.4, MID_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TEXTCOLOR', (2,1), (2,4), RED),
        ('FONTNAME', (2,1), (2,4), 'Helvetica-Bold'),
        ('TEXTCOLOR', (2,5), (2,5), GREEN),
    ]))
    story.append(t3)
    story.append(Spacer(1, 10))

    # ── SECTION 3: OTP / OPIOID TREATMENT ───────────────────────────────────
    story.append(Paragraph("3. Opioid Treatment Programs (OTP) — Methadone &amp; Buprenorphine", h2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=8))

    story.append(Paragraph(
        "OTPs are DEA-licensed, SAMHSA-certified facilities providing methadone, buprenorphine, or naltrexone for opioid use disorder (OUD). UHC follows the <b>CMS OTP bundled payment model</b> for billing (effective Jan 1, 2020). All new OTP admissions <b>require prior authorization</b>.",
        body))

    story.append(Paragraph("3.1  OTP HCPCS Billing Codes (CMS Bundle Model)", h3))
    otp_data = [
        ['HCPCS', 'Description', 'PA?', 'Frequency'],
        ['G2067', 'Weekly bundle — Methadone', 'YES (admission PA)', 'Weekly'],
        ['G2068', 'Weekly bundle — Buprenorphine', 'YES (admission PA)', 'Weekly'],
        ['G2069', 'Weekly bundle — Naltrexone (injectable)', 'YES (admission PA)', 'Weekly'],
        ['G2070', 'Additional drug counseling per week', 'Covered under G2067–69', 'Per session'],
        ['G2071', 'Unsupported days (non-treatment days)', 'No PA', 'Per day'],
        ['G2072', 'Weekly bundle — no medication', 'YES', 'Weekly (counseling only)'],
        ['G2073', 'Intake activities (admission)', 'YES', 'One-time at admission'],
        ['G2074', 'Periodic assessment', 'No PA', 'Per encounter'],
        ['G2075', 'Counseling — individual, 30 min', 'No PA (bundled)', 'Per session'],
        ['G2076', 'Toxicology/UDS testing', 'May require PA', 'Frequency limits apply'],
        ['G2078', 'Take-home dose (methadone)', 'YES — Phase 2+ only', 'Per dose dispensed'],
        ['G2079', 'Phase 2 (maintenance) weekly bundle', 'Reauth required', 'Weekly (after Phase 1)'],
        ['G2080', 'Additional 30 min counseling beyond weekly bundle', 'No PA (bundled)', 'Per 30 min'],
    ]
    t4 = Table(otp_data, colWidths=[0.8*inch, 2.7*inch, 1.5*inch, 1.7*inch])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0,0), (-1,-1), 0.4, MID_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t4)
    story.append(Spacer(1, 8))

    story.append(Paragraph("3.2  OTP PA Requirements — Step by Step", h3))
    story.append(Paragraph("<b>New Admission:</b>", body))
    steps = [
        "1. Submit PA request via providerexpress.com before or within 48 hours of admission",
        "2. Attach biopsychosocial assessment (within 30 days)",
        "3. Include DSM-5 diagnosis: <b>F11.10–F11.99</b> (Opioid Use Disorder, moderate–severe)",
        "4. Document ASAM Level 1-OTP recommendation",
        "5. Include treatment plan with: goals, objectives, discharge criteria, medication management plan",
        "6. Confirm prescriber has valid DEA registration (Schedule II for methadone; any DEA for buprenorphine)",
        "7. Standard review turnaround: <b>3 business days</b> (routine) | <b>Same day</b> (urgent)",
    ]
    for s in steps:
        story.append(Paragraph(s, body_sm))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Concurrent Review / Reauthorization:</b>", body))
    story.append(Paragraph("• Phase 1 (induction): reauth at <b>60 days</b>", body_sm))
    story.append(Paragraph("• Phase 2 (maintenance): reauth every <b>90 days</b>", body_sm))
    story.append(Paragraph("• Submit reauth 14 days before current auth expires to avoid gap", body_sm))
    story.append(Paragraph("• Continued stay criteria: documentation of treatment progress, compliance, UDS results", body_sm))
    story.append(Spacer(1, 8))

    # ── SECTION 4: MAT — OFFICE-BASED BUPRENORPHINE ─────────────────────────
    story.append(Paragraph("4. Medication-Assisted Treatment (MAT) — Office-Based Buprenorphine", h2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=8))

    story.append(Paragraph(
        "Office-based buprenorphine (Suboxone, Sublocade, Zubsolv, Bunavail) is typically managed under the <b>medical benefit</b> (not behavioral health) for UHC commercial plans. PA requirements differ by product and plan type.",
        body))

    mat_data = [
        ['Medication', 'Brand', 'NDC/HCPCS', 'PA Required?', 'Notes'],
        ['Buprenorphine/naloxone SL film', 'Suboxone', 'NDC-based', 'Often No (Tier 2)', 'Quantity limits apply; step therapy may require generic first'],
        ['Buprenorphine SL tablet', 'Subutex', 'NDC-based', 'Often No', 'Generic available; rarely used in practice today'],
        ['Buprenorphine ER injection', 'Sublocade (300mg/100mg)', 'J0571–J0575 / NDC', 'YES', 'PA required; site of care review; prescriber NPI required'],
        ['Buprenorphine implant', 'Probuphine', 'J0572', 'YES', 'Requires failure of SL buprenorphine documented'],
        ['Naltrexone injection', 'Vivitrol (380mg)', 'J2315', 'YES (some plans)', 'PA required on many commercial plans; opioid-free documentation required'],
        ['Naltrexone oral', 'Generic', 'NDC-based', 'Often No', 'Low cost; minimal barriers'],
    ]
    t5 = Table(mat_data, colWidths=[1.4*inch, 1.0*inch, 1.1*inch, 1.0*inch, 2.2*inch])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 7.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0,0), (-1,-1), 0.4, MID_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('WORDWRAP', (0,0), (-1,-1), True),
    ]))
    story.append(t5)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "⚠️  MHPAEA Compliance Note: The Mental Health Parity and Addiction Equity Act (MHPAEA) prohibits UHC from applying more restrictive PA requirements for SUD treatment than for comparable medical/surgical services. If you receive a denial based on criteria not applied to medical admissions, cite MHPAEA in your appeal.",
        warn))

    # ── SECTION 5: MEDICAL NECESSITY CRITERIA ───────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("5. Medical Necessity — ASAM Criteria Overview", h2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=8))

    story.append(Paragraph(
        "Optum uses the <b>ASAM (American Society of Addiction Medicine) Criteria, 3rd Edition</b> as the clinical framework for all SUD level-of-care decisions. Documentation must address all six dimensions:",
        body))

    asam_data = [
        ['Dimension', 'Description', 'What to Document'],
        ['1 — Acute Intoxication / Withdrawal', 'Current intoxication or withdrawal risk', 'CIWA-Ar score, COWS score, last use date/amount, withdrawal symptom severity'],
        ['2 — Biomedical Conditions', 'Physical health issues that complicate treatment', 'Medical comorbidities, pregnancy, IV drug use complications, hepatitis, HIV'],
        ['3 — Emotional / Behavioral / Cognitive', 'Mental health or cognitive factors', 'Psychiatric diagnoses, suicidality, trauma history, cognitive barriers to treatment'],
        ['4 — Readiness to Change', 'Motivation and engagement level', 'Stage of change assessment, treatment history, ambivalence, compliance with recommendations'],
        ['5 — Relapse / Continued Use Risk', 'Risk of relapse without structured treatment', 'Relapse history, triggers, coping skills, craving severity'],
        ['6 — Recovery / Living Environment', 'Home and community support factors', 'Housing stability, family support/enabling, access to substances at home, recovery community'],
    ]
    t6 = Table(asam_data, colWidths=[1.5*inch, 2.0*inch, 3.2*inch])
    t6.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0,0), (-1,-1), 0.4, MID_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,1), (0,-1), NAVY),
    ]))
    story.append(t6)
    story.append(Spacer(1, 10))

    # ── SECTION 6: ICD-10 CODES ──────────────────────────────────────────────
    story.append(Paragraph("6. ICD-10-CM Diagnosis Codes — Opioid Use Disorder", h2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=8))

    icd_data = [
        ['ICD-10 Code', 'Description', 'Severity'],
        ['F11.10', 'Opioid use disorder, mild, uncomplicated', 'Mild (2–3 criteria)'],
        ['F11.11', 'Opioid use disorder, mild, in remission', 'Mild — remission'],
        ['F11.120', 'Opioid use disorder, mild, with intoxication, uncomplicated', 'Mild + acute'],
        ['F11.20', 'Opioid use disorder, moderate, uncomplicated', 'Moderate (4–5 criteria)'],
        ['F11.21', 'Opioid use disorder, moderate, in remission', 'Moderate — remission'],
        ['F11.220', 'Opioid use disorder, moderate, with intoxication, uncomplicated', 'Moderate + acute'],
        ['F11.23', 'Opioid use disorder, moderate, with withdrawal', 'Moderate + withdrawal'],
        ['F11.24', 'Opioid use disorder, moderate, with opioid-induced mood disorder', 'Moderate + comorbid'],
        ['F11.250', 'Opioid use disorder, moderate, with opioid-induced psychotic disorder', 'Moderate + psychosis'],
        ['F11.20', 'Opioid use disorder, severe, uncomplicated', 'Severe (6+ criteria)'],
        ['F11.21', 'Opioid use disorder, severe, in remission', 'Severe — remission'],
        ['F11.23', 'Opioid use disorder, severe, with withdrawal', 'Severe + withdrawal — most common for OTP admission'],
        ['F11.90', 'Opioid use, unspecified', '⚠️ Avoid — insufficient for PA; must specify severity'],
    ]
    t7 = Table(icd_data, colWidths=[1.0*inch, 3.5*inch, 2.2*inch])
    t7.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0,0), (-1,-1), 0.4, MID_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FEF2F2')),
        ('TEXTCOLOR', (0,-1), (-1,-1), RED),
    ]))
    story.append(t7)
    story.append(Spacer(1, 10))

    # ── SECTION 7: DENIALS & APPEALS ─────────────────────────────────────────
    story.append(Paragraph("7. Common Denial Reasons &amp; Appeal Strategies", h2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=8))

    denial_data = [
        ['Denial Reason', 'Appeal Strategy'],
        ['Not medically necessary — level of care', 'Submit all 6 ASAM dimensions with specific scores (CIWA-Ar, COWS). Cite ASAM Criteria 3rd Ed. directly. Request peer-to-peer review within 72 hours.'],
        ['Missing clinical documentation', 'Resubmit with full biopsychosocial assessment, treatment plan with discharge criteria, and progress notes. Call 1-888-778-1478 to identify exact missing items.'],
        ['Wrong HCPCS code for OTP', 'Verify you are using G2067–G2080 bundle codes, NOT H0020 for OTP services. Resubmit corrected claim with admission PA number.'],
        ['ICD-10 unspecified / F11.90', 'Amend to specify severity: mild (F11.10), moderate (F11.20), or severe (F11.20 with 7th character). Get corrected diagnosis from treating physician.'],
        ['Concurrent review denied — no progress', 'Submit current ASAM scores showing why discharge is premature. Document acute risk factors. Peer-to-peer within 24 hours for expedited cases.'],
        ['MAT — step therapy required', 'Cite MHPAEA. If step therapy imposes greater barriers than for comparable medical conditions, challenge on parity grounds. Document clinical reason generic buprenorphine is not appropriate.'],
        ['Take-home dose denied', 'Document patient is in Phase 2 (maintenance), has demonstrated compliance, negative UDS, and stable dose for 60+ days per SAMHSA take-home eligibility criteria.'],
        ['Retro-auth denied', 'Document clinical emergency (unable to obtain auth in advance). Submit ER records if applicable. EMTALA protections for ED.'],
    ]
    t8 = Table(denial_data, colWidths=[1.8*inch, 4.9*inch])
    t8.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7F1D1D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 7.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0,0), (-1,-1), 0.4, MID_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,1), (0,-1), colors.HexColor('#7F1D1D')),
    ]))
    story.append(t8)
    story.append(Spacer(1, 8))

    # ── SECTION 8: APPEAL TIMELINES ──────────────────────────────────────────
    story.append(Paragraph("8. Appeal Timelines &amp; Rights", h2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=8))

    appeal_data = [
        ['Appeal Type', 'Timeframe', 'When to Use'],
        ['Expedited / Urgent Appeal', 'Decision within 72 hours', 'Patient currently receiving treatment; denial would cause serious harm'],
        ['Standard Internal Appeal — Level 1', '30 days from denial', 'Initial appeal of PA denial; submit all clinical documentation'],
        ['Standard Internal Appeal — Level 2', '30 days from Level 1 denial', 'Second-level review; request physician reviewer different from initial'],
        ['Peer-to-Peer Review', 'Request within 72 hrs of denial', 'Clinical director or attending speaks directly with Optum medical reviewer'],
        ['External Independent Review', 'After exhausting internal appeals', 'Independent Review Organization (IRO); binding; patient right under ACA'],
        ['Grievance / Complaint', '60 days from denial', 'Administrative issues (delay, access, service complaints)'],
    ]
    t9 = Table(appeal_data, colWidths=[1.7*inch, 1.4*inch, 3.6*inch])
    t9.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0,0), (-1,-1), 0.4, MID_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t9)
    story.append(Spacer(1, 10))

    # ── SECTION 9: QUICK REFERENCE ───────────────────────────────────────────
    story.append(Paragraph("9. Quick Reference — Axlow Cheat Sheet", h2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=8))

    story.append(Paragraph(
        "📞  PA Submission: providerexpress.com &nbsp;|&nbsp; Phone: 1-888-778-1478\n\n"
        "✅  Always requires PA: IOP (H0015), PHP (H0035), Residential (H0018), All OTP admissions (G2073)\n\n"
        "❌  Common reasons Axlow should flag: using H0020 instead of G-codes for OTP · ICD-10 F11.90 unspecified · missing ASAM documentation · not requesting peer-to-peer before filing formal appeal\n\n"
        "⚖️  MHPAEA: UHC cannot apply stricter PA requirements to SUD than to comparable medical/surgical services. If denied on criteria not applied to medical admissions, cite parity in appeal.\n\n"
        "🔁  Reauth schedule: IOP every 30 days · PHP every 7 days · Residential every 30 days · OTP Phase 1 at 60 days · OTP Phase 2 every 90 days",
        callout))

    # ── FOOTER ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GRAY, spaceAfter=8))
    story.append(Paragraph(
        f"This document was compiled for the Axlow knowledge base from publicly available UHC/Optum clinical guidelines and CMS policy. "
        f"It is intended for informational and RCM training purposes only. Verify all prior authorization requirements at <b>providerexpress.com</b> "
        f"before submitting claims or authorizations. Policies are subject to change. Not legal or medical advice. "
        f"Document version: {datetime.now().strftime('%B %d, %Y')}.",
        S('Footer', fontSize=7.5, leading=11, textColor=DARK_GRAY, fontName='Helvetica-Oblique')
    ))

    doc.build(story)
    print(f"✅  PDF saved: {OUTPUT}")

if __name__ == '__main__':
    build()
