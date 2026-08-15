from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

def generate_teacher_pdf(teacher_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#0d2137'),
        spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#00b0ff'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#222222'),
        spaceAfter=4
    )

    # Title & Header
    story.append(Paragraph("<b>Ideal International School</b>", title_style))
    story.append(Paragraph(f"Teacher Performance & Evaluation Report — <b>{teacher_data.get('name', 'N/A')}</b>", h2_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#00b0ff'), spaceAfter=15))

    # Basic Info Table
    info_data = [
        [Paragraph("<b>Date of Birth:</b>", body_style), Paragraph(str(teacher_data.get('dob', '')), body_style),
         Paragraph("<b>Section:</b>", body_style), Paragraph(str(teacher_data.get('section', '')), body_style)],
        [Paragraph("<b>Qualifications:</b>", body_style), Paragraph(str(teacher_data.get('qualifications', '')), body_style),
         Paragraph("<b>Classes per Week:</b>", body_style), Paragraph(str(teacher_data.get('classes_per_week', '')), body_style)],
        [Paragraph("<b>Experience (School):</b>", body_style), Paragraph(f"{teacher_data.get('experience_school', 0)} years", body_style),
         Paragraph("<b>Subjects & Classes:</b>", body_style), Paragraph(str(teacher_data.get('subjects', '')), body_style)],
    ]
    t_info = Table(info_data, colWidths=[120, 140, 120, 140])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f4f8')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))

    # Key Performance Metrics
    story.append(Paragraph("Performance Benchmark Scores", h2_style))
    scores_data = [
        ["Benchmark Metric", "Score / Value", "Rating / Status"],
        ["Teaching Delivery Score (Int. BM)", f"{teacher_data.get('int_bm_score', 0)} / 100", "Satisfactory / Good"],
        ["Teaching Delivery Score (Ext. BM)", f"{teacher_data.get('ext_bm_score', 0)} / 100", "Effective"],
        ["Compliance Score", f"{teacher_data.get('compliance_score', 0)} / 10.0", "Compliant"],
        ["Training Hours Completed", f"{teacher_data.get('training_hours', 0)} / 50 hrs", "In Progress"],
        ["Co-curricular Activities", f"{teacher_data.get('co_curricular_count', 0)} / 12", str(teacher_data.get('co_curricular_quality', 'Good'))],
        ["Attrition Risk Score", f"{teacher_data.get('attrition_score', 0.0)}", str(teacher_data.get('attrition_type', 'No Risk'))]
    ]
    t_scores = Table(scores_data, colWidths=[200, 140, 180])
    t_scores.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d2137')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_scores)
    story.append(Spacer(1, 15))

    # Expectations & Notes
    story.append(Paragraph("Expectations from HOD / Principal", h2_style))
    for exp in teacher_data.get('expectations', []):
        story.append(Paragraph(f"• {exp}", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("School Support Parameters", h2_style))
    for sup in teacher_data.get('support_params', []):
        story.append(Paragraph(f"• {sup}", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
