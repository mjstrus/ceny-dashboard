"""
Unit 2 Helper: Calculate New Prices (POPRAWIONA LOGIKA)

Cena_Docelowa = Cena_Stara × 1.10 (ZAWSZE, dla WSZYSTKICH)

Ale pokazuję:
- Co faktycznie płacili (z rabatem lub bez)
- Wzrost od faktycznej ceny (różny dla każdego)
- Wzrost od cennika (zawsze +10%)
"""

import pandas as pd


def calculate_new_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Oblicz ceny docelowe dla każdego klienta.
    
    Logika:
    - Cena_Docelowa = Cena_Stara × 1.10 (ZAWSZE, dla WSZYSTKICH)
    - Cena_Faktyczna = co faktycznie płacili:
      * Z rabatem: Cena_Stara × 0.90
      * Bez rabatu: Cena_Stara
    - Wzrost_% = (Docelowa - Faktyczna) / Faktyczna × 100
    - Wzrost_Od_Cennika = zawsze +10%
    
    Args:
        df: DataFrame z kolumnami Cena_Stara, Miał_Rabat_10%
    
    Returns:
        DataFrame z nowymi kolumnami
    """
    
    df = df.copy()
    
    # DOCELOWA: Zawsze +10% od cennika (dla WSZYSTKICH)
    df['Cena_Docelowa'] = (df['Cena_Stara'] * 1.10).round(2)
    
    # FAKTYCZNA: co faktycznie płacili
    df['Cena_Faktyczna'] = df.apply(
        lambda row: (row['Cena_Stara'] * 0.90).round(2) if row['Miał_Rabat_10%'] == 1 
                    else row['Cena_Stara'],
        axis=1
    )
    
    # WZROST: od faktycznej ceny
    df['Wzrost_Kwota'] = (df['Cena_Docelowa'] - df['Cena_Faktyczna']).round(2)
    df['Wzrost_%_Od_Faktycznej'] = ((df['Cena_Docelowa'] - df['Cena_Faktyczna']) / df['Cena_Faktyczna'] * 100).round(2)
    
    # Wzrost od cennika (zawsze +10%)
    df['Wzrost_%_Od_Cennika'] = 10.0
    
    return df


def get_price_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Przygotuj tabelę do edycji w Unit 2 (st.data_editor).
    
    Kolumny do edycji:
    - Grupa_Klienta (VIP/Standard)
    - Cena_Docelowa (ręczna edycja dla VIP)
    """
    
    display_cols = ['ID', 'Nazwa', 'Typ_Pełny', 'Cena_Stara', 'Miał_Rabat_10%', 
                    'Cena_Faktyczna', 'Grupa_Klienta', 'Cena_Docelowa', 
                    'Wzrost_Kwota', 'Wzrost_%_Od_Faktycznej', 'Wzrost_%_Od_Cennika']
    
    # Dodaj Grupa_Klienta jeśli jej brak
    if 'Grupa_Klienta' not in df.columns:
        df['Grupa_Klienta'] = 'Standard'
    
    df_display = df[display_cols].copy()
    df_display.columns = ['ID', 'Nazwa', 'Typ', 'Cennik', 'Rabat?', 
                          'Płacili', '👑 Grupa Klienta', '💰 Nowa Cena', 
                          'Wzrost PLN', 'Wzrost %', 'Wzrost Cennika %']
    
    # Format
    df_display['Rabat?'] = df_display['Rabat?'].map({1: '✓ TAK', 0: '✗ Nie'})
    
    return df_display
