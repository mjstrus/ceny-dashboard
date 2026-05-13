"""
pdf_reporter.py — Generuj PDF raport z statystyką i wykresami
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend dla streamlit
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
import os

# Kolory Abacus
NAVY = '#1B2A4A'
GOLD = '#E8A000'


def create_summary_report(summary: dict, df: pd.DataFrame, filename: str = None) -> bytes:
    """
    Generuj PDF raport z statystyką i wykresami.
    
    Args:
        summary: Dict z metrykami z summary_generator.py
        df: DataFrame z danymi klientów (musi mieć kolumny: Status, Wzrost_%_Od_Faktycznej)
        filename: Opcjonalna ścieżka do pliku (jeśli None, zwróć bytes)
    
    Returns:
        Bytes PDF lub None (jeśli zapisano do pliku)
    """
    
    # Stwórz PDF
    buffer = BytesIO() if filename is None else filename
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Style
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor(NAVY),
        spaceAfter=6,
        alignment=1  # Center
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor(NAVY),
        spaceAfter=12,
        spaceBefore=12
    )
    
    story = []
    
    # TITLE
    story.append(Paragraph("📊 RAPORT STATYSTYKI LISTY KLIENTÓW", title_style))
    story.append(Paragraph(f"Abacus Centrum | {datetime.now().strftime('%d.%m.%Y')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # METRYKI GŁÓWNE
    story.append(Paragraph("📈 Metryki Główne", heading_style))
    
    metrics_data = [
        ['Liczba klientów', f"{summary.get('Liczba_Klientów_Razem', 0)}"],
        ['  - Standard', f"{summary.get('Liczba_Klientów_Standard', 0)}"],
        ['  - VIP', f"{summary.get('Liczba_Klientów_VIP', 0)}"],
        ['  - FREE', f"{summary.get('Liczba_Klientów_FREE', 0)}"],
        ['', ''],
        ['Przychód PRZED (mc)', f"{summary.get('Przychod_Przed_PLN', 0):,.0f} PLN"],
        ['Przychód PO (mc)', f"{summary.get('Przychod_Po_PLN', 0):,.0f} PLN"],
        ['Wzrost (mc)', f"+{summary.get('Wzrost_PLN', 0):,.0f} PLN ({summary.get('Wzrost_PCT', 0):.1f}%)"],
        ['', ''],
        ['Roczny impact', f"+{summary.get('Roczny_Wzrost_PLN', 0):,.0f} PLN"],
        ['Średnia docs/klienta', f"{summary.get('Srednia_Doc_Klienta', 0):.1f}"],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor(NAVY)),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 0.2*inch))
    
    # WYKRESY
    story.append(PageBreak())
    story.append(Paragraph("📊 Wizualizacja", heading_style))
    
    # Wykres 1: Segmentacja (Pie)
    fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
    segments = [summary.get('Zielony_Cnt', 0), summary.get('Zolty_Cnt', 0), summary.get('Czerwony_Cnt', 0)]
    labels = ['🟢 Zielony', '🟡 Żółty', '🔴 Czerwony']
    colors_pie = ['#22c55e', '#eab308', '#ef4444']
    
    if sum(segments) > 0:
        ax.pie(segments, labels=labels, autopct='%1.1f%%', colors=colors_pie, startangle=90)
        ax.set_title('Segmentacja Klientów', fontsize=12, fontweight='bold', color=NAVY)
    
    img_seg = BytesIO()
    fig.savefig(img_seg, format='png', bbox_inches='tight', dpi=100)
    img_seg.seek(0)
    plt.close()
    story.append(Image(img_seg, width=3*inch, height=2*inch))
    story.append(Spacer(1, 0.2*inch))
    
    # Wykres 2: Przychód
    fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
    months = ['PRZED', 'PO']
    values = [summary.get('Przychod_Przed_PLN', 0), summary.get('Przychod_Po_PLN', 0)]
    bars = ax.bar(months, values, color=[colors.HexColor(NAVY), colors.HexColor(GOLD)])
    ax.set_ylabel('PLN', fontweight='bold')
    ax.set_title('Przychód Miesięczny', fontsize=12, fontweight='bold', color=NAVY)
    
    # Dodaj wartości na słupkach
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.0f}',
                ha='center', va='bottom', fontweight='bold')
    
    img_rev = BytesIO()
    fig.savefig(img_rev, format='png', bbox_inches='tight', dpi=100)
    img_rev.seek(0)
    plt.close()
    story.append(Image(img_rev, width=3*inch, height=2*inch))
    story.append(Spacer(1, 0.3*inch))
    
    # SEGMENTACJA SZCZEGÓŁOWA
    story.append(Paragraph("📋 Segmentacja Szczegółowa", heading_style))
    
    seg_data = [
        ['Status', 'Liczba', 'Opis'],
        ['🟢 Zielony', str(summary.get('Zielony_Cnt', 0)), 'Wzrost ≤10% (OK)'],
        ['🟡 Żółty', str(summary.get('Zolty_Cnt', 0)), 'Wzrost 10-20% lub >20% z rabatem'],
        ['🔴 Czerwony', str(summary.get('Czerwony_Cnt', 0)), 'Wzrost >20% bez rabatu (RYZYKO)'],
    ]
    
    seg_table = Table(seg_data, colWidths=[1.2*inch, 1*inch, 3*inch])
    seg_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(NAVY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(seg_table)
    story.append(Spacer(1, 0.3*inch))
    
    # STOPKA
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("___________________________________________________________", styles['Normal']))
    story.append(Paragraph(f"<i>Raport wygenerowany: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</i>", styles['Normal']))
    
    # BUILD PDF
    doc.build(story)
    
    if filename is None:
        buffer.seek(0)
        return buffer.getvalue()
    
    return None
