"""
Unit 0 Helper: Price Manager
Wyświetl, edytuj i modyfikuj cennik
"""

import pandas as pd
import numpy as np


def get_default_pricing() -> pd.DataFrame:
    """
    Domyślny nowy cennik (2026).
    """
    
    data = {
        'Typ': ['KH', 'KH', 'KPIR', 'KPIR', 'Ryczałt', 'Ryczałt'],
        'VAT': ['tak', 'nie', 'tak', 'nie', 'tak', 'nie'],
        '1-10': [760, 660, 350, 320, 300, 250],
        '11-20': [1150, 980, 450, 420, 400, 250],
        '21-50': [1600, 1350, 580, 550, 530, 250],
        '51-100': [2250, 1800, 680, 650, 630, 250],
        '100+': [500, 400, 150, 120, 100, 0]
    }
    
    return pd.DataFrame(data)


def apply_global_modification(df: pd.DataFrame, typ: str, vat: str, percent_change: float) -> pd.DataFrame:
    """
    Zastosuj zmianę procentową dla konkretnego typu/VAT.
    
    Args:
        df: DataFrame cennnika
        typ: 'KH', 'KPIR', lub 'Ryczałt'
        vat: 'tak' lub 'nie'
        percent_change: zmiana % (np. +5 dla +5%)
    
    Returns:
        Zmodyfikowany DataFrame
    """
    
    df = df.copy()
    mask = (df['Typ'] == typ) & (df['VAT'] == vat)
    
    # Zmodyfikuj wszystkie kolumny cenowe
    price_cols = ['1-10', '11-20', '21-50', '51-100', '100+']
    
    for col in price_cols:
        if col in df.columns:
            df.loc[mask, col] = (df.loc[mask, col] * (1 + percent_change / 100)).round(2)
    
    return df


def apply_global_all_modification(df: pd.DataFrame, percent_change: float) -> pd.DataFrame:
    """
    Zastosuj zmianę procentową dla WSZYSTKICH cen.
    """
    
    df = df.copy()
    price_cols = ['1-10', '11-20', '21-50', '51-100', 'Paczka 25 (100+)']
    
    for col in price_cols:
        if col in df.columns:
            df[col] = (df[col] * (1 + percent_change / 100)).round(2)
    
    return df


def get_pricing_summary(df: pd.DataFrame) -> str:
    """
    Przygotuj podsumowanie cennnika (tekst).
    """
    
    summary = "📊 **Podsumowanie Cennnika:**\n\n"
    summary += "- **6 typów:** KH, KPIR, Ryczałt (każdy z VAT/bez VAT)\n"
    summary += "- **5 widełek:** 1-10, 11-20, 21-50, 51-100, 100+ (paczka 25)\n"
    summary += "- **Ryczałt bez VAT:** stała cena 250 PLN (brak widełek)\n"
    summary += f"- **Total pozycji:** {len(df)}\n"
    
    return summary
