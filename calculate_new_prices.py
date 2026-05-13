"""
Unit 2 Helper: Calculate New Prices (INTEGRACJA Z UNIT 0)

Mapuje dokumenty na widełki i pobiera ceny z Unit 0 cennnika
"""

import pandas as pd
import numpy as np


def map_docs_to_range(doc_count: float) -> str:
    """
    Mapuj ilość dokumentów na grupę widełk.
    
    Args:
        doc_count: Średnia liczba dokumentów na miesiąc
    
    Returns:
        String: '1-10', '11-20', '21-50', '51-100', lub '100+'
    """
    
    doc_count = float(doc_count) if doc_count else 0
    
    if doc_count <= 10:
        return '1-10'
    elif doc_count <= 20:
        return '11-20'
    elif doc_count <= 50:
        return '21-50'
    elif doc_count <= 100:
        return '51-100'
    else:
        return '100+'


def get_price_from_pricing(typ: str, vat: str, price_range: str, pricing_df: pd.DataFrame) -> float:
    """
    Pobierz cenę z Unit 0 cennnika.
    
    Args:
        typ: 'Kh', 'KPIR', 'Ryczałt'
        vat: 'tak', 'nie'
        price_range: '1-10', '11-20', itd.
        pricing_df: DataFrame cennnika z Unit 0
    
    Returns:
        Cena (float) lub NaN jeśli nie znaleziono
    """
    
    # Normalizuj typ
    typ = typ.strip().upper() if typ else ""
    if typ == 'KH':
        typ = 'KH'
    elif typ in ['KPIR', 'KPIR']:
        typ = 'KPIR'
    elif typ in ['RYCZAŁT', 'RYCZALT']:
        typ = 'Ryczałt'
    
    # Szukaj w cenniku
    mask = (pricing_df['Typ'] == typ) & (pricing_df['VAT'] == vat.strip().lower())
    
    if mask.any():
        row = pricing_df[mask].iloc[0]
        price = row[price_range]
        return float(price) if price > 0 else np.nan
    
    return np.nan


def calculate_new_prices(df: pd.DataFrame, pricing_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Oblicz ceny docelowe na podstawie Unit 0 cennnika.
    
    Logika:
    - Dla każdego klienta: mapuj Doc_Avg na grupę widełk
    - Pobierz cenę z Unit 0 cennnika (na podstawie Typ + VAT + widełka)
    - Cena_Faktyczna = co faktycznie płacili (z rabatem lub bez)
    - Cena_Docelowa = cena z cennnika Unit 0
    - Wzrost = różnica
    
    Args:
        df: DataFrame klientów
        pricing_df: DataFrame cennnika z Unit 0
    
    Returns:
        DataFrame z kolumnami: Cena_Range, Cena_Docelowa, Cena_Faktyczna, Wzrost_Kwota, Wzrost_%
    """
    
    df = df.copy()
    
    # Jeśli brak pricing_df, zwróć oryginalne dane
    if pricing_df is None or pricing_df.empty:
        return df
    
    # Bezpieczna konwersja typów
    try:
        df['Cena_Stara'] = pd.to_numeric(df['Cena_Stara'], errors='coerce')
        df['Doc_Avg'] = pd.to_numeric(df['Doc_Avg'], errors='coerce')
        df['Miał_Rabat_10%'] = pd.to_numeric(df['Miał_Rabat_10%'], errors='coerce').fillna(0).astype(int)
    except Exception as e:
        print(f"Błąd konwersji: {e}")
        return df
    
    # Mapuj dokumenty na grupy widełk
    df['Cena_Range'] = df['Doc_Avg'].apply(map_docs_to_range)
    
    # Pobierz ceny z Unit 0 cennnika
    def get_cena_docelowa(row):
        try:
            price = get_price_from_pricing(
                row['Typ_Umowy'],
                row['VAT'],
                row['Cena_Range'],
                pricing_df
            )
            return price if not pd.isna(price) else row['Cena_Stara']
        except:
            return row['Cena_Stara']
    
    df['Cena_Docelowa'] = df.apply(get_cena_docelowa, axis=1)
    
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
    
    # Dodaj Grupa_Klienta jeśli jej brak
    if 'Grupa_Klienta' not in df.columns:
        df['Grupa_Klienta'] = 'Standard'
    
    # Logika FREE: jeśli Grupa_Klienta=FREE, to Cena_Docelowa=0 (gratis!)
    free_mask = df['Grupa_Klienta'].str.upper() == 'FREE'
    if free_mask.any():
        df.loc[free_mask, 'Cena_Docelowa'] = 0.0
        df.loc[free_mask, 'Wzrost_Kwota'] = -df.loc[free_mask, 'Cena_Faktyczna']
        df.loc[free_mask, 'Wzrost_%_Od_Faktycznej'] = -100.0
    
    return df


def get_price_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Przygotuj tabelę do edycji w Unit 2 (st.data_editor).
    """
    
    display_cols = ['ID', 'Nazwa', 'Typ_Pełny', 'Cena_Range', 'Cena_Stara', 'Miał_Rabat_10%', 
                    'Cena_Faktyczna', 'Grupa_Klienta', 'Cena_Docelowa', 
                    'Wzrost_Kwota', 'Wzrost_%_Od_Faktycznej']
    
    # Sprawdź czy wszystkie kolumny istnieją
    for col in display_cols:
        if col not in df.columns:
            df[col] = None
    
    df_display = df[display_cols].copy()
    df_display.columns = ['ID', 'Nazwa', 'Typ', 'Widełka', 'Cennik', 'Rabat?', 
                          'Płacili', '👑 Grupa Klienta', '💰 Nowa Cena (Unit 0)', 
                          'Wzrost PLN', 'Wzrost %']
    
    # Format
    df_display['Rabat?'] = df_display['Rabat?'].apply(
        lambda x: '✓ TAK' if x == 1 else '✗ Nie' if x == 0 else '?'
    )
    
    return df_display
