# pdf_generator.py
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_bulletin_pdf(student_data, grades_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom Styles
    style_title = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=18, leading=22, textColor=colors.HexColor('#1E293B'))
    style_subtitle = ParagraphStyle('SubTitleStyle', parent=styles['Heading2'], alignment=TA_CENTER, fontSize=12, leading=15, textColor=colors.HexColor('#475569'))
    style_header_info = ParagraphStyle('HeaderInfo', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#0F172A'))
    style_cell = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=9, leading=11, alignment=TA_CENTER)
    style_cell_left = ParagraphStyle('CellLeft', parent=styles['Normal'], fontSize=9, leading=11, alignment=TA_LEFT)
    style_cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontSize=9, leading=11, alignment=TA_CENTER, fontName='Helvetica-Bold')

    # Header
    story.append(Paragraph("<b>RÉPUBLIQUE DÉMOCRATIQUE DU CONGOLAISE</b>", style_title))
    story.append(Paragraph("MINISTÈRE DE L'ÉDUCATION NATIONALE ET NOUVELLE CITOYENNETÉ", style_subtitle))
    story.append(Paragraph("<b>BULLETIN SCOLAIRE OFFICIEL</b>", ParagraphStyle('Sub', parent=style_title, fontSize=14, textColor=colors.HexColor('#4F46E5'))))
    story.append(Spacer(1, 15))

    # Student Info Table
    info_data = [
        [
            Paragraph(f"<b>Élève:</b> {student_data['full_name']}", style_header_info),
            Paragraph(f"<b>Code Élève:</b> {student_data['student_code']}", style_header_info)
        ],
        [
            Paragraph(f"<b>Classe:</b> {student_data['classroom']}", style_header_info),
            Paragraph(f"<b>Année Scolaire:</b> {student_data['school_year']}", style_header_info)
        ]
    ]
    info_table = Table(info_data, colWidths=[270, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))

    # Grades Table Header
    headers = ["Matière", "P1\n/10", "P2\n/10", "Exam1\n/20", "Tot Sem1\n/40", "P3\n/10", "P4\n/10", "Exam2\n/20", "Tot Sem2\n/40", "Total An\n/80"]
    table_data = [[Paragraph(f"<b>{h}</b>", style_cell_bold) for h in headers]]

    total_max_an = 0
    total_obtained_an = 0

    for g in grades_data:
        tot_s1 = g['p1'] + g['p2'] + g['exam1']
        tot_s2 = g['p3'] + g['p4'] + g['exam2']
        tot_an = tot_s1 + tot_s2

        total_obtained_an += tot_an
        total_max_an += 80

        row = [
            Paragraph(f"<b>{g['subject_name']}</b>", style_cell_left),
            Paragraph(f"{g['p1']:.1f}", style_cell),
            Paragraph(f"{g['p2']:.1f}", style_cell),
            Paragraph(f"{g['exam1']:.1f}", style_cell),
            Paragraph(f"<b>{tot_s1:.1f}</b>", style_cell_bold),
            Paragraph(f"{g['p3']:.1f}", style_cell),
            Paragraph(f"{g['p4']:.1f}", style_cell),
            Paragraph(f"{g['exam2']:.1f}", style_cell),
            Paragraph(f"<b>{tot_s2:.1f}</b>", style_cell_bold),
            Paragraph(f"<b>{tot_an:.1f}</b>", style_cell_bold),
        ]
        table_data.append(row)

    percentage = (total_obtained_an / total_max_an * 100) if total_max_an > 0 else 0

    # Total Row
    tot_row = [
        Paragraph("<b>TOTAL GÉNÉRAL</b>", style_cell_left),
        Paragraph("-", style_cell), Paragraph("-", style_cell), Paragraph("-", style_cell), Paragraph("-", style_cell),
        Paragraph("-", style_cell), Paragraph("-", style_cell), Paragraph("-", style_cell), Paragraph("-", style_cell),
        Paragraph(f"<b>{total_obtained_an:.1f} / {total_max_an}</b>", style_cell_bold)
    ]
    table_data.append(tot_row)

    perc_row = [
        Paragraph("<b>POURCENTAGE & MENTION</b>", style_cell_left),
        Paragraph("", style_cell), Paragraph("", style_cell), Paragraph("", style_cell), Paragraph("", style_cell),
        Paragraph("", style_cell), Paragraph("", style_cell), Paragraph("", style_cell), Paragraph("", style_cell),
        Paragraph(f"<b>{percentage:.2f}%</b>", style_cell_bold)
    ]
    table_data.append(perc_row)

    grades_table = Table(table_data, colWidths=[120, 40, 40, 45, 55, 40, 40, 45, 55, 50])
    grades_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,-2), (-1,-1), colors.HexColor('#EEF2FF')),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#4F46E5')),
        ('SPAN', (0, -1), (8, -1)), # Span for percentage
        ('SPAN', (0, -2), (8, -2)), # Span for totals
    ]))

    story.append(grades_table)
    story.append(Spacer(1, 25))

    # Signatures
    sig_data = [
        [
            Paragraph("<b>L'Enseignant Titulaire</b>", style_cell_bold),
            Paragraph("<b>Le Parent / Tuteur</b>", style_cell_bold),
            Paragraph("<b>Le Chef d'Établissement</b>", style_cell_bold)
        ],
        [
            Paragraph("<br/><br/>Sceau & Signature", style_cell),
            Paragraph("<br/><br/>Signature", style_cell),
            Paragraph("<br/><br/>Sceau & Signature", style_cell)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[175, 175, 180])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(sig_table)

    doc.build(story)
    buffer.seek(0)
    return buffer
