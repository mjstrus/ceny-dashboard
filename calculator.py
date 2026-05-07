"""
Unit 3: Price Impact Calculator
Kalkulacja wpływu zmian ceny dla każdego klienta.

Logika:
- Wzrost bazowy: zawsze +10% (z planów komunikacji)
- Anulowanie rabatu: 0% (jeśli bez rabatu) lub +10% (jeśli miał)
- Razem wzrost = wzrost_bazowy + anulowanie_rabatu
- Przychód: cena_bazowa × liczba_dokumentów
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


def calculate_price_impact(
    df: pd.DataFrame,
    new_prices: Dict[str, float],
    base_increase_pct: float = 0.10,
    rabat_loss_pct: float = 0.10
) -> pd.DataFrame:
    """
    Oblicz wpływ zmian ceny dla każdego klienta.
    
    Args:
        df: DataFrame z danymi klientów (z data_loader)
        new_prices: dict {'Kh_vat': 500, 'Kh_no_vat': 400, ...}
        base_increase_pct: zawsze 10% wzrost (z komunikacji)
        rabat_loss_pct: rabat 10% dla tych którzy go mieli
    
    Returns:
        DataFrame z nowymi kolumnami (przychód, wpływ, segment)
    """
    
    df = df.copy()
    
    # Mapowanie nowych cen na DataFrame
    def get_new_price(row):
        typ_key = row['Typ_Umowy'].replace('Ryczałt', 'Ryczalt')
        vat_key = 'vat' if 'z VAT' in row['VAT'] else 'no_vat'
        key = f"{typ_key}_{vat_key}"
        return new_prices.get(key, row['Cena_Bazowa'])  # fallback na starą cenę
    
    df['Cena_Nowa'] = df.apply(get_new_price, axis=1)
    
    # =====================================================================
    # PRZYCHÓD OBLICZENIE
    # =====================================================================
    
    # Przychód stary (obecny) - cena bazowa × średnia dokumentów
    df['Przychod_Stary_Mc'] = df['Cena_Bazowa'] * df['Doc_Avg']
    
    # Przychód nowy - nowa cena × średnia dokumentów
    # Dla klientów z rabatem: nowa cena będzie wyższa (rabat się anuluje)
    df['Przychod_Nowy_Mc'] = df['Cena_Nowa'] * df['Doc_Avg']
    
    # =====================================================================
    # KOMPONENTY ZMIAN CENY
    # =====================================================================
    
    # Wzrost bazowy: zawsze +10%
    df['Wzrost_Bazowy_Pct'] = base_increase_pct * 100  # 10%
    
    # Anulowanie rabatu: 0% (bez rabatu) lub +10% (miał rabat)
    df['Anulowanie_Rabatu_Pct'] = df['Czy_Rabat'].apply(
        lambda x: rabat_loss_pct * 100 if x == 1 else 0
    )
    
    # Razem wzrost
    df['Wzrost_Razem_Pct'] = df['Wzrost_Bazowy_Pct'] + df['Anulowanie_Rabatu_Pct']
    
    # =====================================================================
    # WPŁYW (DELTA)
    # =====================================================================
    
    # Wpływ w PLN
    df['Wplyw_Pln'] = df['Przychod_Nowy_Mc'] - df['Przychod_Stary_Mc']
    
    # Wpływ w %
    df['Wplyw_Pct'] = (df['Wplyw_Pln'] / df['Przychod_Stary_Mc'] * 100).round(2)
    
    # Edge case: jeśli przychód stary = 0, ustaw 0
    df.loc[df['Przychod_Stary_Mc'] == 0, 'Wplyw_Pct'] = 0
    
    return df


def segment_clients(df: pd.DataFrame, threshold_1: float = 10.0, threshold_2: float = 20.0) -> pd.DataFrame:
    """
    Segmentuj klientów na podstawie wpływu ceny.
    
    Args:
        df: DataFrame z obliczonym Wplyw_Pct
        threshold_1: próg dla zielonego (≤ 10%)
        threshold_2: próg dla żółtego (≤ 20%)
    
    Returns:
        DataFrame z dodatkowymi kolumnami (Segment, Kolor, Zagrożenie)
    """
    
    df = df.copy()
    
    # Segmentacja
    df['Segment'] = pd.cut(
        df['Wplyw_Pct'],
        bins=[-np.inf, threshold_1, threshold_2, np.inf],
        labels=['🟢 Zielony', '🟡 Żółty', '🔴 Czerwony']
    )
    
    # Mapa kolorów (do CSS/Streamlit)
    segment_colors = {
        '🟢 Zielony': 'green',
        '🟡 Żółty': 'orange',
        '🔴 Czerwony': 'red'
    }
    df['Segment_Color'] = df['Segment'].map(segment_colors)
    
    # Poziom zagrożenia
    zagroženie_map = {
        '🟢 Zielony': 'Brak',
        '🟡 Żółty': 'Średnie',
        '🔴 Czerwony': 'Wysokie'
    }
    df['Zagroženie'] = df['Segment'].map(zagroženie_map)
    
    return df


def get_segment_summary(df: pd.DataFrame) -> Dict[str, Dict]:
    """
    Uzyskaj podsumowanie per segment.
    
    Returns:
        Dict: {
            'Zielony': {'count': 50, 'avg_impact_pct': 5, 'total_impact_pln': 25000},
            ...
        }
    """
    
    summary = {}
    
    for segment in df['Segment'].unique():
        subset = df[df['Segment'] == segment]
        
        summary[segment] = {
            'count': len(subset),
            'count_pct': len(subset) / len(df) * 100,
            'avg_impact_pct': subset['Wplyw_Pct'].mean(),
            'total_impact_pln': subset['Wplyw_Pln'].sum(),
            'avg_income_old': subset['Przychod_Stary_Mc'].mean(),
            'avg_income_new': subset['Przychod_Nowy_Mc'].mean(),
        }
    
    return summary


def get_revenue_impact(df: pd.DataFrame) -> Dict[str, float]:
    """
    Uzyskaj agregowany wpływ na przychód.
    
    Returns:
        Dict: {
            'revenue_old_monthly': X,
            'revenue_new_monthly': Y,
            'impact_pln': Y-X,
            'impact_pct': (Y-X)/X*100
        }
    """
    
    revenue_old = df['Przychod_Stary_Mc'].sum()
    revenue_new = df['Przychod_Nowy_Mc'].sum()
    impact_pln = revenue_new - revenue_old
    impact_pct = (impact_pln / revenue_old * 100) if revenue_old > 0 else 0
    
    return {
        'revenue_old_monthly': revenue_old,
        'revenue_new_monthly': revenue_new,
        'revenue_old_annual': revenue_old * 12,
        'revenue_new_annual': revenue_new * 12,
        'impact_pln_monthly': impact_pln,
        'impact_pln_annual': impact_pln * 12,
        'impact_pct': impact_pct,
    }


def get_display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Przygotuj DataFrame do wyświetlenia w dashboardzie.
    """
    
    display_cols = [
        'ID', 'Nazwa', 'Typ_Pełny', 
        'Cena_Bazowa', 'Cena_Nowa',
        'Doc_Avg',
        'Przychod_Stary_Mc', 'Przychod_Nowy_Mc', 'Wplyw_Pln',
        'Wzrost_Bazowy_Pct', 'Anulowanie_Rabatu_Pct', 'Wplyw_Pct',
        'Segment', 'Zagroženie'
    ]
    
    df_display = df[display_cols].copy()
    
    # Rename for display
    df_display.columns = [
        'ID', 'Nazwa', 'Typ',
        'Cena Stara', 'Cena Nowa',
        'Śr. Dok/mc',
        'Przychód Stary', 'Przychód Nowy', 'Wpływ (PLN)',
        'Wzrost %', 'Rabat ∅ %', 'Wpływ %',
        'Segment', 'Zagrożenie'
    ]
    
    return df_display
