"""
pdf_reporter.py — Generuj PDF raport z statystyką i wykresami
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend dla streamlit
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
import os
from unidecode import unidecode

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
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=0.1*inch, leftMargin=0.1*inch,
                           topMargin=0.2*inch, bottomMargin=0.2*inch)
    
    # Style
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'Helvetica'
    styles['Heading1'].fontName = 'Helvetica-Bold'
    styles['Heading2'].fontName = 'Helvetica-Bold'
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor(NAVY),
        spaceAfter=6,
        alignment=1,  # Center
        fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor(NAVY),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    story = []
    
    # TITLE
    story.append(Paragraph("RAPORT STATYSTYKI LISTY KLIENTÓW", title_style))
    story.append(Paragraph(f"Abacus Centrum | {datetime.now().strftime('%d.%m.%Y')}", heading_style))
    story.append(Spacer(1, 0.3*inch))
    
    # METRYKI GŁÓWNE
    story.append(Paragraph("Metryki Glowne", heading_style))
    
    metrics_data = [
        ['Liczba klientow', f"{summary.get('Liczba_Klientów_Razem', 0)}"],
        ['  - Standard', f"{summary.get('Liczba_Klientów_Standard', 0)}"],
        ['  - VIP', f"{summary.get('Liczba_Klientów_VIP', 0)}"],
        ['  - FREE', f"{summary.get('Liczba_Klientów_FREE', 0)}"],
        ['', ''],
        ['Przychod PRZED (mc)', f"{summary.get('Przychod_Przed_PLN', 0):,.0f} PLN"],
        ['Przychod PO (mc)', f"{summary.get('Przychod_Po_PLN', 0):,.0f} PLN"],
        ['Wzrost (mc)', f"+{summary.get('Wzrost_PLN', 0):,.0f} PLN ({summary.get('Wzrost_PCT', 0):.1f}%)"],
        ['', ''],
        ['Roczny impact', f"+{summary.get('Roczny_Wzrost_PLN', 0):,.0f} PLN"],
        ['Srednia docs/klienta', f"{summary.get('Srednia_Doc_Klienta', 0):.1f}"],
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
    story.append(Paragraph("Wizualizacja", heading_style))
    
    # Wykres 1: Segmentacja (Pie)
    fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
    segments = [summary.get('Zielony_Cnt', 0), summary.get('Zolty_Cnt', 0), summary.get('Czerwony_Cnt', 0), summary.get('Czarny_Cnt', 0)]
    labels = ['Zielony', 'Zolty', 'Czerwony', 'Czarny']
    colors_pie = ['#22c55e', '#eab308', '#f97316', '#1f2937']
    
    if sum(segments) > 0:
        ax.pie(segments, labels=labels, autopct='%1.1f%%', colors=colors_pie, startangle=90)
        ax.set_title('Segmentacja klientow', fontsize=12, fontweight='bold', color=NAVY)
    
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
    bars = ax.bar(months, values, color=[NAVY, GOLD])
    ax.set_ylabel('PLN', fontweight='bold')
    ax.set_title('Przychod Miesieczny', fontsize=12, fontweight='bold', color=NAVY)
    
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
    story.append(Paragraph("Segmentacja szczegolowa", heading_style))
    
    seg_data = [
        ['Status', 'Liczba', 'Opis'],
        ['Zielony', str(summary.get('Zielony_Cnt', 0)), 'Wzrost <=10% (OK)'],
        ['Zolty', str(summary.get('Zolty_Cnt', 0)), 'Wzrost 10-20% lub >20% z rabatem'],
        ['Czerwony', str(summary.get('Czerwony_Cnt', 0)), 'Wzrost >20% bez rabatu (RYZYKO)'],
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
    
    # ============================================================================
    # LISTA FIRM
    # ============================================================================
    story.append(PageBreak())
    story.append(Paragraph("Lista firm - Edytuj tabele ponizej", heading_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Przygotuj tabelę klientów
    if len(df) > 0:
        # Mapowanie: CSV -> DF columns (w kolejności Marcina)
        col_mapping = {
            'Nazwa': 'Nazwa',
            'Typ': 'Typ_Umowy',
            'VAT': 'VAT',
            'Status': 'Status',
            'Widełki': 'Cena_Range',
            'Miał rabat 10%?': 'Miał_Rabat_10%',
            'Cena Stara': 'Cena_Stara',
            'Grupa klienta': 'Grupa_Klienta',
            'Cena Nowa': 'Cena_Docelowa',
            '% Rabatu': 'Procent_Rabatu',
            'Wzrost PLN': 'Wzrost_PLN',
            'Wzrost %': 'Wzrost_%_Od_Faktycznej',
        }
        
        # Weź tylko kolumny które istnieją w df (w prawidłowej kolejności)
        csv_headers = []
        df_cols = []
        for k, v in col_mapping.items():
            if v in df.columns:
                csv_headers.append(k)
                df_cols.append(v)
        
        # Podziel długie nazwy na wiersze (multiline headers)
        multiline_headers = [
            'Nazwa',
            'Typ',
            'VAT',
            'Status',
            'Widełki',
            'Miał\nrabat\n10%?',
            'Cena\nStara',
            'Grupa\nklienta',
            'Cena\nNowa',
            'Wzrost\nPLN',
            'Wzrost\n%'
        ]
        multiline_headers = multiline_headers[:len(csv_headers)]
        
        # Nagłówki (wieloliniowe)
        clients_data = [[unidecode(h) for h in multiline_headers]]
        
        # Dane
        for idx, row in df.iterrows():
            row_data = []
            for df_col in df_cols:
                val = row[df_col]
                
                # Specjalnie dla VAT
                if df_col == 'VAT':
                    if val == True or val == 1 or str(val).lower() in ['true', 'tak', '1']:
                        row_data.append('tak')
                    else:
                        row_data.append('nie')
                elif isinstance(val, float):
                    if 'Wzrost_%' in df_col:
                        row_data.append(f"{val:.1f}%")
                    elif 'PLN' in df_col or 'Cena' in df_col or 'Rabat' in df_col:
                        row_data.append(f"{val:.0f}")
                    else:
                        row_data.append(f"{val:.1f}")
                elif isinstance(val, int):
                    row_data.append(str(int(val)))
                else:
                    text = str(val).replace('🟢', '').replace('🟡', '').replace('🔴', '').replace('⚫', '')
                    row_data.append(unidecode(text.strip()))
            clients_data.append(row_data)
        
        # Oblicz szerokości kolumn - DUŻE (wieloliniowe nagłówki)
        # Custom widths dla każdej kolumny - BARDZO KOMPAKTOWE
        col_width_map = {
            'Nazwa': 1.4,                    # Zmniejszone (było 2.0")
            'Typ': 0.4,                      # (było 0.5")
            'VAT': 0.3,                      # (było 0.4")
            'Status': 0.5,                   # (było 0.6")
            'Widełki': 0.4,                  # (było 0.5")
            'Miał rabat 10%?': 0.45,         # (było 0.6")
            'Cena Stara': 0.55,              # (było 0.7")
            'Grupa klienta': 0.6,            # (było 0.8")
            'Cena Nowa': 0.55,               # (było 0.7")
            'Wzrost PLN': 0.55,              # (było 0.7")
            'Wzrost %': 0.45,                # (było 0.6")
        }
        
        col_widths = []
        for col_header in csv_headers:
            width = col_width_map.get(col_header, 0.5)  # Default 0.5 jeśli nie w mapie
            col_widths.append(width * inch)
        
        clients_table = Table(clients_data, colWidths=col_widths)
        clients_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(NAVY)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),  # Nagłówki 8pt (było 6pt) +2pt
            ('FONTSIZE', (0, 1), (-1, -1), 8),  # Dane 8pt (było 6pt) +2pt
            ('ROWHEIGHT', (0, 0), (-1, 0), 0.50*inch),  # Nagłówek wyższy (było 0.45") dla większego fontu
            ('ROWHEIGHT', (0, 1), (-1, -1), 0.18*inch),  # Wiersze trochy wyższe (było 0.15") dla większego fontu
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(clients_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    # ============================================================================
    # SUGESTIE I ALERTY
    # ============================================================================
    story.append(PageBreak())
    story.append(Paragraph("Sugestie i Alerty", heading_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Zielony
    zielony = df[df['Status'] == 'Zielony']
    if len(zielony) > 0:
        story.append(Paragraph("Zielony - Wzrost do 10% (OK)", styles['Normal']))
        story.append(Paragraph(f"Liczba klientow: {len(zielony)}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Zółty
    zolty = df[df['Status'] == 'Zolty']
    if len(zolty) > 0:
        story.append(Paragraph("Zolty - Wzrost 10-20% lub >20% z rabatem", styles['Normal']))
        story.append(Paragraph(f"Liczba klientow: {len(zolty)}", styles['Normal']))
        story.append(Paragraph("AKCJA: Wymaga rozmowy z klientem", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Czerwony
    czerwony = df[df['Status'] == 'Czerwony']
    if len(czerwony) > 0:
        story.append(Paragraph("Czerwony - Wzrost >20% z rabatem", styles['Normal']))
        story.append(Paragraph(f"Liczba klientow: {len(czerwony)}", styles['Normal']))
        story.append(Paragraph("AKCJA: Wyjasnij anulowanie rabatu za Saldeo (10 PLN)", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Czarny (RYZYKO!)
    czarny = df[df['Status'] == 'Czarny']
    if len(czarny) > 0:
        story.append(Paragraph("Czarny - RYZYKO! Wzrost >20% bez rabatu", styles['Normal']))
        story.append(Paragraph(f"Liczba klientow: {len(czarny)}", styles['Normal']))
        story.append(Paragraph("AKCJA PRIORYTET: Zaproponuj rabat 20 PLN:", styles['Normal']))
        story.append(Paragraph("  - 10 PLN za dokumenty do 3. dnia miesiaca (kompletne)", styles['Normal']))
        story.append(Paragraph("  - 10 PLN za platnosc faktury w 3 dni", styles['Normal']))
        story.append(Paragraph("  - Wniosek o wakacje skladkowe (gratis)", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
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
