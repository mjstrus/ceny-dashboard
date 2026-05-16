"""
CENY DASHBOARD - 5-Step Milestone Architecture
Marcin's requested flow: Cennik → Excel → Edycje → Statystyki → Raport
"""

import streamlit as st
import pandas as pd
from io import BytesIO

# ============================================================================
# CONFIG & IMPORTS
# ============================================================================

st.set_page_config(page_title="Ceny Dashboard", layout="wide")

from price_manager import get_default_pricing, apply_global_modification
from data_loader import load_excel_file, get_display_dataframe
from calculate_new_prices import calculate_new_prices
from summary_generator import generate_summary, get_alerts
from unit2_price_editor import render_unit2_editor, handle_price_editor_submission
from pdf_reporter import create_summary_report

NAVY = "#1B2A4A"

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'step_1_done' not in st.session_state:
    st.session_state.step_1_done = False  # Cennik zatwierdzon

if 'step_2_done' not in st.session_state:
    st.session_state.step_2_done = False  # Excel wczytany

if 'step_3_done' not in st.session_state:
    st.session_state.step_3_done = False  # Edycje zatwierdzone

if 'step_4_done' not in st.session_state:
    st.session_state.step_4_done = False  # Statystyki obliczone

if 'pricing_df' not in st.session_state:
    st.session_state.pricing_df = None

if 'df' not in st.session_state:
    st.session_state.df = None

if 'df_with_prices' not in st.session_state:
    st.session_state.df_with_prices = None

if 'summary' not in st.session_state:
    st.session_state.summary = None


# ============================================================================
# HEADER
# ============================================================================

st.markdown(f"""
<div style="background: linear-gradient(to right, {NAVY}, #0d1b2a); padding: 20px; border-radius: 10px; margin-bottom: 30px;">
    <h1 style="color: white; margin: 0;">💰 Ceny Dashboard - Abacus Centrum</h1>
    <p style="color: #E8A000; margin: 0; margin-top: 10px;">5-Step Pricing Workflow</p>
</div>
""", unsafe_allow_html=True)

# Progress indicator
progress_cols = st.columns(5)
steps = [
    ("1️⃣", "Cennik", st.session_state.step_1_done),
    ("2️⃣", "Excel", st.session_state.step_2_done),
    ("3️⃣", "Edycje", st.session_state.step_3_done),
    ("4️⃣", "Statystyki", st.session_state.step_4_done),
    ("5️⃣", "Raport", False),
]

for i, (emoji, label, done) in enumerate(steps):
    with progress_cols[i]:
        if done:
            st.success(f"{emoji} {label}")
        else:
            st.info(f"{emoji} {label}")


# ============================================================================
# KROK 1: CENNIK
# ============================================================================

st.divider()
st.markdown("## KROK 1: Zatwierdzenie Cennika")

if not st.session_state.step_1_done:
    st.info("**Przejrzyj i zatwierdź nowy cennik 2026**")
    
    # Load default pricing
    pricing_df = get_default_pricing()
    st.session_state.pricing_df = pricing_df
    
    # Display pricing table
    st.subheader("Nowy Cennik 2026")
    st.dataframe(
        pricing_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Button to confirm
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ OK - CENNIK ZATWIERDZON", type="primary", use_container_width=True, key="step1"):
            st.session_state.step_1_done = True
            st.success("✅ Cennik zatwierdzon! Przejdź do Kroku 2.")
            st.rerun()

else:
    st.success("✅ Cennik zatwierdzon")
    with st.expander("📋 Pokaż cennik"):
        st.dataframe(st.session_state.pricing_df, use_container_width=True, hide_index=True)


# ============================================================================
# KROK 2: WGRYWANIE EXCELA
# ============================================================================

st.divider()
st.markdown("## KROK 2: Wgrywanie Danych (Excel)")

if not st.session_state.step_1_done:
    st.warning("⏳ Najpierw zatwierdź cennik w Kroku 1")

elif not st.session_state.step_2_done:
    st.info("**Wgraj plik Excel z danymi klientów**")
    
    uploaded_file = st.file_uploader("Wybierz plik Excel", type="xlsx")
    
    if uploaded_file is not None:
        try:
            # Load data
            with st.spinner("Wczytywanie..."):
                df, errors = load_excel_file(uploaded_file)
            
            # Show errors if any
            if errors:
                st.error("❌ Błędy w danych:")
                for error in errors:
                    st.error(f"  • {error}")
            else:
                st.success(f"✅ Załadowano {len(df)} klientów")
                st.session_state.df = df
                
                # Show preview
                st.subheader("Podgląd danych")
                st.dataframe(df.head(10), use_container_width=True, hide_index=True)
                
                # Button to confirm
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("✅ OK - DANE WCZYTANE", type="primary", use_container_width=True, key="step2"):
                        st.session_state.step_2_done = True
                        # Calculate prices immediately
                        st.session_state.df_with_prices = calculate_new_prices(
                            st.session_state.df,
                            st.session_state.pricing_df
                        )
                        st.success("✅ Dane wczytane! Przejdź do Kroku 3.")
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ Błąd przy wczytywaniu: {str(e)}")

else:
    st.success("✅ Dane wczytane")
    st.write(f"**{len(st.session_state.df)} klientów załadowanych**")
    with st.expander("📋 Pokaż dane"):
        st.dataframe(st.session_state.df, use_container_width=True, hide_index=True)


# ============================================================================
# KROK 3: EDYCJE DANYCH
# ============================================================================

st.divider()
st.markdown("## KROK 3: Edycja Danych")

if not st.session_state.step_2_done:
    st.warning("⏳ Najpierw wgraj dane w Kroku 2")

elif not st.session_state.step_3_done:
    st.info("**Edytuj dane klientów jeśli trzeba**")
    
    # Render editor
    edited_df = render_unit2_editor(st.session_state.df_with_prices)
    
    # Button to confirm edits
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ OK - ZMIANY ZATWIERDZONE", type="primary", use_container_width=True, key="step3"):
            # Handle submission
            try:
                # Extract edits
                updates = pd.DataFrame({
                    'ID': edited_df['ID'],
                    'Grupa_Klienta': edited_df.get('👑 Grupa Klienta', edited_df.get('Grupa_Klienta')),
                    'Cena_Docelowa': edited_df.get('💰 Nowa Cena', edited_df.get('Cena_Docelowa'))
                })
                
                updates = updates.set_index('ID')
                
                # Batch update
                for col in ['Grupa_Klienta', 'Cena_Docelowa']:
                    mask = st.session_state.df['ID'].isin(updates.index)
                    st.session_state.df.loc[mask, col] = st.session_state.df.loc[mask, 'ID'].map(
                        updates[col]
                    ).values
                
                # Recalculate prices with new data
                st.session_state.df_with_prices = calculate_new_prices(
                    st.session_state.df,
                    st.session_state.pricing_df
                )
                
                st.session_state.step_3_done = True
                st.success(f"✅ {len(edited_df)} klientów zaktualizowano! Przejdź do Kroku 4.")
                st.rerun()
            
            except Exception as e:
                st.error(f"❌ Błąd: {str(e)}")

else:
    st.success("✅ Edycje zatwierdzone")
    st.info("📊 Statystyki w Kroku 4 się automatycznie przeliczą...")
    with st.expander("📋 Pokaż edytowane dane"):
        st.dataframe(st.session_state.df_with_prices, use_container_width=True, hide_index=True)


# ============================================================================
# KROK 4: STATYSTYKI & RAPORT
# ============================================================================

st.divider()
st.markdown("## KROK 4: Statystyki & Raport")

if not st.session_state.step_3_done:
    st.warning("⏳ Najpierw zatwierdź edycje w Kroku 3")

else:
    # ZAWSZE przeliczyć summary na bazie current df_with_prices
    # (jeśli User edytował w Unit 2, summary musi być nowy!)
    st.session_state.summary = generate_summary(st.session_state.df_with_prices)
    
    summary = st.session_state.summary
    alerts = get_alerts(summary)
    
    # Display metrics
    st.subheader("📊 Metryki Główne")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Liczba Klientów",
            summary.get('Liczba_Klientów_Razem', 0),
            f"Standard: {summary.get('Liczba_Klientów_Standard', 0)}"
        )
    
    with col2:
        st.metric(
            "Przychód PRZED (mc)",
            f"{summary.get('Przychod_Przed_PLN', 0):,.0f} PLN",
            f"Rocznie: {summary.get('Roczny_Przed_PLN', 0):,.0f} PLN"
        )
    
    with col3:
        st.metric(
            "Przychód PO (mc)",
            f"{summary.get('Przychod_Po_PLN', 0):,.0f} PLN",
            f"Rocznie: {summary.get('Roczny_Po_PLN', 0):,.0f} PLN"
        )
    
    with col4:
        st.metric(
            "Wzrost (mc)",
            f"+{summary.get('Wzrost_PLN', 0):,.0f} PLN",
            f"Roczny impact: +{summary.get('Roczny_Wzrost_PLN', 0):,.0f} PLN"
        )
    
    # Segmentacja
    st.subheader("🎯 Segmentacja Klientów")
    
    seg_col1, seg_col2, seg_col3, seg_col4 = st.columns(4)
    
    with seg_col1:
        st.metric(
            "🟢 Zielony",
            summary.get('Zielony_Cnt', 0),
            "Wzrost ≤10% (OK)"
        )
    
    with seg_col2:
        st.metric(
            "🟡 Żółty",
            summary.get('Zolty_Cnt', 0),
            "Wzrost 10-20%"
        )
    
    with seg_col3:
        st.metric(
            "🔴 Czerwony",
            summary.get('Czerwony_Cnt', 0),
            "Wzrost >20% z rabatem"
        )
    
    with seg_col4:
        st.metric(
            "⚫ Czarny (RYZYKO!)",
            summary.get('Czarny_Cnt', 0),
            "Wzrost >20% bez rabatu"
        )
    
    # Alerts
    if alerts:
        st.subheader("⚠️ Alerty")
        for alert in alerts:
            st.warning(alert)
    
    # Button to download report
    st.subheader("📥 Pobierz Raport")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ POBIERZ PDF RAPORT", type="primary", use_container_width=True, key="step4"):
            try:
                with st.spinner("Generowanie PDF..."):
                    pdf_bytes = create_summary_report(summary, st.session_state.df_with_prices)
                
                st.download_button(
                    label="📥 Kliknij aby pobrać PDF",
                    data=pdf_bytes,
                    file_name=f"Statystyka_Klientów_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_report"
                )
                st.success("✅ Raport gotowy do pobrania!")
                st.session_state.step_4_done = True
            
            except Exception as e:
                st.error(f"❌ Błąd przy generowaniu PDF: {str(e)}")
    
    # Display table with all data
    st.subheader("📋 Pełna Tabela Danych")
    st.dataframe(
        st.session_state.df_with_prices,
        use_container_width=True,
        hide_index=True
    )
    
    # DEBUG PANEL
    with st.expander("🔧 DEBUG: Weryfikacja Obliczeń"):
        st.write("**Dane które są sumowane:**")
        
        # Pokaż co idzie do summary
        debug_df = st.session_state.df_with_prices[[
            'ID', 'Nazwa', 'Grupa_Klienta', 'Cena_Faktyczna', 'Cena_Docelowa', 'Wzrost_Kwota'
        ]].copy()
        
        st.dataframe(debug_df, use_container_width=True, hide_index=True)
        
        st.write("**Ręczna weryfikacja:**")
        
        # Pokaż sumy - normalize case!
        debug_df['Grupa_Klienta_Upper'] = debug_df['Grupa_Klienta'].str.upper()
        paying = debug_df[debug_df['Grupa_Klienta_Upper'] != 'FREE']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Suma Cena_Faktyczna", f"{paying['Cena_Faktyczna'].sum():,.2f} PLN")
        with col2:
            st.metric("Suma Cena_Docelowa", f"{paying['Cena_Docelowa'].sum():,.2f} PLN")
        with col3:
            st.metric("Różnica (Wzrost)", f"{(paying['Cena_Docelowa'].sum() - paying['Cena_Faktyczna'].sum()):,.2f} PLN")
        
        st.write(f"**Liczba wierszy (bez FREE):** {len(paying)}")
        st.write(f"**Liczba wierszy (wszystkie):** {len(debug_df)}")


# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
**Abacus Centrum Księgowe** | Puławy
📧 Kontakt: info@abacus24.pl
""")
