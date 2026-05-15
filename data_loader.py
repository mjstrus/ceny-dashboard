"""
Unit 1: Data Loader
Funkcje do wczytania i parsowania Master Excela z danymi klientów.
"""

import pandas as pd
import streamlit as st
from typing import Tuple, Optional

# Optional import - fallback jeśli constants.py nie istnieje
try:
    from constants import validate_data_columns, REQUIRED_DATA_COLUMNS
except ImportError:
    # Fallback - hardcoded required columns
    REQUIRED_DATA_COLUMNS = [
        'ID', 'Nazwa', 'Typ_Umowy', 'VAT', 'Doc_Marzec', 'Doc_Luty',
        'Doc_Styczeń', 'Doc_Avg', 'Cena_Stara', 'Miał_Rabat_10%',
    ]
    def validate_data_columns(df):
        """Fallback validation function"""
        missing = set(REQUIRED_DATA_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")


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
        return None, [f"[ERROR] Błąd wczytania Excel: {str(e)}"]
    
    # Walidacja struktury - tylko kolumny które MUSZĄ być w excelu
    errors = []
    required_columns = {
        'ID', 'Nazwa', 'Typ_Umowy', 'VAT', 'Cena_Stara',
        'Doc_Marzec', 'Doc_Luty', 'Doc_Styczeń', 'Miał_Rabat_10%',
    }
    
    missing = required_columns - set(df.columns)
    if missing:
        errors.append(f"[ERROR] Brakujące kolumny: {', '.join(missing)}")
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
    
    # Oczyść VAT (trim) i konwertuj na "tak"/"nie"
    df['VAT'] = df['VAT'].astype(str).str.strip().str.lower()
    df['VAT'] = df['VAT'].map(lambda x: 'tak' if x in ['tak', 'true', '1', 'yes'] else 'nie')
    
    # Konwertuj Cena_Stara na numeric PRZED walidacją
    if 'Cena_Stara' in df.columns:
        df['Cena_Stara'] = pd.to_numeric(df['Cena_Stara'], errors='coerce')
    
    # Konwertuj Miał_Rabat_10% na numeric PRZED walidacją
    if 'Miał_Rabat_10%' in df.columns:
        df['Miał_Rabat_10%'] = df['Miał_Rabat_10%'].astype(str).str.strip().str.lower()
        df['Miał_Rabat_10%'] = df['Miał_Rabat_10%'].isin(['tak', 'true', '1', 'yes']).astype(int)
    
    # Konwertuj Doc kolumny na numeric PRZED walidacją
    for col in ['Doc_Marzec', 'Doc_Luty', 'Doc_Styczeń', 'Doc_Średnia']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Walidacja typów i wartości
    validation_errors, df = validate_data(df)
    if validation_errors:
        errors.extend(validation_errors)
    
    # Jeśli tylko warnings - dalej wczytaj dane
    critical_errors = [e for e in errors if e.startswith('[ERROR]')]
    if critical_errors:
        return None, errors
    
    # Jeśli brak błędów krytycznych - zwróć df i warnings
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
    
    # Sprawdź czy wszystkie wymagane kolumny istnieją
    missing_cols = set(REQUIRED_DATA_COLUMNS) - set(df.columns)
    if missing_cols:
        errors.append(f"[ERROR] Brakuje kolumn: {sorted(missing_cols)}")
        # Zawsze zwracaj tuple (errors, df)
        return errors, df
    # Sprawdź duplikaty ID
    if df['ID'].duplicated().any():
        dup_ids = df[df['ID'].duplicated()]['ID'].unique()
        errors.append(f"[WARN]  Duplikaty ID: {list(dup_ids)}")
    
    # Sprawdź puste ID
    if df['ID'].isna().any():
        errors.append("[ERROR] Brakuje ID dla niektórych klientów")
    
    # Sprawdź typ umowy
    valid_types = {'Kh', 'KPIR', 'Ryczałt'}
    invalid = df[~df['Typ_Umowy'].isin(valid_types)]
    if not invalid.empty:
        errors.append(f"[ERROR] Niepoprawny typ umowy: {invalid['Typ_Umowy'].unique()}")
    
    # Sprawdź ceny > 0 - jeśli brakuje, wstaw 250 (domyślna)
    if 'Cena_Stara' in df.columns:
        missing_prices = df[(df['Cena_Stara'] <= 0) | (df['Cena_Stara'].isna())]
        if not missing_prices.empty:
            missing_ids = [int(x) for x in missing_prices["ID"].values]
            errors.append(f"[WARN]  Brakuje ceny dla ID: {missing_ids} - wstawiam domyślną 250 PLN")
            # Wstaw domyślną cenę
            df.loc[(df['Cena_Stara'] <= 0) | (df['Cena_Stara'].isna()), 'Cena_Stara'] = 250
    
    # Sprawdź ilości dokumentów (mogą być NaN dla nowych klientów, to OK)
    for col in ['Doc_Marzec', 'Doc_Luty', 'Doc_Styczeń']:
        if col in df.columns:
            na_count = df[col].isna().sum()
            if na_count > 0:
                errors.append(f"[WARN]  {na_count} brakuje wartości w {col} (OK dla nowych klientów)")
    
    return errors, df


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
    df_display['Ma Rabat'] = df_display['Ma Rabat'].map({1: 'OK Tak', 0: '✗ Nie'})
    
    return df_display
