"""
Ceny Dashboard — SIMPLIFIED VERSION
Tylko Unit 1 (import) + Unit 2 (input cen)
"""

import streamlit as st
import pandas as pd
import os
import pathlib
from data_loader import load_excel_file, get_display_dataframe

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Ceny Dashboard",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Dashboard Ujednolicenia Cen")
st.markdown("Abacus Centrum | Walidacja nowych cen")

# ============================================================================
# SESSION STATE
# ============================================================================

if 'df' not in st.session_state:
    st.session_state.df = None

if 'new_prices' not in st.session_state:
    st.session_state.new_prices = {
        'Kh_vat': 500,
        'Kh_no_vat': 400,
        'KPIR_vat': 350,
        'KPIR_no_vat': 280,
        'Ryczalt_vat': 600,
        'Ryczalt_no_vat': 480,
    }

# ============================================================================
# UNIT 1: WCZYTANIE DANYCH
# ============================================================================

st.header("📥 Krok 1: Wczytaj Dane")

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
        st.metric("Śr. cena", f"{avg_price:.0f} PLN")
    with col3:
        avg_doc = st.session_state.df['Doc_Avg'].mean()
        st.metric("Śr. dokumentów/mc", f"{avg_doc:.1f}")
    
    # Tabela
    df_display = get_display_dataframe(st.session_state.df)
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # ====================================================================
    # UNIT 2: NOWE CENY
    # ====================================================================
    
    st.divider()
    st.header("💵 Krok 2: Nowe Ceny")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Kh")
        st.session_state.new_prices['Kh_vat'] = st.number_input("Kh z VAT", value=500, step=10)
        st.session_state.new_prices['Kh_no_vat'] = st.number_input("Kh bez VAT", value=400, step=10)
    
    with col2:
        st.subheader("KPIR")
        st.session_state.new_prices['KPIR_vat'] = st.number_input("KPIR z VAT", value=350, step=10)
        st.session_state.new_prices['KPIR_no_vat'] = st.number_input("KPIR bez VAT", value=280, step=10)
    
    with col3:
        st.subheader("Ryczałt")
        st.session_state.new_prices['Ryczalt_vat'] = st.number_input("Ryczałt z VAT", value=600, step=10)
        st.session_state.new_prices['Ryczalt_no_vat'] = st.number_input("Ryczałt bez VAT", value=480, step=10)
    
    st.info("✓ Ceny ustawione. Dashboard v1.0 (simplified) — Units 3-6 będą w następnej iteracji")

else:
    st.warning("Wczytaj dane aby kontynuować")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("**Ceny Dashboard v1.0 (Simplified)** | Abacus Centrum")
