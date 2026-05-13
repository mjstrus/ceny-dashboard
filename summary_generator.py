"""
Unit 3 Helper: Summary Generator
Podsumowanie listy klientów per pracownik (Standard + VIP + FREE)
"""

import pandas as pd
import numpy as np


def generate_summary(df: pd.DataFrame) -> dict:
    """
    Wygeneruj podsumowanie dla listy klientów.
    
    Args:
        df: DataFrame z kolumnami: Cena_Faktyczna, Cena_Docelowa, Grupa_Klienta, Doc_Avg, Wzrost_%_Od_Faktycznej
    
    Returns:
        Dict z metrykami
    """
    
    if df is None or df.empty:
        return {}
    
    df = df.copy()
    
    # Bezpieczne konwersje
    df['Cena_Faktyczna'] = pd.to_numeric(df['Cena_Faktyczna'], errors='coerce').fillna(0)
    df['Cena_Docelowa'] = pd.to_numeric(df['Cena_Docelowa'], errors='coerce').fillna(0)
    df['Doc_Avg'] = pd.to_numeric(df['Doc_Avg'], errors='coerce').fillna(0)
    df['Wzrost_%_Od_Faktycznej'] = pd.to_numeric(df['Wzrost_%_Od_Faktycznej'], errors='coerce').fillna(0)
    df['Miał_Rabat_10%'] = pd.to_numeric(df['Miał_Rabat_10%'], errors='coerce').fillna(0).astype(int)
    
    # Normalizuj Grupa_Klienta
    if 'Grupa_Klienta' not in df.columns:
        df['Grupa_Klienta'] = 'Standard'
    df['Grupa_Klienta'] = df['Grupa_Klienta'].fillna('Standard')
    
    # Segmentacja
    standard_df = df[df['Grupa_Klienta'] == 'Standard']
    vip_df = df[df['Grupa_Klienta'] == 'VIP']
    free_df = df[df['Grupa_Klienta'] == 'FREE']
    
    # Metryki finansowe (bez FREE)
    paying_df = pd.concat([standard_df, vip_df])
    
    przychod_przed = paying_df['Cena_Faktyczna'].sum()
    przychod_po = paying_df['Cena_Docelowa'].sum()
    wzrost_pln = przychod_po - przychod_przed
    wzrost_pct = (wzrost_pln / przychod_przed * 100) if przychod_przed > 0 else 0
    
    # Roczny impact
    roczny_przed = przychod_przed * 12
    roczny_po = przychod_po * 12
    roczny_wzrost = roczny_po - roczny_przed
    
    # Średnie
    srednia_doc = df['Doc_Avg'].mean()
    srednia_cena_przed = df['Cena_Faktyczna'].mean() if len(df) > 0 else 0
    srednia_cena_po = df['Cena_Docelowa'].mean() if len(df) > 0 else 0
    
    # Segmentacja po kolorach (Status)
    if 'Status' in df.columns:
        zielony = len(df[df['Status'] == 'Zielony'])
        zolty = len(df[df['Status'] == 'Żółty'])
        czerwony = len(df[df['Status'] == 'Czerwony'])
    else:
        # Fallback jeśli brak Status
        zielony = len(paying_df[paying_df['Wzrost_%_Od_Faktycznej'] <= 10])
        zolty = len(paying_df[(paying_df['Wzrost_%_Od_Faktycznej'] > 10) & (paying_df['Wzrost_%_Od_Faktycznej'] <= 20)])
        czerwony = len(paying_df[paying_df['Wzrost_%_Od_Faktycznej'] > 20])
    
    # Rabat (ile miało 10% rabat)
    z_rabatem = len(df[df['Miał_Rabat_10%'] == 1])
    bez_rabatu = len(df[df['Miał_Rabat_10%'] == 0])
    
    summary = {
        'Liczba_Klientów_Standard': len(standard_df),
        'Liczba_Klientów_VIP': len(vip_df),
        'Liczba_Klientów_FREE': len(free_df),
        'Liczba_Klientów_Razem': len(df),
        
        'Przychod_Przed_PLN': round(przychod_przed, 2),
        'Przychod_Po_PLN': round(przychod_po, 2),
        'Wzrost_PLN': round(wzrost_pln, 2),
        'Wzrost_PCT': round(wzrost_pct, 2),
        
        'Roczny_Przed_PLN': round(roczny_przed, 2),
        'Roczny_Po_PLN': round(roczny_po, 2),
        'Roczny_Wzrost_PLN': round(roczny_wzrost, 2),
        
        'Srednia_Doc_Klienta': round(srednia_doc, 1),
        'Srednia_Cena_Przed': round(srednia_cena_przed, 2),
        'Srednia_Cena_Po': round(srednia_cena_po, 2),
        
        'Zielony_Cnt': zielony,
        'Zolty_Cnt': zolty,
        'Czerwony_Cnt': czerwony,
        
        'Z_Rabatem': z_rabatem,
        'Bez_Rabatu': bez_rabatu,
    }
    
    return summary


def get_alerts(summary: dict) -> list:
    """
    Wygeneruj alerty/sugestie na podstawie summary.
    
    Returns:
        Lista alertów (strings)
    """
    
    alerts = []
    
    # Alert: czerwoni klienci (rzeczywisty wzrost >20%, bez rabatu)
    if summary.get('Czerwony_Cnt', 0) > 0:
        pct_red = (summary.get('Czerwony_Cnt', 0) / (summary.get('Liczba_Klientów_Standard', 0) + summary.get('Liczba_Klientów_VIP', 0))) * 100 if (summary.get('Liczba_Klientów_Standard', 0) + summary.get('Liczba_Klientów_VIP', 0)) > 0 else 0
        alerts.append(f"🔴 {summary.get('Czerwony_Cnt', 0)} klientów ({pct_red:.1f}%) ma wzrost >20% (rzeczywisty wzrost ceny) — RYZYKO!")
        alerts.append(f"💡 Warto im zaproponować:")
        alerts.append(f"   • Rabat za dostarczenie dokumentów do 3. dnia miesiąca")
        alerts.append(f"   • Rabat za płatność faktury w 3 dni")
        alerts.append(f"   • Wniosek o wakacje składkowe w cenie")
    
    # Alert: żółci klienci (wzrost 10-20% LUB >20% ale mieli rabat)
    if summary.get('Zolty_Cnt', 0) > 0:
        pct_yellow = (summary.get('Zolty_Cnt', 0) / (summary.get('Liczba_Klientów_Standard', 0) + summary.get('Liczba_Klientów_VIP', 0))) * 100 if (summary.get('Liczba_Klientów_Standard', 0) + summary.get('Liczba_Klientów_VIP', 0)) > 0 else 0
        alerts.append(f"🟡 {summary.get('Zolty_Cnt', 0)} klientów ({pct_yellow:.1f}%) ma wzrost 10-20% lub >20% ale mieli rabat — wymaga komunikacji")
        alerts.append(f"💡 Wyjaśnić że wzrost wynika z anulowania rabatu za Saldeo, nie podwyżki ceny")
    
    # Zieloni (OK)
    if summary.get('Zielony_Cnt', 0) > 0:
        pct_red = (summary.get('Wzrost_Pow_20_PCT', 0) / (summary.get('Liczba_Klientów_Standard', 0) + summary.get('Liczba_Klientów_VIP', 0))) * 100 if (summary.get('Liczba_Klientów_Standard', 0) + summary.get('Liczba_Klientów_VIP', 0)) > 0 else 0
        alerts.append(f"⚠️ {summary.get('Wzrost_Pow_20_PCT', 0)} klientów ({pct_red:.1f}%) ma wzrost >20% — priorytet komunikacji")
        alerts.append(f"💡 Warto im zaproponować:")
        alerts.append(f"   • Rabat za dostarczenie dokumentów do 3. dnia miesiąca")
        alerts.append(f"   • Rabat za płatność faktury w 3 dni")
        alerts.append(f"   • Wniosek o wakacje składkowe w cenie")
    
    # Alert: FREE klienci
    if summary.get('Liczba_Klientów_FREE', 0) > 0:
        alerts.append(f"🎁 {summary.get('Liczba_Klientów_FREE', 0)} FREE klientów (usługa gratis)")
    
    # Alert: wysokie VIP
    if summary.get('Liczba_Klientów_VIP', 0) > 0:
        alerts.append(f"👑 {summary.get('Liczba_Klientów_VIP', 0)} VIP klientów — indywidualne negocjacje")
    
    # Rekomendacja: średnia wzrostu
    if summary.get('Wzrost_PCT', 0) > 0:
        alerts.append(f"📈 Średni wzrost przychodu: {summary.get('Wzrost_PCT', 0):.1f}% (dobrze!)")
    
    # Informacja: roczny impact
    if summary.get('Roczny_Wzrost_PLN', 0) > 0:
        alerts.append(f"💰 Roczny impact: +{summary.get('Roczny_Wzrost_PLN', 0):,.0f} PLN")
    
    return alerts
