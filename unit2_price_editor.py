"""
Unit 2: Price Editor - FIXED VERSION
Uproszczona, działająca wersja
"""

import streamlit as st
import pandas as pd
from calculate_new_prices import calculate_new_prices
from summary_generator import generate_summary


def render_unit2_editor(df_with_prices):
    """
    Render Unit 2: Price editing interface with ONLY editable columns
    
    Args:
        df_with_prices: DataFrame with calculated prices
        
    Returns:
        edited_df: DataFrame with user edits from st.data_editor
    """
    
    st.info("""
    **Edytuj poniższe kolumny:**
    - **👑 Grupa Klienta:** Standard / VIP / FREE
    - **💰 Nowa Cena:** Zmień cenę jeśli trzeba
    
    **Pozostałe kolumny pokazują stan:**
    - Cena Stara: Cena którą płacił dotychczas
    - Status: Zielony/Żółty/Czarny (na bazie wzrostu)
    """)
    
    # Przygotuj TYLKO kolumny do edycji - bez None!
    df_display = df_with_prices[[
        'ID', 'Nazwa', 'Cena_Stara', 'Cena_Docelowa', 'Grupa_Klienta', 'Status'
    ]].copy()
    
    # Formatuj Status z emoji
    df_display['Status'] = df_display['Status'].apply(
        lambda x: '🟢 Zielony' if x == 'Zielony' 
                  else '🟡 Żółty' if x == 'Żółty'
                  else '🔴 Czerwony' if x == 'Czerwony'
                  else '⚫ Czarny' if x == 'Czarny'
                  else '❓ ?'
    )
    
    # Zmień nazwy na user-friendly (ale pamiętaj oryginalne!)
    df_display.columns = ['ID', 'Nazwa', 'Cena Stara', '💰 Nowa Cena', '👑 Grupa Klienta', '📊 Status']
    
    # EDYTOWALNA TABELA
    st.subheader("Edytuj tabelę poniżej")
    
    edited_df = st.data_editor(
        df_display,
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
            "📊 Status": st.column_config.TextColumn(disabled=True),
            "Cena Stara": st.column_config.NumberColumn(disabled=True),
            "Nazwa": st.column_config.TextColumn(disabled=True),
            "ID": st.column_config.TextColumn(disabled=True),
        }
    )
    
    return edited_df


def handle_price_editor_submission(edited_df, session_state):
    """
    Handle submitted price edits - UPDATE session_state
    
    Args:
        edited_df: DataFrame with edited prices and groups
        session_state: Streamlit session state object
        
    Returns:
        bool: True if update successful, False otherwise
    """
    
    if edited_df is None or len(edited_df) == 0:
        st.warning("⚠️ Brak danych do zatwierdź!")
        return False
    
    try:
        # Mapuj z renamed columns z powrotem na oryginalne nazwy
        updates_data = {
            'ID': edited_df['ID'],
            'Grupa_Klienta': edited_df['👑 Grupa Klienta'],
            'Cena_Docelowa': edited_df['💰 Nowa Cena']
        }
        
        updates_df = pd.DataFrame(updates_data).set_index('ID')
        
        # Update session_state.df (oryginalne dane)
        for idx in updates_df.index:
            mask = session_state.df['ID'] == idx
            if mask.any():
                session_state.df.loc[mask, 'Grupa_Klienta'] = updates_df.loc[idx, 'Grupa_Klienta']
                session_state.df.loc[mask, 'Cena_Docelowa'] = updates_df.loc[idx, 'Cena_Docelowa']
        
        # Przelicz całe df_with_prices na bazie zmienionego session_state.df
        session_state.df_with_prices = calculate_new_prices(
            session_state.df,
            session_state.pricing_df
        )
        
        # Przelicz summary
        session_state.summary = generate_summary(session_state.df_with_prices)
        
        st.success("✅ Zmiany zatwierdzone! Statystyki przeobliczone.")
        st.info(f"ℹ️ {len(edited_df)} klientów zaktualizowano")
        
        # Odśwież stronę - Unit 4 musi przeczytać nowy summary!
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Błąd podczas aktualizacji: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False


def render_unit2_complete_section(df_with_prices):
    """
    Complete Unit 2 section: render editor + button + handle submission
    
    Args:
        df_with_prices: DataFrame with calculated prices
    """
    
    # Render editor and get edits
    edited_df = render_unit2_editor(df_with_prices)
    
    # Button to submit edits
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ OK - ZATWIERDŹ EDYCJE", type="primary", use_container_width=True, key="confirm_edits"):
            handle_price_editor_submission(edited_df, st.session_state)
    
    st.divider()
