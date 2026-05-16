"""
Unit 2 Helper: Calculate New Prices (INTEGRACJA Z UNIT 0)

Mapuje dokumenty na widełki i pobiera ceny z Unit 0 cennnika
"""

import pandas as pd
import numpy as np

# Optional import - fallback jeśli constants.py nie istnieje
try:
    from constants import (
        validate_data_columns,
        validate_pricing_columns,
        PACKAGE_SIZE_DOCS,
        DEFAULT_PRICE,
    )
except ImportError:
    # Fallback values
    PACKAGE_SIZE_DOCS = 25
    DEFAULT_PRICE = 250
    
    def validate_data_columns(df):
        """Fallback validation"""
        pass
    
    def validate_pricing_columns(df):
        """Fallback validation"""
        pass


def calculate_price_with_packages(
    typ: str,
    vat: str,
    doc_count: float,
    pricing_df: pd.DataFrame
) -> float:
    """
    Calculate final price including package support for 100+ documents.
    
    Single unified function replacing:
    - map_docs_to_range()
    - get_price_from_pricing()
    - get_cena_docelowa() wrapper
    
    Args:
        typ: Client type ('KH', 'KPIR', 'Ryczałt')
        vat: VAT status ('tak' or 'nie')
        doc_count: Average monthly document count
        pricing_df: Pricing table from Unit 0 with columns:
                   Typ, VAT, '1-10', '11-20', '21-50', '51-100', '100+'
    
    Returns:
        float: Final price, or 0 if calculation fails
        
    Logic:
    1. If doc_count <= 100: return price from appropriate range
    2. If doc_count > 100: return base_price(51-100) + packages_count * package_price
       where packages_count = ceil((doc_count - 100) / PACKAGE_SIZE_DOCS)
    
    Example:
    - doc_count = 110, typ = 'KH', vat = 'tak'
    - base_price = 2250 (51-100 range)
    - package_price = 500 (100+ column)
    - packages = ceil(10/25) = 1
    - total = 2250 + 1*500 = 2750
    """
    
    try:
        doc_count = float(doc_count) if doc_count else 0
        
        # Normalize inputs
        typ = str(typ).strip().upper() if typ else ""
        if typ == 'KH':
            typ = 'KH'
        elif typ in ['KPIR']:
            typ = 'KPIR'
        elif typ in ['RYCZAŁT', 'RYCZALT']:
            typ = 'Ryczałt'
        
        vat = str(vat).strip().lower() if vat else 'nie'
        
        # Find pricing row
        mask = (pricing_df['Typ'] == typ) & (pricing_df['VAT'] == vat)
        if not mask.any():
            return 0.0  # Type/VAT combo not found
        
        pricing_row = pricing_df[mask].iloc[0]
        
        # Calculate price range based on doc_count
        if doc_count <= 10:
            price_range_col = '1-10'
        elif doc_count <= 20:
            price_range_col = '11-20'
        elif doc_count <= 50:
            price_range_col = '21-50'
        elif doc_count <= 100:
            price_range_col = '51-100'
        else:
            # 100+ documents: use base price + packages
            base_price = float(pricing_row['51-100']) if pricing_row['51-100'] > 0 else 0
            package_price = float(pricing_row['100+']) if pricing_row['100+'] > 0 else 0
            
            docs_over_100 = doc_count - 100
            num_packages = int(np.ceil(docs_over_100 / PACKAGE_SIZE_DOCS))
            
            total = base_price + (num_packages * package_price)
            return total if total > 0 else 0
        
        # For doc_count <= 100: return price from range
        price = float(pricing_row[price_range_col]) if pricing_row[price_range_col] > 0 else 0
        return price
        
    except Exception as e:
        # Silent fail - return 0
        return 0.0


def map_docs_to_range(doc_count: float) -> str:
    """
    DEPRECATED: Use calculate_price_with_packages() instead.
    
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
    DEPRECATED: Use calculate_price_with_packages() instead.
    
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
    
    # VALIDATION: fail-fast na złych danych
    try:
        validate_data_columns(df)
        validate_pricing_columns(pricing_df)
    except ValueError as e:
        raise ValueError(f"Data validation error: {e}")
    
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
    
    # Oblicz ceny UNIFIED FUNCTION - jedną zamiast 3 funkcji
    df['Cena_Docelowa'] = df.apply(
        lambda row: calculate_price_with_packages(
            row['Typ_Umowy'],
            row['VAT'],
            row['Doc_Avg'],
            pricing_df
        ) or row['Cena_Stara'],  # Fallback to Cena_Stara if calculation fails
        axis=1
    )
    
    # FAKTYCZNA: co faktycznie płacili (Cena_Stara już zawiera rabat!)
    df['Cena_Faktyczna'] = df['Cena_Stara'].round(2)
    
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
    
    # WZROST gdyby nie było rabatu (od Cena_Stara)
    def calculate_wzrost_bez_rabatu(row):
        try:
            if row['Cena_Stara'] > 0:
                wzrost = ((row['Cena_Docelowa'] - row['Cena_Stara']) / row['Cena_Stara'] * 100)
                return round(wzrost, 2)
            else:
                return 0.0
        except:
            return 0.0
    
    df['Wzrost_Kwota'] = (df['Cena_Docelowa'] - df['Cena_Faktyczna']).round(2)
    df['Wzrost_%_Od_Faktycznej'] = df.apply(calculate_wzrost, axis=1)
    df['Wzrost_%_Bez_Rabatu'] = df.apply(calculate_wzrost_bez_rabatu, axis=1)
    
    # STATUS SEGMENTACJI (Zielony/Żółty/Czerwony/Czarny)
    def assign_status(row):
        wzrost_pct = row['Wzrost_%_Od_Faktycznej']
        miał_rabat = row['Miał_Rabat_10%']
        
        if wzrost_pct <= 10:
            return 'Zielony'
        elif wzrost_pct <= 20:
            return 'Żółty'
        elif wzrost_pct > 20 and miał_rabat == 1:
            return 'Czerwony'  # Miał rabat — wzrost to anulowanie rabatu (łatwo wyjaśnić)
        else:
            return 'Czarny'  # Rzeczywisty wzrost ceny BEZ rabatu = RYZYKO!
    
    df['Status'] = df.apply(assign_status, axis=1)
    
    return df


def get_price_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Przygotuj tabelę do edycji w Unit 2 (st.data_editor).
    TYLKO kolumny do edycji - uproszczone!
    """
    
    # Uproszczony zbiór kolumn - TYLKO TO CO ISTNIEJE
    display_cols = ['ID', 'Nazwa', 'Typ_Umowy', 'Status', 'Cena_Range', 
                    'Cena_Stara', 'Grupa_Klienta', 'Cena_Docelowa']
    
    # Sprawdzenie czy kolumny istnieją
    available_cols = [col for col in display_cols if col in df.columns]
    df_display = df[available_cols].copy()
    
    # Formatuj Status z kolorami
    if 'Status' in df_display.columns:
        df_display['Status'] = df_display['Status'].apply(
            lambda x: '🟢 Zielony' if x == 'Zielony' 
                      else '🟡 Żółty' if x == 'Żółty'
                      else '🔴 Czerwony' if x == 'Czerwony'
                      else '⚫ Czarny' if x == 'Czarny'
                      else '❓ Nieznany'
        )
    
    # Zmień nazwy kolumn na user-friendly
    col_mapping = {
        'ID': 'ID',
        'Nazwa': 'Nazwa',
        'Typ_Umowy': 'Typ',
        'Status': '📊 Status',
        'Cena_Range': 'Widełka',
        'Cena_Stara': 'Cena Stara',
        'Grupa_Klienta': '👑 Grupa Klienta',
        'Cena_Docelowa': '💰 Nowa Cena'
    }
    
    df_display = df_display.rename(columns={k: v for k, v in col_mapping.items() if k in df_display.columns})
    
    return df_display
