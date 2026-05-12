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
    # UNIT 2: NOWE CENY (AUTO-KALKULACJA + OVERRIDE)
    # ====================================================================
    
    st.divider()
    st.header("💵 Krok 2: Nowe Ceny")
    
    from calculate_new_prices import calculate_new_prices, get_price_table
    
    # Auto-oblicz ceny
    df_with_prices = calculate_new_prices(st.session_state.df)
    st.session_state.df = df_with_prices
    
    st.info("""
    **Formuła:**
    - Bez rabatu: Cena_Nowa = Cena_Stara × 1.10 (+10%)
    - Z rabatem: Cena_Nowa = Cena_Stara × 1.20 (+10% wzrost + 10% anulowanie rabatu)
    """)
    
    # Pokaż tabelę z auto-kalkulacją
    st.subheader("Ceny (auto-obliczone)")
    df_prices = get_price_table(df_with_prices)
    st.dataframe(df_prices, use_container_width=True, hide_index=True)
    
    # Option: override dla VIP
    st.subheader("✏️ Override dla VIP (opcjonalnie)")
    with st.expander("Edytuj ceny dla konkretnych klientów", expanded=False):
        override_id = st.number_input("ID klienta do edycji", min_value=1)
        if override_id in st.session_state.df['ID'].values:
            override_price = st.number_input(
                f"Nowa cena dla ID {override_id}",
                value=float(st.session_state.df[st.session_state.df['ID'] == override_id]['Cena_Nowa'].values[0]),
                step=10.0
            )
            if st.button(f"✓ Zatwierdź dla ID {override_id}"):
                st.session_state.df.loc[st.session_state.df['ID'] == override_id, 'Cena_Nowa'] = override_price
                st.success(f"✓ Zaktualizowano!")
                st.rerun()
        else:
            st.warning(f"ID {override_id} nie znalezione")
    
    st.success("✓ Ceny gotowe. Unit 3 (Analiza Wpływu) wkrótce...")

else:
    st.warning("Wczytaj dane aby kontynuować")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("**Ceny Dashboard v1.0 (Simplified)** | Abacus Centrum")
