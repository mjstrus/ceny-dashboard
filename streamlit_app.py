"""
Ceny Dashboard - UNIT 0 + UNIT 1 + UNIT 2
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
    import plotly.graph_objects as go
    import plotly.express as px
    
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
    
    st.subheader("Segmentacja Klientów po Kolorach")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🟢 Zielony (OK)",
            summary.get('Zielony_Cnt', 0),
            "Wzrost ≤10%"
        )
    
    with col2:
        st.metric(
            "🟡 Żółty (Wymaga rozmowy)",
            summary.get('Zolty_Cnt', 0),
            "Wzrost 10-20% lub >20% z rabatem"
        )
    
    with col3:
        st.metric(
            "🔴 Czerwony (RYZYKO!)",
            summary.get('Czerwony_Cnt', 0),
            "Wzrost >20% bez rabatu"
        )
    
    # WYKRESY
    st.subheader("📈 Wykresy")
    
    col1, col2 = st.columns(2)
    
    # Wykres 1: Segmentacja (Pie)
    with col1:
        import plotly.graph_objects as go
        
        segments = [summary.get('Zielony_Cnt', 0), summary.get('Zolty_Cnt', 0), summary.get('Czerwony_Cnt', 0)]
        labels = ['🟢 Zielony', '🟡 Żółty', '🔴 Czerwony']
        colors_chart = ['#22c55e', '#eab308', '#ef4444']
        
        fig_seg = go.Figure(data=[go.Pie(labels=labels, values=segments, marker=dict(colors=colors_chart))])
        fig_seg.update_layout(title="Segmentacja Klientów", height=400)
        st.plotly_chart(fig_seg, use_container_width=True)
    
    # Wykres 2: Przychód PRZED vs PO
    with col2:
        fig_rev = go.Figure(data=[
            go.Bar(name='PRZED', x=['Miesięczny', 'Roczny'], y=[summary.get('Przychod_Przed_PLN', 0), summary.get('Roczny_Przed_PLN', 0)], marker_color='#1B2A4A'),
            go.Bar(name='PO', x=['Miesięczny', 'Roczny'], y=[summary.get('Przychod_Po_PLN', 0), summary.get('Roczny_Po_PLN', 0)], marker_color='#E8A000')
        ])
        fig_rev.update_layout(title="Przychód PRZED vs PO", barmode='group', height=400, yaxis_title="PLN")
        st.plotly_chart(fig_rev, use_container_width=True)
    
    # EKSPORT PDF
    st.subheader("📥 Eksport Raportu")
    
    col_export = st.columns(1)[0]
    with col_export:
        if st.button("📄 Generuj i Pobierz PDF", type="primary", use_container_width=True):
            from pdf_reporter import create_summary_report
            
            pdf_bytes = create_summary_report(summary, df_with_prices)
            
            st.download_button(
                label="⬇️ Pobierz PDF",
                data=pdf_bytes,
                file_name=f"Statystyka_Klientów_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    
    st.divider()
    
    # Alerty/Sugestie
    if alerts:
        st.subheader("🎯 Sugestie & Alerty")
        for alert in alerts:
            if alert.startswith("⚠️"):
                st.warning(alert)
            elif alert.startswith("💡"):
                st.info(alert)
            elif alert.startswith("🎁"):
                st.success(alert)
            elif alert.startswith("📈"):
                st.info(alert)
            elif alert.startswith("💰"):
                st.success(alert)
            elif alert.startswith("👑"):
                st.info(alert)
            else:
                st.write(alert)
    
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
    
    **Dwie kolumny wzrostu:**
    - **Wzrost % (z rabatem):** Rzeczywisty wzrost od ceny którą płacili (z uwzględnieniem rabatu)
    - **Wzrost % (gdyby brak rabatu):** Wzrost gdyby nigdy nie mieli rabatu za Saldeo - pokazuje prawdziwy wzrost ceny cennnika
    
    **Przykład:**
    - Klient miał rabat 10%, płacił 900 PLN
    - Nowa cena: 1100 PLN
    - Wzrost z rabatem: (1100-900)/900 = 22%
    - Wzrost bez rabatu: (1100-1000)/1000 = 10% ← to rzeczywisty wzrost ceny
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
st.markdown("**Ceny Dashboard v3.0** | Abacus Centrum | Zatwierdzenie → Wczytywanie → Statystyka → Edycja")
