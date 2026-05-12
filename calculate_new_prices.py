"""
Ceny Dashboard — EDYTOWALNA TABELA
Unit 1: Import danych
Unit 2: Edycja cen (VIP/Standard, Cena_Docelowa)
"""

import streamlit as st
import pandas as pd
import os
import pathlib
from data_loader import load_excel_file, get_display_dataframe
from calculate_new_prices import calculate_new_prices, get_price_table

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Ceny Dashboard",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Dashboard Ujednolicenia Cen")
st.markdown("Abacus Centrum | Edycja cen dla klientów")

# ============================================================================
# SESSION STATE
# ============================================================================

if 'df' not in st.session_state:
    st.session_state.df = None

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
    st.header("💵 Krok 2: Edycja Cen")
    
    st.info("""
    **Cena_Docelowa dla WSZYSTKICH: Cennik + 10%** (Cena_Stara × 1.10)
    
    Ale to oznacza RÓŻNE rzeczy:
    - **Bez rabatu:** Płacili 100 → Będą 110 (+10%)
    - **Z rabatem:** Płacili 90 → Będą 110 (+22%, bo likwidacja rabatu + wzrost)
    
    **Edytuj kolumny:**
    - 👑 Grupa Klienta: VIP / Standard
    - 💰 Nowa Cena: zmień ręcznie dla VIP
    """)
    
    # Auto-oblicz ceny
    df_with_prices = calculate_new_prices(st.session_state.df)
    
    # Przygotuj tabelę do edycji
    df_editable = get_price_table(df_with_prices)
    
    # EDYTOWALNA TABELA
    st.subheader("Edytuj tabele poniżej")
    
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
        # Zaitegruj zmiany z oryginalnym DataFrame
        for idx, row in edited_df.iterrows():
            client_id = row['ID']
            st.session_state.df.loc[st.session_state.df['ID'] == client_id, 'Grupa_Klienta'] = row['👑 Grupa Klienta']
            st.session_state.df.loc[st.session_state.df['ID'] == client_id, 'Cena_Docelowa'] = row['💰 Nowa Cena']
        
        st.success("✓ Zmiany zatwierdzone!")
        st.info(f"📊 {len(edited_df)} klientów zaktualizowano")
    
    st.divider()
    st.success("✓ Gotowe! Możesz teraz wyeksportować raport lub kontynuować edycję.")

else:
    st.warning("📥 Wczytaj dane aby kontynuować")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("**Ceny Dashboard v2.0** | Abacus Centrum | Edytowalna tabela")
