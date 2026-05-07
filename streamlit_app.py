"""
Ceny Dashboard — Streamlit App
Dashboard do ujednolicenia cen dla ~200 klientów Abacus Centrum.

Funkcjonalność:
- Unit 1: Wczytanie danych historycznych (stare ceny + dokumenty)
- Unit 2: Input nowych cen (6 typów)
- Unit 3: Kalkulacja wpływu ceny
- Unit 4: Risk Assessment & Segmentacja
- Unit 5: Wizualizacja & Tabele
- Unit 6: Export & Raportowanie
"""

import streamlit as st
import pandas as pd
import os
from data_loader import load_excel_file, get_display_dataframe

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================

st.set_page_config(
    page_title="Ceny Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS — Abacus styling (Navy + Gold)
st.markdown("""
<style>
    :root {
        --navy: #1B2A4A;
        --gold: #E8A000;
        --light-gray: #F5F5F5;
    }
    
    .header-title {
        color: white;
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2d45 100%);
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .metric-card {
        background: #F5F5F5;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #E8A000;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = None
    st.session_state.df_raw = None

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
# HEADER
# ============================================================================

st.markdown("""
<div class="header-title">
    <h1>💰 Dashboard Ujednolicenia Cen</h1>
    <p>Walidacja nowych cen • Ocena ryzyka retencji • Planowanie wdrażania</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# UNIT 1: DATA INPUT & LOADING
# ============================================================================

st.header("📥 Krok 1: Wczytaj Dane")

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Opcje wczytania:")
    
    load_method = st.radio(
        "Gdzie są dane?",
        ["📤 Wczytaj plik Excel", "📂 Użyj przykładowych danych (dev)"],
        horizontal=True,
        label_visibility="collapsed"
    )

with col2:
    if st.button("🔄 Odśwież", help="Przeładuj dane"):
        st.session_state.data_loaded = False
        st.session_state.df = None
        st.session_state.df_raw = None
        st.rerun()

# Load data based on method
if load_method == "📤 Wczytaj plik Excel":
    uploaded_file = st.file_uploader(
        "Wybierz plik .xlsx z danymi klientów",
        type=['xlsx'],
        help="Format: ID, Nazwa, Typ_Umowy, VAT, Cena_Bazowa, Doc_Marzec, Doc_Kwiecien, Doc_Maj, Czy_Rabat"
    )
    
    if uploaded_file is not None:
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            
            df, errors = load_excel_file(tmp_path)
            
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.session_state.data_loaded = True
                st.session_state.df = df
                st.session_state.df_raw = df.copy()
                st.success(f"✓ Wczytano {len(df)} klientów")
                st.rerun()
        except Exception as e:
            st.error(f"❌ Błąd: {str(e)}")

else:  # Use sample data
    sample_path = 'sample_data/master_clients_sample.xlsx'
    if os.path.exists(sample_path):
        df, errors = load_excel_file(sample_path)
        if not errors:
            st.session_state.data_loaded = True
            st.session_state.df = df
            st.session_state.df_raw = df.copy()
            st.info(f"📂 Dane przykładowe wczytane: {len(df)} klientów")
        else:
            for error in errors:
                st.error(error)
    else:
        st.error(f"Nie znaleziono pliku: {sample_path}")

# ============================================================================
# DISPLAY LOADED DATA
# ============================================================================

if st.session_state.data_loaded and st.session_state.df is not None:
    st.divider()
    
    st.subheader("📊 Podgląd Wczytanych Danych")
    
    df_display = get_display_dataframe(st.session_state.df)
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Liczba klientów", len(df_display))
    with col2:
        st.metric("Przychód dzisiaj (mc)", f"${st.session_state.df['Cena_Bazowa'].sum() * st.session_state.df['Doc_Avg'].mean():,.0f}")
    with col3:
        rabat_clients = (st.session_state.df['Czy_Rabat'] == 1).sum()
        st.metric("Klienci z rabatem", f"{rabat_clients} ({rabat_clients/len(df_display)*100:.0f}%)")
    with col4:
        avg_doc = st.session_state.df['Doc_Avg'].mean()
        st.metric("Śr. dokumentów/mc", f"{avg_doc:.1f}")
    
    # Table
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # ====================================================================
    # UNIT 2: INPUT NOWYCH CEN
    # ====================================================================
    
    st.divider()
    st.header("💵 Krok 2: Ustaw Nowe Ceny")
    
    st.info("""
    **Plan komunikacji:**
    - Wszyscy klienci wiedzą o ~10% podwyżce
    - Część traci rabat 10% (za tool do FV)
    - Razem nie powinno być > 20% (limit tolerancji)
    """)
    
    # Create input fields for 6 price types
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Kh")
        st.session_state.new_prices['Kh_vat'] = st.number_input(
            "Kh z VAT (PLN)",
            value=st.session_state.new_prices['Kh_vat'],
            min_value=0,
            step=10,
            key='kh_vat'
        )
        st.session_state.new_prices['Kh_no_vat'] = st.number_input(
            "Kh bez VAT (PLN)",
            value=st.session_state.new_prices['Kh_no_vat'],
            min_value=0,
            step=10,
            key='kh_no_vat'
        )
    
    with col2:
        st.subheader("KPIR")
        st.session_state.new_prices['KPIR_vat'] = st.number_input(
            "KPIR z VAT (PLN)",
            value=st.session_state.new_prices['KPIR_vat'],
            min_value=0,
            step=10,
            key='kpir_vat'
        )
        st.session_state.new_prices['KPIR_no_vat'] = st.number_input(
            "KPIR bez VAT (PLN)",
            value=st.session_state.new_prices['KPIR_no_vat'],
            min_value=0,
            step=10,
            key='kpir_no_vat'
        )
    
    with col3:
        st.subheader("Ryczałt")
        st.session_state.new_prices['Ryczalt_vat'] = st.number_input(
            "Ryczałt z VAT (PLN)",
            value=st.session_state.new_prices['Ryczalt_vat'],
            min_value=0,
            step=10,
            key='ryczalt_vat'
        )
        st.session_state.new_prices['Ryczalt_no_vat'] = st.number_input(
            "Ryczałt bez VAT (PLN)",
            value=st.session_state.new_prices['Ryczalt_no_vat'],
            min_value=0,
            step=10,
            key='ryczalt_no_vat'
        )
    
    # Show price comparison
    st.subheader("Porównanie: Stare vs Nowe")
    
    price_comparison = []
    for typ, vat in [('Kh', 'z VAT'), ('Kh', 'bez VAT'), 
                      ('KPIR', 'z VAT'), ('KPIR', 'bez VAT'),
                      ('Ryczałt', 'z VAT'), ('Ryczałt', 'bez VAT')]:
        # Find old price from data
        old_price_data = st.session_state.df[
            (st.session_state.df['Typ_Umowy'] == typ) & 
            (st.session_state.df['VAT'] == vat)
        ]
        old_price = old_price_data['Cena_Bazowa'].mean() if not old_price_data.empty else 0
        
        # Get new price
        key = typ.replace('Ryczałt', 'Ryczalt') + ('_vat' if 'VAT' in vat else '_no_vat')
        new_price = st.session_state.new_prices[key]
        
        change_pct = ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
        
        price_comparison.append({
            'Typ': f"{typ} {vat}",
            'Stara Cena': f"{old_price:.0f} PLN",
            'Nowa Cena': f"{new_price:.0f} PLN",
            'Zmiana': f"+{change_pct:.1f}%" if change_pct >= 0 else f"{change_pct:.1f}%"
        })
    
    df_comparison = pd.DataFrame(price_comparison)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)
    
    # ====================================================================
    # UNIT 3: PRICE IMPACT CALCULATION
    # ====================================================================
    
    st.divider()
    st.header("📊 Krok 3: Analiza Wpływu Ceny")
    
    # Import calculator
    from calculator import calculate_price_impact, segment_clients, get_segment_summary, get_revenue_impact, get_display_dataframe as get_calc_display
    
    # Oblicz wpływ
    df_impact = calculate_price_impact(st.session_state.df, st.session_state.new_prices)
    df_impact = segment_clients(df_impact)
    
    # Podsumowanie segmentów
    segment_summary = get_segment_summary(df_impact)
    revenue_impact = get_revenue_impact(df_impact)
    
    # Wyświetl metryki przychodu
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Przychód dzisiaj (mc)",
            f"${revenue_impact['revenue_old_monthly']:,.0f}",
            help="Suma przychodu (cena × dokumenty) dla wszystkich klientów"
        )
    
    with col2:
        st.metric(
            "Przychód docelowy (mc)",
            f"${revenue_impact['revenue_new_monthly']:,.0f}",
            delta=f"${revenue_impact['impact_pln_monthly']:,.0f}",
            help="Po zmianach cen"
        )
    
    with col3:
        impact_pct = revenue_impact['impact_pct']
        st.metric(
            "Wzrost przychodu",
            f"+{impact_pct:.1f}%",
            help=f"Moc zmian: +${revenue_impact['impact_pln_annual']:,.0f} rocznie"
        )
    
    with col4:
        total_clients = len(df_impact)
        red_count = len(df_impact[df_impact['Segment'] == '🔴 Czerwony'])
        st.metric(
            "Zagrożeni (> 20%)",
            f"{red_count}/{total_clients}",
            delta=f"{red_count/total_clients*100:.0f}%",
            delta_color="inverse"
        )
    
    # Segmentacja — Pie Chart
    segment_dist = df_impact['Segment'].value_counts()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Wizualizacja segmentów (tekst + bar)
        st.subheader("Rozkład Segmentów")
        
        for segment in ['🟢 Zielony', '🟡 Żółty', '🔴 Czerwony']:
            if segment in segment_summary:
                info = segment_summary[segment]
                count = info['count']
                pct = info['count_pct']
                
                # Progress bar
                col_label, col_bar = st.columns([1, 3])
                with col_label:
                    st.write(f"{segment}")
                with col_bar:
                    st.progress(pct / 100, text=f"{count} klientów ({pct:.0f}%)")
    
    with col2:
        st.subheader("Stats per Segment")
        
        segment_stats = []
        for segment, info in segment_summary.items():
            segment_stats.append({
                'Segment': segment,
                'Liczba': info['count'],
                'Śr. Wpływ %': f"{info['avg_impact_pct']:.1f}%",
                'Razem Wpływ': f"${info['total_impact_pln']:,.0f}"
            })
        
        df_stats = pd.DataFrame(segment_stats)
        st.dataframe(df_stats, use_container_width=True, hide_index=True)
    
    # Tabela szczegółowa — posortowana po wpływie (descending)
    st.subheader("Szczegóły Klientów (posortowane po wpływie)")
    
    df_display_calc = get_calc_display(df_impact)
    
    # Sortowanie: Czerwoni na górze (największy wpływ)
    df_display_calc['Sort_Key'] = df_display_calc['Wpływ %'].astype(float)
    df_display_calc = df_display_calc.sort_values('Sort_Key', ascending=False).drop('Sort_Key', axis=1)
    
    # Kolory dla segmentów (conditional)
    # Note: Streamlit dataframe nie ma full conditional formatting, więc robimy HTML
    st.dataframe(df_display_calc, use_container_width=True, hide_index=True)
    
    # Filter + Search
    st.subheader("🔎 Filtruj Klientów")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        segment_filter = st.multiselect(
            "Segment",
            ['🟢 Zielony', '🟡 Żółty', '🔴 Czerwony'],
            default=['🟢 Zielony', '🟡 Żółty', '🔴 Czerwony']
        )
    
    with col2:
        typ_filter = st.multiselect(
            "Typ umowy",
            df_impact['Typ_Umowy'].unique(),
            default=df_impact['Typ_Umowy'].unique()
        )
    
    with col3:
        search = st.text_input("Szukaj (nazwa)")
    
    # Zastosuj filtry
    df_filtered = df_impact[
        (df_impact['Segment'].isin(segment_filter)) &
        (df_impact['Typ_Umowy'].isin(typ_filter)) &
        (df_impact['Nazwa'].str.contains(search, case=False, na=False) | (search == ''))
    ]
    
    st.write(f"**{len(df_filtered)} klientów** (z {len(df_impact)})")
    
    df_display_filtered = get_calc_display(df_filtered)
    st.dataframe(df_display_filtered, use_container_width=True, hide_index=True)
    
    # Store calculated data in session state for Unit 4-6
    st.session_state.df_impact = df_impact
    st.session_state.segment_summary = segment_summary
    st.session_state.revenue_impact = revenue_impact
    
    # ====================================================================
    # UNIT 4 & 5: WIZUALIZACJE
    # ====================================================================
    
    st.divider()
    st.header("📈 Krok 4: Wizualizacje & Analiza")
    
    from visualizations import (
        create_segment_pie_chart,
        create_impact_histogram,
        create_revenue_comparison,
        create_by_type_comparison,
        create_segment_details_table,
        create_threat_summary
    )
    
    # Wykresy w dwóch kolumnach
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_segment_pie_chart(df_impact), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_impact_histogram(df_impact), use_container_width=True)
    
    # Przychód: porównanie
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_revenue_comparison(revenue_impact), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_by_type_comparison(df_impact), use_container_width=True)
    
    # ====================================================================
    # TABELE SZCZEGÓŁOWE
    # ====================================================================
    
    st.divider()
    st.header("📋 Podsumowanie per Segment")
    
    df_segment_details = create_segment_details_table(segment_summary, revenue_impact)
    st.dataframe(df_segment_details, use_container_width=True, hide_index=True)
    
    # Klienci zagrożeni (Czerwoni i Żółci)
    st.divider()
    st.header("⚠️ Klienci Zagrożeni (> 10% wzrost)")
    
    df_threat = create_threat_summary(df_impact)
    
    if not df_threat.empty:
        st.warning(f"**{len(df_threat)} klientów wymaga uwagi** (Żółci i Czerwoni)")
        st.dataframe(df_threat, use_container_width=True, hide_index=True)
        
        # Stats zagrożonych
        red_count = len(df_impact[df_impact['Segment'] == '🔴 Czerwony'])
        yellow_count = len(df_impact[df_impact['Segment'] == '🟡 Żółty'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🟡 Żółci", yellow_count, f"{yellow_count/len(df_impact)*100:.0f}% klientów")
        with col2:
            st.metric("🔴 Czerwoni", red_count, f"{red_count/len(df_impact)*100:.0f}% klientów (priorytet)")
        with col3:
            total_threat_impact = df_threat['Wpływ %'].apply(lambda x: float(x.rstrip('%'))).sum()
            st.metric("Razem Wpływ", f"+{total_threat_impact:.0f}%")
    else:
        st.success("✓ Wszyscy klienci OK (wzrost ≤ 10%)")
    
    # ====================================================================
    # UNIT 6: EXPORT
    # ====================================================================
    
    st.divider()
    st.header("💾 Krok 5: Export & Raportowanie")
    
    from exporter import export_to_excel, export_to_csv, get_markdown_report
    from datetime import datetime
    
    # Przygotuj export
    excel_buffer = export_to_excel(df_impact, segment_summary, revenue_impact)
    csv_data = export_to_csv(df_impact)
    markdown_report = get_markdown_report(segment_summary, revenue_impact, len(df_threat))
    
    # Download buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📥 Excel Report",
            data=excel_buffer,
            file_name=f"plan_wdrazania_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="3 arkusze: Clients, Summary, By_Segment"
        )
    
    with col2:
        st.download_button(
            label="📄 CSV Export",
            data=csv_data,
            file_name=f"plan_wdrazania_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
            help="Szczegóły wszystkich klientów"
        )
    
    with col3:
        st.download_button(
            label="📝 Markdown Report",
            data=markdown_report,
            file_name=f"plan_wdrazania_{datetime.now().strftime('%Y-%m-%d')}.md",
            mime="text/markdown",
            help="Raport do kopiowania/edycji"
        )
    
    # Podgląd Markdown report
    st.subheader("📝 Raport Tekstowy")
    
    with st.expander("📖 Pokaż raport (Markdown)", expanded=False):
        st.markdown(markdown_report)
    
    # ====================================================================
    # CHECKLIST WDRAŻANIA
    # ====================================================================
    
    st.divider()
    st.header("✅ Checklist Wdrażania")
    
    checklist = f"""
    ## Przygotowanie
    - [ ] Zatwierdzić nowe ceny (6 typów)
    - [ ] Zatwierdzić threshold 20% (limit tolerancji)
    - [ ] Przygotować szablon komunikacji dla każdego segmentu
    
    ## Fala 1: 🟢 Zieloni ({len(df_impact[df_impact['Segment'] == '🟢 Zielony'])} klientów)
    - [ ] Wysłać notę o zmianach (~10% wzrost)
    - [ ] Bez negocjacji
    
    ## Fala 2: 🟡 Żółci ({yellow_count} klientów)
    - [ ] Indywidualny kontakt
    - [ ] Wyjaśnić: wzrost ceny + anulowanie rabatu
    - [ ] Być gotowym do pytań
    
    ## Fala 3: 🔴 Czerwoni ({red_count} klientów) — PRIORYTET
    - [ ] Kontakt osobiście
    - [ ] Propozycja alternatywy (np. inny typ umowy)
    - [ ] Negocjacja jeśli trzeba
    - [ ] Risk mitigation: nie stracić klienta
    
    ## Implementacja
    - [ ] Zmiana cen w Enova365 / Symfonia
    - [ ] Aktualizacja master cennika w systemach
    - [ ] Test z pilotażem (1-2 faktury)
    - [ ] Go live
    
    ## Follow-up
    - [ ] Tracking rezygnacji (monitor)
    - [ ] Post-implementacja review (miesiąc 1)
    - [ ] Adjustments jeśli potrzeba
    """
    
    st.markdown(checklist)
    
    # ====================================================================
    # PODSUMOWANIE
    # ====================================================================
    
    st.divider()
    st.success("""
    ✅ **Dashboard Kompletny!**
    
    ### Następne kroki:
    1. ✓ Exportuj raport (Excel, CSV, Markdown)
    2. ✓ Przejrzyj zagrożonych klientów
    3. → Przygotuj komunikację per segment
    4. → Wdrażaj Falami 1, 2, 3
    5. → Monitor i adjustuj
    """)
    
    st.info("""
    **💡 Tips:**
    - Exportuj raport codziennie (trackowanie zmian)
    - Zmień ceny w Unit 2 i sprawdź impact w real-time
    - Dla Czerwonych: przygotuj alternatywy (inne typy umów)
    """)

else:
    st.warning("📥 Wczytaj dane aby kontynuować")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
**Ceny Dashboard v1.0** | Abacus Centrum  
Units: 1 (Data Input) ✓ | 2 (New Prices) ✓ | 3-6 (TBD)
""")
