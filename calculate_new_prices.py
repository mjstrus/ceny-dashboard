"""
Unit 2 Helper: Calculate New Prices
Oblicza Cena_Nowa na podstawie Cena_Stara + 10% wzrost + anulowanie rabatu
"""

import pandas as pd


def calculate_new_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Oblicz nowe ceny dla każdego klienta.
    
    Logika:
    - Zawsze: +10% (Cena_Stara × 1.10)
    - Jeśli miał rabat: +dodatkowe 10% (czyli razem × 1.20)
    
    Args:
        df: DataFrame z kolumnami Cena_Stara, Miał_Rabat_10%
    
    Returns:
        DataFrame z dodanymi kolumnami Cena_Nowa, Wzrost_Kwota, Wzrost_%
    """
    
    df = df.copy()
    
    # Oblicz nową cenę
    # Logika:
    # - Miał_Rabat_10% = 1 → Cena_Nowa = Cena_Stara (wyrównanie, likwidacja rabatu)
    # - Miał_Rabat_10% = 0 → Cena_Nowa = Cena_Stara × 1.10 (+10% wzrost)
    df['Cena_Nowa_Auto'] = df.apply(
        lambda row: row['Cena_Stara'] if row['Miał_Rabat_10%'] == 1 
                    else row['Cena_Stara'] * 1.10,
        axis=1
    ).round(2)
    
    # Jeśli już ma Cena_Nowa w danych, użyj auto dla nowych, ale zachowaj istniejące
    if 'Cena_Nowa' in df.columns:
        # Zamień NaN na auto-obliczone
        df['Cena_Nowa'] = df['Cena_Nowa'].fillna(df['Cena_Nowa_Auto'])
    else:
        df['Cena_Nowa'] = df['Cena_Nowa_Auto']
    
    # Oblicz wpływ
    df['Wzrost_Kwota'] = (df['Cena_Nowa'] - df['Cena_Stara']).round(2)
    df['Wzrost_%'] = ((df['Cena_Nowa'] - df['Cena_Stara']) / df['Cena_Stara'] * 100).round(2)
    
    return df


def get_price_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Przygotuj tabelę do wyświetlenia w Unit 2.
    """
    
    display_cols = ['ID', 'Nazwa', 'Typ_Pełny', 'Cena_Stara', 'Miał_Rabat_10%', 
                    'Cena_Nowa_Auto', 'Cena_Nowa', 'Wzrost_Kwota', 'Wzrost_%']
    
    df_display = df[display_cols].copy()
    df_display.columns = ['ID', 'Nazwa', 'Typ', 'Cena Stara', 'Miał Rabat', 
                          'Auto (bez override)', 'Cena Nowa', 'Wpływ PLN', 'Wpływ %']
    
    # Format
    df_display['Miał Rabat'] = df_display['Miał Rabat'].map({1: '✓ Tak (+10%)', 0: '✗ Nie'})
    
    return df_display
