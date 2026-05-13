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

st.title("💰 Dashboard Ujednolicenia Cen")
st.markdown("Abacus Centrum | Unit 0 → 1 → 2")

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

st.header("📋 Unit 0: Cennik 2026")

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

st.header("📥 Unit 1: Wczytaj Dane Klientów")

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
    # UNIT 2: EDYCJA CEN (EDYTOWALNA TABELA)
    # ====================================================================
    
    st.divider()
    st.header("💵 Unit 2: Edycja Cen Klientów")
    
    st.info("""
    **Cena_Docelowa = NOWY CENNIK z Unit 0** (na podstawie Typ + VAT + Doc_Avg)
    
    **Porównanie:**
    - **Płacili:** Cena_Stara (lub Cena_Stara × 0.90 jeśli miał rabat)
    - **Będą płacić:** Cena_Docelowa (z Unit 0 cennnika + widełki)
    - **Wzrost:** różnica (zależy od rabatu + zakresu dokumentów)
    
    **Przykład:**
    - Bez rabatu, 15 doc → grupa 11-20 → cena z Unit 0 dla 11-20
    - Z rabatem, 50 doc → grupa 21-50 → cena z Unit 0 dla 21-50 (koniec rabatu!)
    """)
    
    # Auto-oblicz ceny (na podstawie cennnika z Unit 0)
    df_with_prices = calculate_new_prices(st.session_state.df, st.session_state.pricing_df)
    
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
                options=["Standard", "VIP"],
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
        # Zaintegruj zmiany z oryginalnym DataFrame
        for idx, row in edited_df.iterrows():
            client_id = row['ID']
            st.session_state.df.loc[st.session_state.df['ID'] == client_id, 'Grupa_Klienta'] = row['👑 Grupa Klienta']
            st.session_state.df.loc[st.session_state.df['ID'] == client_id, 'Cena_Docelowa'] = row['💰 Nowa Cena']
        
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
st.markdown("**Ceny Dashboard v3.0** | Abacus Centrum | Unit 0→1→2")
