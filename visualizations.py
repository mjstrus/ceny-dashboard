"""
Unit 4 & 5: Risk Assessment & Visualizations
Segmentacja zagrożenia i wykresy.

Nota: Unit 4 (logika segmentacji) jest już w calculator.py (segment_clients).
Ten plik zawiera dodatkowe wizualizacje dla Unit 5.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict


def create_segment_pie_chart(df: pd.DataFrame) -> go.Figure:
    """
    Utwórz pie chart rozkładu segmentów.
    """
    segment_counts = df['Segment'].value_counts()
    
    colors = {
        '🟢 Zielony': '#00CC96',
        '🟡 Żółty': '#FFA15A',
        '🔴 Czerwony': '#EF553B'
    }
    
    fig = px.pie(
        values=segment_counts.values,
        names=segment_counts.index,
        color=segment_counts.index,
        color_discrete_map=colors,
        title="Rozkład Segmentów Ryzyka"
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


def create_impact_histogram(df: pd.DataFrame) -> go.Figure:
    """
    Histogram: ile klientów ma jaki % wzrostu.
    """
    fig = px.histogram(
        df,
        x='Wplyw_Pct',
        nbins=20,
        title="Rozkład Wpływu Ceny (% wzrostu)",
        labels={'Wplyw_Pct': 'Wpływ %', 'count': 'Liczba klientów'},
        color_discrete_sequence=['#1B2A4A']
    )
    
    # Dodaj linię threshold 20%
    fig.add_vline(x=20, line_dash="dash", line_color="red", 
                  annotation_text="Próg: 20%", annotation_position="top right")
    
    fig.add_vline(x=10, line_dash="dash", line_color="orange",
                  annotation_text="Próg: 10%", annotation_position="top left")
    
    return fig


def create_revenue_comparison(revenue_impact: Dict) -> go.Figure:
    """
    Bar chart: przychód dzisiaj vs przychód docelowy.
    """
    fig = go.Figure(data=[
        go.Bar(
            name='Dzisiaj',
            x=['Przychód/mc'],
            y=[revenue_impact['revenue_old_monthly']],
            marker_color='#E8A000',
            text=[f"${revenue_impact['revenue_old_monthly']:,.0f}"],
            textposition='auto'
        ),
        go.Bar(
            name='Docelowo',
            x=['Przychód/mc'],
            y=[revenue_impact['revenue_new_monthly']],
            marker_color='#1B2A4A',
            text=[f"${revenue_impact['revenue_new_monthly']:,.0f}"],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Przychód: Dzisiaj vs Docelowo",
        barmode='group',
        hovermode='x unified'
    )
    
    return fig


def create_by_type_comparison(df: pd.DataFrame) -> go.Figure:
    """
    Przychód per typ umowy: stary vs nowy.
    """
    df_agg = df.groupby('Typ_Pełny').agg({
        'Przychod_Stary_Mc': 'sum',
        'Przychod_Nowy_Mc': 'sum'
    }).reset_index()
    
    fig = go.Figure(data=[
        go.Bar(
            name='Przychód Stary',
            x=df_agg['Typ_Pełny'],
            y=df_agg['Przychod_Stary_Mc'],
            marker_color='#E8A000'
        ),
        go.Bar(
            name='Przychód Nowy',
            x=df_agg['Typ_Pełny'],
            y=df_agg['Przychod_Nowy_Mc'],
            marker_color='#1B2A4A'
        )
    ])
    
    fig.update_layout(
        title="Przychód per Typ Umowy",
        barmode='group',
        hovermode='x unified'
    )
    
    return fig


def create_segment_details_table(segment_summary: Dict, revenue_impact: Dict) -> pd.DataFrame:
    """
    Tabela podsumowania per segment.
    """
    data = []
    
    for segment, info in segment_summary.items():
        data.append({
            'Segment': segment,
            'Liczba Klientów': info['count'],
            '% Ogółem': f"{info['count_pct']:.1f}%",
            'Śr. Wpływ %': f"{info['avg_impact_pct']:.1f}%",
            'Razem Wpływ (PLN)': f"${info['total_impact_pln']:,.0f}",
            'Śr. Przychód Stary': f"${info['avg_income_old']:,.0f}",
            'Śr. Przychód Nowy': f"${info['avg_income_new']:,.0f}"
        })
    
    return pd.DataFrame(data)


def create_threat_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tabela: klienci zagrożeni (Czerwoni i Żółci).
    """
    threatened = df[df['Segment'].isin(['🟡 Żółty', '🔴 Czerwony'])].copy()
    
    display_cols = ['ID', 'Nazwa', 'Typ_Pełny', 'Cena_Bazowa', 'Cena_Nowa', 
                    'Wplyw_Pct', 'Segment', 'Zagroženie']
    
    if not threatened.empty:
        df_threat = threatened[display_cols].copy()
        df_threat.columns = ['ID', 'Nazwa', 'Typ', 'Cena Stara', 'Cena Nowa',
                            'Wpływ %', 'Segment', 'Zagrożenie']
        
        # Sortuj po wpływie (descending)
        df_threat['Sort_Key'] = df_threat['Wpływ %'].astype(float)
        df_threat = df_threat.sort_values('Sort_Key', ascending=False).drop('Sort_Key', axis=1)
        
        return df_threat
    else:
        return pd.DataFrame()
