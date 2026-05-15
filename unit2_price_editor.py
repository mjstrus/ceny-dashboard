"""
Unit 2: Price Editor for Ceny Dashboard
Handles rendering the price editing table and processing batch updates
"""

import streamlit as st
import pandas as pd
from calculate_new_prices import get_price_table, calculate_new_prices
from summary_generator import generate_summary


def render_unit2_editor(df_with_prices):
    """
    Render Unit 2: Price editing interface with editable table
    
    Args:
        df_with_prices: DataFrame with calculated prices
        
    Returns:
        edited_df: DataFrame with user edits from st.data_editor
    """
    
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
    - Wzrost bez rabatu: (1100-1000)/1000 = 10%
    """)
    
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
    
    return edited_df


def handle_price_editor_submission(edited_df, session_state):
    """
    Handle submitted price edits with batch update (O(n) instead of O(n²))
    
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
        # Extract updated columns from edited_df
        updates = pd.DataFrame({
            'ID': edited_df['ID'],
            'Grupa_Klienta': edited_df.get('👑 Grupa Klienta', edited_df.get('Grupa_Klienta')),
            'Cena_Docelowa': edited_df.get('💰 Nowa Cena', edited_df.get('Cena_Docelowa'))
        })
        
        # Batch update: set index to ID for efficient merge/update
        updates = updates.set_index('ID')
        
        # Update session_state.df with batch operation (O(n) instead of O(n²))
        for col in ['Grupa_Klienta', 'Cena_Docelowa']:
            mask = session_state.df['ID'].isin(updates.index)
            session_state.df.loc[mask, col] = session_state.df.loc[mask, 'ID'].map(
                updates[col]
            ).values
        
        # Recalculate prices and summary
        session_state.df_with_prices = calculate_new_prices(
            session_state.df, 
            session_state.pricing_df
        )
        session_state.summary = generate_summary(session_state.df_with_prices)
        
        st.success("✅ Zmiany zatwierdzone! Statystyki przeobliczone.")
        st.info(f"ℹ️ {len(edited_df)} klientów zaktualizowano")
        
        # Refresh page to show updated statistics
        try:
            st.rerun()
        except:
            st.warning("Odśwież stronę F5 aby zobaczyć zmienione statystyki w Unit 3")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Błąd podczas aktualizacji: {str(e)}")
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
    if st.button("OK Zatwierdz wszystkie zmiany", type="primary"):
        handle_price_editor_submission(edited_df, st.session_state)
    
    st.divider()
    st.success("OK Gotowe! Dashboard ready.")
