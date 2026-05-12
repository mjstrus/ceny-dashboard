"""
Unit 2 Helper: Calculate New Prices (DEFENSYWNA WERSJA)
Obsługuje NaN, type safety, i problemy z danymi
"""

import pandas as pd
import numpy as np


def calculate_new_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Oblicz ceny docelowe dla każdego klienta.
    
    Logika:
    - Cena_Docelowa = Cena_Stara × 1.10 (ZAWSZE)
    - Cena_Faktyczna = co faktycznie płacili (z rabatem lub bez)
    - Wzrost_% = (Docelowa - Faktyczna) / Faktyczna × 100
    """
    
    df = df.copy()
    
    # Bezpieczna konwersja typów
    try:
        df['Cena_Stara'] = pd.to_numeric(df['Cena_Stara'], errors='coerce')
        df['Miał_Rabat_10%'] = pd.to_numeric(df['Miał_Rabat_10%'], errors='coerce').fillna(0).astype(int)
    except Exception as e:
        print(f"Błąd konwersji: {e}")
        return df
    
    # Usuń wiersze z NaN w Cena_Stara
    df = df.dropna(subset=['Cena_Stara'])
    
    # DOCELOWA: +10% od cennika
    df['Cena_Docelowa'] = (df['Cena_Stara'] * 1.10).round(2)
    
    # FAKTYCZNA: co faktycznie płacili
    def calculate_faktyczna(row):
        try:
            if row['Miał_Rabat_10%'] == 1:
                return round(row['Cena_Stara'] * 0.90, 2)
            else:
                return row['Cena_Stara']
        except:
            return row['Cena_Stara']
    
    df['Cena_Faktyczna'] = df.apply(calculate_faktyczna, axis=1)
    
    # WZROST: od faktycznej ceny
    def calculate_wzrost(row):
        try:
            if row['Cena_Faktyczna'] > 0:
                wzrost = ((row['Cena_Docelowa'] - row['Cena_Faktyczna']) / row['Cena_Faktyczna'] * 100)
                return round(wzrost, 2)
            else:
                return 0.0
        except:
            return 0.0
    
    df['Wzrost_Kwota'] = (df['Cena_Docelowa'] - df['Cena_Faktyczna']).round(2)
    df['Wzrost_%_Od_Faktycznej'] = df.apply(calculate_wzrost, axis=1)
    df['Wzrost_%_Od_Cennika'] = 10.0
    
    # Dodaj Grupa_Klienta jeśli jej brak
    if 'Grupa_Klienta' not in df.columns:
        df['Grupa_Klienta'] = 'Standard'
    
    return df


def get_price_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Przygotuj tabelę do edycji w Unit 2 (st.data_editor).
    """
    
    display_cols = ['ID', 'Nazwa', 'Typ_Pełny', 'Cena_Stara', 'Miał_Rabat_10%', 
                    'Cena_Faktyczna', 'Grupa_Klienta', 'Cena_Docelowa', 
                    'Wzrost_Kwota', 'Wzrost_%_Od_Faktycznej', 'Wzrost_%_Od_Cennika']
    
    # Sprawdź czy wszystkie kolumny istnieją
    for col in display_cols:
        if col not in df.columns:
            df[col] = None
    
    df_display = df[display_cols].copy()
    df_display.columns = ['ID', 'Nazwa', 'Typ', 'Cennik', 'Rabat?', 
                          'Płacili', '👑 Grupa Klienta', '💰 Nowa Cena', 
                          'Wzrost PLN', 'Wzrost %', 'Wzrost Cennika %']
    
    # Format
    df_display['Rabat?'] = df_display['Rabat?'].apply(
        lambda x: '✓ TAK' if x == 1 else '✗ Nie' if x == 0 else '?'
    )
    
    return df_display
