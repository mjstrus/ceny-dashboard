"""
Unit 1: Data Loader
Funkcje do wczytania i parsowania Master Excela z danymi klientów.
"""

import pandas as pd
import streamlit as st
from typing import Tuple, Optional


@st.cache_data
def load_excel_file(file_path: str) -> Tuple[pd.DataFrame, list]:
    """
    Wczytaj Excel i zwaliduj strukturę.
    
    Args:
        file_path: ścieżka do pliku .xlsx
    
    Returns:
        Tuple[DataFrame, errors_list] gdzie:
        - DataFrame: załadowane dane (jeśli sukces)
        - errors_list: lista błędów walidacji (jeśli są)
    """
    try:
        df = pd.read_excel(file_path, sheet_name='Clients')
    except Exception as e:
        return None, [f"❌ Błąd wczytania Excel: {str(e)}"]
    
    # Walidacja struktury
    errors = []
    required_columns = {
        'ID', 'Nazwa', 'Typ_Umowy', 'VAT', 'Cena_Stara',
        'Doc_Marzec', 'Doc_Luty', 'Doc_Styczeń', 'Miał_Rabat_10%',
        'Doc_Średnia', 'Grupa_Widełk', 'Grupa_Klienta', 'Cena_Nowa'
    }
    
    missing = required_columns - set(df.columns)
    if missing:
        errors.append(f"❌ Brakujące kolumny: {', '.join(missing)}")
        return None, errors
    
    # DATA CLEANING
    # Usuń wiersze ze zmianymi ID (NaN)
    df = df.dropna(subset=['ID'])
    
    # Oczyść typ umowy: trim + standardyzuj
    df['Typ_Umowy'] = df['Typ_Umowy'].str.strip().str.upper()
    
    # Mapowanie do standardowych nazw
    typ_map = {
        'KH': 'Kh',
        'KPIR': 'KPIR',
        'RYCZAŁT': 'Ryczałt'
    }
    df['Typ_Umowy'] = df['Typ_Umowy'].map(typ_map).fillna(df['Typ_Umowy'])
    
    # Oczyść VAT (trim)
    df['VAT'] = df['VAT'].str.strip()
    
    # Walidacja typów i wartości
    validation_errors = validate_data(df)
    if validation_errors:
        errors.extend(validation_errors)
    
    if errors:
        return None, errors
    
    # Jeśli nie ma Doc_Średnia, oblicz ją
    if 'Doc_Średnia' not in df.columns:
        df['Doc_Średnia'] = df[['Doc_Marzec', 'Doc_Luty', 'Doc_Styczeń']].mean(axis=1).round(1)
    
    # Alias do Doc_Avg
    df['Doc_Avg'] = df['Doc_Średnia']
    
    # Ustandaryzuj kolumny
    df['Typ_Pełny'] = df['Typ_Umowy'] + ' ' + df['VAT']
    
    return df, []


def validate_data(df: pd.DataFrame) -> list:
    """
    Waliduj dane w DataFrame.
    
    Returns:
        Lista błędów walidacji (pusty list = OK)
    """
    errors = []
    
    # Sprawdź duplikaty ID
    if df['ID'].duplicated().any():
        dup_ids = df[df['ID'].duplicated()]['ID'].unique()
        errors.append(f"⚠️  Duplikaty ID: {list(dup_ids)}")
    
    # Sprawdź puste ID
    if df['ID'].isna().any():
        errors.append("❌ Brakuje ID dla niektórych klientów")
    
    # Sprawdź typ umowy
    valid_types = {'Kh', 'KPIR', 'Ryczałt'}
    invalid = df[~df['Typ_Umowy'].isin(valid_types)]
    if not invalid.empty:
        errors.append(f"❌ Niepoprawny typ umowy: {invalid['Typ_Umowy'].unique()}")
    
    # Sprawdź ceny > 0
    invalid_prices = df[df['Cena_Stara'] <= 0]
    if not invalid_prices.empty:
        errors.append(f"❌ Cena <= 0 dla ID: {list(invalid_prices['ID'].values)}")
    
    # Sprawdź ilości dokumentów (mogą być NaN dla nowych klientów, to OK)
    for col in ['Doc_Marzec', 'Doc_Luty', 'Doc_Styczeń']:
        if col in df.columns:
            na_count = df[col].isna().sum()
            if na_count > 0:
                errors.append(f"⚠️  {na_count} brakuje wartości w {col} (OK dla nowych klientów)")
    
    return errors


def get_display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Przygotuj DataFrame do wyświetlenia w dashboard.
    
    Returns:
        DataFrame z wybranym i przeformatowanym kolumnami
    """
    display_cols = ['ID', 'Nazwa', 'Typ_Pełny', 'Cena_Stara', 'Doc_Avg', 'Miał_Rabat_10%']
    
    df_display = df[display_cols].copy()
    df_display.columns = ['ID', 'Nazwa', 'Typ Umowy', 'Cena Stara', 'Śr. Dokumentów/mc', 'Ma Rabat']
    
    # Format: Miał_Rabat_10% -> Tak/Nie
    df_display['Ma Rabat'] = df_display['Ma Rabat'].map({1: '✓ Tak', 0: '✗ Nie'})
    
    return df_display
