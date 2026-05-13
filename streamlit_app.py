"""
Ceny Dashboard — UNIT 0 + UNIT 1 + UNIT 2
Unit 0: Zarządzanie cennikiem
Unit 1: Import danych klientów
Unit 2: Edycja cen
"""

import streamlit as st
import pandas as pd
import os
import pathlib
from data_loader import load_excel_file, get_display_dataframe
from calculate_new_prices import calculate_new_prices, get_price_table
from price_manager import get_default_pricing, apply_global_modification, apply_global_all_modification, get_pricing_summary

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Ceny Dashboard",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Dashboard Zarządzania Cennikiem")
st.markdown("Abacus Centrum | Zatwierdzenie → Wczytywanie → Statystyka → Edycja")

# ============================================================================
# SESSION STATE
# ============================================================================

if 'pricing_df' not in st.session_state:
    st.session_state.pricing_df = get_default_pricing()

if 'df' not in st.session_state:
    st.session_state.df = None

# ============================================================================
# UNIT 0: ZARZĄDZANIE CENNIKIEM
# ============================================================================

st.header("📋 Zatwierdzenie cennika")

st.info(get_pricing_summary(st.session_state.pricing_df))

# Edytowalna tabela cennnika
st.subheader("Edytuj cennik poniżej")

edited_pricing = st.data_editor(
    st.session_state.pricing_df,
    use_container_width=True,
    hide_index=True,
    key="pricing_editor",
    column_config={
        "Typ": st.column_config.SelectboxColumn(
            "Typ",
            options=["KH", "KPIR", "Ryczałt"],
            required=True
        ),
        "VAT": st.column_config.SelectboxColumn(
            "VAT",
            options=["tak", "nie"],
            required=True
        ),
        "1-10": st.column_config.NumberColumn("1-10", step=1.0, format="%.2f"),
        "11-20": st.column_config.NumberColumn("11-20", step=1.0, format="%.2f"),
        "21-50": st.column_config.NumberColumn("21-50", step=1.0, format="%.2f"),
        "51-100": st.column_config.NumberColumn("51-100", step=1.0, format="%.2f"),
        "Paczka 25 (100+)": st.column_config.NumberColumn("Paczka 25", step=1.0, format="%.2f"),
    }
)

# Modyfikacje globalne
st.subheader("⚙️ Modyfikacje Globalne")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Zmień całą kategorię**")
    mod_typ = st.selectbox("Typ", ["KH", "KPIR", "Ryczałt"], key="mod_typ")
    mod_vat = st.selectbox("VAT", ["tak", "nie"], key="mod_vat")
    mod_percent = st.number_input("Zmiana %", value=0.0, step=1.0, key="mod_percent")
    
    if st.button("✓ Zastosuj dla tej kategorii"):
        edited_pricing = apply_global_modification(edited_pricing, mod_typ, mod_vat, mod_percent)
        st.success(f"✓ {mod_typ} {mod_vat}: {mod_percent:+.1f}%")

with col2:
    st.markdown("**Zmień wszystko**")
    all_percent = st.number_input("Zmiana % dla WSZYSTKIEGO", value=0.0, step=1.0, key="all_percent")
    
    if st.button("✓ Zastosuj dla całego cennnika"):
        edited_pricing = apply_global_all_modification(edited_pricing, all_percent)
        st.success(f"✓ Całość: {all_percent:+.1f}%")

with col3:
    st.markdown("**Reset**")
    if st.button("🔄 Przywróć domyślny cennik"):
        edited_pricing = get_default_pricing()
        st.success("✓ Cennik przywrócony")

# ============================================================================
# BUTTON: ZATWIERDŹ CENNIK
# ============================================================================

st.divider()

if st.button("✅ ZATWIERDŹ CENNIK I PRZEJDŹ DO KLIENTÓW", type="primary", use_container_width=True):
    st.session_state.pricing_df = edited_pricing
    st.success("✓ Cennik zatwierddzony! Przejdź do Unit 1")

st.divider()

# ============================================================================
# UNIT 1: WCZYTANIE DANYCH KLIENTÓW
# ============================================================================

st.header("📥 Wczytywanie danych klientów")

col1, col2 = st.columns([2, 1])

with col1:
    load_method = st.radio(
        "Opcje:",
        ["📂 Dane przykładowe (demo)", "📤 Wczytaj plik Excel"],
        horizontal=True
    )

with col2:
    if st.button("🔄 Odśwież"):
        st.session_state.df = None
        st.rerun()

# Wczytaj dane
if load_method == "📂 Dane przykładowe (demo)":
    current_dir = pathlib.Path(__file__).parent
    sample_path = current_dir / 'sample_data' / 'master_clients_sample.xlsx'
    
    if sample_path.exists():
        df, errors = load_excel_file(str(sample_path))
        if not errors:
            st.session_state.df = df
            st.success(f"✓ Wczytano {len(df)} klientów (demo data)")
        else:
            st.error(f"Błąd: {errors}")
    else:
        st.error(f"Nie znaleziono: {sample_path}")

else:  # Upload Excel
    uploaded_file = st.file_uploader("Wybierz .xlsx", type=['xlsx'])
    if uploaded_file is not None:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name
        
        df, errors = load_excel_file(tmp_path)
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        if errors:
            st.error(f"Błąd: {errors}")
        else:
            st.session_state.df = df
            st.success(f"✓ Wczytano {len(df)} klientów")

# ============================================================================
# POKAZ DANE
# ============================================================================

if st.session_state.df is not None:
    st.divider()
    
    st.subheader("📊 Wczytane Dane")
    
    # Metryki
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Liczba klientów", len(st.session_state.df))
    with col2:
        avg_price = st.session_state.df['Cena_Stara'].mean()
        st.metric("Śr. cena (cennik)", f"{avg_price:.0f} PLN")
    with col3:
        avg_doc = st.session_state.df['Doc_Avg'].mean()
        st.metric("Śr. dokumentów/mc", f"{avg_doc:.1f}")
    
    # Tabela wczytanych danych
    df_display = get_display_dataframe(st.session_state.df)
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # ====================================================================
    # OBLICZ CENY (dla Unit 3 i Unit 2)
    # ====================================================================
    
    df_with_prices = calculate_new_prices(st.session_state.df, st.session_state.pricing_df)
    
    # ====================================================================
    # UNIT 3: PODSUMOWANIE (SUMMARY DASHBOARD)
    # ====================================================================
    
    st.divider()
    st.header("📊 Statystyka wgranej listy klientów")
    
    from summary_generator import generate_summary, get_alerts
    
    # Oblicz summary
    summary = generate_summary(df_with_prices)
    alerts = get_alerts(summary)
    
    # Karty metryczne
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Liczba Klientów",
            summary.get('Liczba_Klientów_Razem', 0),
            f"Standard: {summary.get('Liczba_Klientów_Standard', 0)}"
        )
    
    with col2:
        st.metric(
            "VIP",
            summary.get('Liczba_Klientów_VIP', 0),
            f"FREE: {summary.get('Liczba_Klientów_FREE', 0)}"
        )
    
    with col3:
        st.metric(
            "Średnia Docs/Klient",
            f"{summary.get('Srednia_Doc_Klienta', 0):.1f}",
            f"Cena przed: {summary.get('Srednia_Cena_Przed', 0):.0f} PLN"
        )
    
    with col4:
        st.metric(
            "Średnia Cena Po",
            f"{summary.get('Srednia_Cena_Po', 0):.0f} PLN",
            f"Wzrost: {summary.get('Wzrost_PCT', 0):.1f}%"
        )
    
    # Finansowe
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Przychód PRZED (mc)",
            f"{summary.get('Przychod_Przed_PLN', 0):,.0f} PLN",
            f"Rocznie: {summary.get('Roczny_Przed_PLN', 0):,.0f} PLN"
        )
    
    with col2:
        st.metric(
            "Przychód PO (mc)",
            f"{summary.get('Przychod_Po_PLN', 0):,.0f} PLN",
            f"Rocznie: {summary.get('Roczny_Po_PLN', 0):,.0f} PLN"
        )
    
    with col3:
        st.metric(
            "Wzrost (mc)",
            f"+{summary.get('Wzrost_PLN', 0):,.0f} PLN",
            f"Roczny impact: +{summary.get('Roczny_Wzrost_PLN', 0):,.0f} PLN"
        )
    
    # Segmentacja wzrostu
    st.subheader("Segmentacja Klientów po Wzroście")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Wzrost ≤10% (OK)",
            summary.get('Wzrost_Do_10_PCT', 0),
            "Łatwa komunikacja"
        )
    
    with col2:
        st.metric(
            "Wzrost 10-20% (ŻÓŁTY)",
            summary.get('Wzrost_10_20_PCT', 0),
            "Wymaga dyskusji"
        )
    
    with col3:
        st.metric(
            "Wzrost >20% (RYZYKO)",
            summary.get('Wzrost_Pow_20_PCT', 0),
            "Priorytet komunikacji!"
        )
    
    # Alerty/Sugestie
    if alerts:
        st.subheader("🎯 Sugestie & Alerty")
        for alert in alerts:
            st.info(alert)
    
    # ====================================================================
    # UNIT 2: EDYCJA CEN (EDYTOWALNA TABELA)
    # ====================================================================
    
    st.divider()
    st.header("💵 Edycja cen klientów")
    
    st.info("""
    **Cena_Docelowa = NOWY CENNIK** (ze sekcji "Zatwierdzenie cennika")
    
    **Cena_Docelowa liczony na podstawie:** Typ + VAT + Liczba dokumentów
    
    **Grupy klientów:**
    - **Standard:** cena z cennnika
    - **VIP:** cena edytowalna (negocjacje)
    - **FREE:** 0 PLN (gratis dla zaprzyjaźnionych)
    
    **Porównanie:**
    - **Płacili (mc):** Cena_Faktyczna (Cena_Stara lub Cena_Stara × 0.90 jeśli miał rabat)
    - **Będą płacić (mc):** Cena_Docelowa (z cennnika + widełki)
    - **Wzrost:** różnica (zależy od rabatu + zakresu dokumentów)
    """)
    
    # Przygotuj tabelę do edycji
    df_editable = get_price_table(df_with_prices)
    
    # EDYTOWALNA TABELA
    st.subheader("Edytuj tabelę poniżej")
    
    edited_df = st.data_editor(
        df_editable,
        use_container_width=True,
        hide_index=True,
        key="price_editor",
        column_config={
            "👑 Grupa Klienta": st.column_config.SelectboxColumn(
                "Grupa",
                options=["Standard", "VIP", "FREE"],
                required=True
            ),
            "💰 Nowa Cena": st.column_config.NumberColumn(
                "Nowa Cena",
                min_value=0,
                step=1.0,
                format="%.2f"
            ),
        }
    )
    
    # Button: Zatwierdź zmiany
    if st.button("✅ Zatwierdź wszystkie zmiany", type="primary"):
        # Mapping: zmień nazwy emoji na oryginalne
        column_mapping = {
            '👑 Grupa Klienta': 'Grupa_Klienta',
            '💰 Nowa Cena (Unit 0)': 'Cena_Docelowa'
        }
        
        # Zaintegruj zmiany z oryginalnym DataFrame
        for idx, row in edited_df.iterrows():
            client_id = row['ID']
            # Grupa_Klienta
            st.session_state.df.loc[st.session_state.df['ID'] == client_id, 'Grupa_Klienta'] = row['👑 Grupa Klienta']
            # Cena_Docelowa
            st.session_state.df.loc[st.session_state.df['ID'] == client_id, 'Cena_Docelowa'] = row['💰 Nowa Cena (Unit 0)']
        
        st.success("✓ Zmiany zatwierdzone!")
        st.info(f"📊 {len(edited_df)} klientów zaktualizowano")
    
    st.divider()
    st.success("✓ Gotowe! Dashboard ready.")

else:
    st.warning("📥 Wczytaj dane aby kontynuować Unit 2")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("**Ceny Dashboard v3.0** | Abacus Centrum | Zatwierdzenie → Wczytywanie → Statystyka → Edycja")
