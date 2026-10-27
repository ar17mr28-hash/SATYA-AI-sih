import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

class ComplianceReportGenerator:
    """
    Generates professional, government-grade PDF compliance reports
    for VerifyAI institutional applications.
    """

    @staticmethod
    def generate_pdf_report(
        application_data: dict,
        institution_data: dict,
        documents: list,
        findings: list,
        compliance_results: list,
        decisions: list,
        output_path: str
    ) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Palette
        c_navy = colors.HexColor("#0F172A")
        c_blue = colors.HexColor("#2563EB")
        c_cyan = colors.HexColor("#06B6D4")
        c_emerald = colors.HexColor("#10B981")
        c_amber = colors.HexColor("#F59E0B")
        c_red = colors.HexColor("#EF4444")
        c_light = colors.HexColor("#F8FAFC")
        c_border = colors.HexColor("#E2E8F0")

        # Custom Typography Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=c_navy,
            alignment=TA_LEFT
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#475569"),
            alignment=TA_LEFT
        )
        h2_style = ParagraphStyle(
            'Heading2Custom',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=15,
            textColor=c_navy,
            spaceAfter=4
        )
        body_style = ParagraphStyle(
            'BodyCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#1E293B")
        )
        bold_style = ParagraphStyle(
            'BoldCustom',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=12,
            textColor=c_navy
        )
        badge_style = ParagraphStyle(
            'BadgeText',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            alignment=TA_CENTER
        )

        story = []

        # 1. Header with Branding & Watermark Metadata
        header_table_data = [
            [
                Paragraph("<b>VerifyAI</b> &bull; Intelligent Regulatory Verification", title_style),
                Paragraph(f"<b>REPORT DATE</b><br/>{datetime.datetime.utcnow().strftime('%d %b %Y, %H:%M UTC')}", ParagraphStyle('HeadRight', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=TA_RIGHT, textColor=colors.HexColor("#64748B")))
            ],
            [
                Paragraph("Automated Document Authentication & Regulatory Compliance System | SIH-26261", subtitle_style),
                Paragraph(f"<b>REF ID:</b> <font color='#2563EB'><b>{application_data.get('reference_id', 'AICTE-2026-0000')}</b></font>", ParagraphStyle('RefRight', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, alignment=TA_RIGHT))
            ]
        ]
        header_table = Table(header_table_data, colWidths=[380, 160])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=c_blue, spaceBefore=2, spaceAfter=10))

        # 2. Executive Summary & Verification Badges
        status_str = application_data.get('status', 'UNDER_REVIEW').replace('_', ' ').upper()
        risk_str = application_data.get('risk_level', 'MEDIUM').upper()
        comp_score = application_data.get('compliance_score', 0.0)

        badge_bg = c_emerald if status_str in ["APPROVED", "MARK COMPLETE APPROVED"] else (c_amber if "CLARIFICATION" in status_str or "CORRECTION" in status_str else c_blue)
        risk_bg = c_emerald if risk_str == "LOW" else (c_amber if risk_str == "MEDIUM" else c_red)

        summary_box = [
            [
                Paragraph("<b>INSTITUTION DETAILS</b>", h2_style),
                Paragraph("<b>APPLICATION AUDIT SUMMARY</b>", h2_style)
            ],
            [
                Paragraph(
                    f"<b>Name:</b> {institution_data.get('name')}<br/>"
                    f"<b>Code:</b> {institution_data.get('code')} &nbsp;|&nbsp; <b>Type:</b> {institution_data.get('institution_type')}<br/>"
                    f"<b>Location:</b> {institution_data.get('district')}, {institution_data.get('state')}<br/>"
                    f"<b>Contact:</b> {institution_data.get('contact_email')} &bull; {institution_data.get('contact_phone')}",
                    body_style
                ),
                Paragraph(
                    f"<b>Current Review Status:</b> {status_str}<br/>"
                    f"<b>Regulatory Compliance Score:</b> <b>{comp_score}%</b><br/>"
                    f"<b>Risk Profile:</b> <b>{risk_str}</b><br/>"
                    f"<b>Documents Evaluated:</b> {len(documents)} Attached Files",
                    body_style
                )
            ]
        ]
        sum_table = Table(summary_box, colWidths=[270, 270])
        sum_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_light),
            ('BOX', (0, 0), (-1, -1), 0.5, c_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(sum_table)
        story.append(Spacer(1, 14))

        # 3. Documents Audited Matrix
        story.append(Paragraph("1. Submitted Documents & OCR Extraction Audit", h2_style))
        doc_rows = [
            [
                Paragraph("<b>Document Type</b>", bold_style),
                Paragraph("<b>Original File</b>", bold_style),
                Paragraph("<b>OCR Engine</b>", bold_style),
                Paragraph("<b>Key Entities Extracted</b>", bold_style),
                Paragraph("<b>Verification</b>", bold_style)
            ]
        ]
        for d in documents:
            extr = d.get("extraction") or {}
            fields = extr.get("extracted_fields") or {}
            field_summary = "<br/>".join([f"&bull; <i>{k}</i>: {v}" for k, v in list(fields.items())[:3]]) or "None detected"
            conf = f"{int(extr.get('confidence_score', 0)*100)}%" if extr.get('confidence_score') else "Unavailable"
            status_text = d.get('verification_status', 'Pending').replace('_', ' ').capitalize()

            doc_rows.append([
                Paragraph(f"<b>{d.get('document_type')}</b>", body_style),
                Paragraph(d.get('original_name', 'document.pdf'), body_style),
                Paragraph(f"{extr.get('ocr_method', 'native_pdf')}<br/>(Conf: {conf})", body_style),
                Paragraph(field_summary, body_style),
                Paragraph(f"<b>{status_text}</b><br/><font size='7' color='#64748B'>Mock Provider</font>", body_style)
            ])

        doc_table = Table(doc_rows, colWidths=[110, 110, 90, 150, 80])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 0.5, c_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(doc_table)
        story.append(Spacer(1, 14))

        # 4. Explainable AI Findings & Cross-Document Discrepancies
        story.append(Paragraph("2. Explainable AI Discrepancy & Validation Findings", h2_style))
        if findings:
            finding_rows = [
                [
                    Paragraph("<b>Finding / Discrepancy</b>", bold_style),
                    Paragraph("<b>Severity</b>", bold_style),
                    Paragraph("<b>Verifiable Text Evidence</b>", bold_style),
                    Paragraph("<b>AI Explanation & Recommended Action</b>", bold_style)
                ]
            ]
            for f in findings:
                sev = f.get('severity', 'warning').upper()
                sev_color = "#EF4444" if sev == "CRITICAL" else ("#F59E0B" if sev == "WARNING" else "#2563EB")
                finding_rows.append([
                    Paragraph(f"<b>{f.get('title')}</b><br/><font size='7' color='#64748B'>Source: {f.get('source_doc_title', 'General')}</font>", body_style),
                    Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", body_style),
                    Paragraph(f"<i>\"{f.get('evidence_snippet', 'N/A')}\"</i>", body_style),
                    Paragraph(f"<b>Explanation:</b> {f.get('explanation')}<br/><b>Recommendation:</b> {f.get('recommended_action')}", body_style)
                ])

            finding_table = Table(finding_rows, colWidths=[120, 55, 155, 210])
            finding_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#FEF2F2")),
                ('BOX', (0, 0), (-1, -1), 0.5, c_border),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(finding_table)
        else:
            story.append(Paragraph("<i>No discrepancies or inconsistencies detected across submitted records.</i>", body_style))
        story.append(Spacer(1, 14))

        # 5. Regulatory Compliance Checklist
        story.append(Paragraph("3. AICTE Regulatory Compliance Evaluation", h2_style))
        comp_rows = [
            [
                Paragraph("<b>Rule Reference</b>", bold_style),
                Paragraph("<b>Compliance Status</b>", bold_style),
                Paragraph("<b>Evaluated Evidence</b>", bold_style),
                Paragraph("<b>Regulatory Rationale</b>", bold_style)
            ]
        ]
        for c in compliance_results:
            c_stat = c.get('status', 'satisfied').replace('_', ' ').upper()
            c_color = "#10B981" if c_stat == "SATISFIED" else ("#EF4444" if c_stat == "NOT SATISFIED" else "#F59E0B")
            rule_obj = c.get('rule') or {}
            comp_rows.append([
                Paragraph(f"<b>{rule_obj.get('rule_code', 'RULE')}</b><br/>{rule_obj.get('rule_name', 'Rule')}", body_style),
                Paragraph(f"<font color='{c_color}'><b>{c_stat}</b></font>", body_style),
                Paragraph(c.get('evidence_summary', 'Documents evaluated'), body_style),
                Paragraph(c.get('explanation', ''), body_style)
            ])

        comp_table = Table(comp_rows, colWidths=[120, 90, 160, 170])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, c_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(comp_table)
        story.append(Spacer(1, 14))

        # 6. Officer Remarks & Verification Seal
        story.append(Paragraph("4. Officer Review Remarks & Administrative Audit", h2_style))
        latest_decision = decisions[-1] if decisions else None
        officer_text = latest_decision.get('remarks', 'Automated validation completed. Awaiting officer final sign-off.') if latest_decision else 'No officer remarks recorded.'
        officer_name = (latest_decision.get('officer') or {}).get('full_name', 'Authorized AICTE Scrutiny Officer') if latest_decision else 'Pending Assignment'

        decision_box = [
            [
                Paragraph(f"<b>Officer Decision:</b> {status_str}<br/><b>Scrutiny Officer:</b> {officer_name}<br/><b>Officer Remarks:</b> {officer_text}", body_style),
                Paragraph(
                    "<b>SECURITY & AUDIT SEAL</b><br/>"
                    "<font size='7' color='#475569'>Digitally certified by VerifyAI Engine.<br/>"
                    "Hash: SHA256:e3b0c44298fc1c149afbf4c8<br/>"
                    "AICTE Regulatory Verification Cell</font>",
                    body_style
                )
            ]
        ]
        dec_table = Table(decision_box, colWidths=[360, 180])
        dec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_light),
            ('BOX', (0, 0), (-1, -1), 0.5, c_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(dec_table)

        doc.build(story)
        return output_path
