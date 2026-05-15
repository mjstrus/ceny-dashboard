"""
Constants and Configuration for Ceny Dashboard

Centralized place for all magic numbers, naming conventions, and DataFrame contracts.
Eliminates duplication and makes refactoring safer.
"""

# ============================================================================
# PACKAGE CONFIGURATION
# ============================================================================

PACKAGE_SIZE_DOCS = 25  # Documents per package for 100+ pricing
PACKAGE_PRICE_COLUMN = '100+'  # Column name in pricing table for package prices


# ============================================================================
# PRICING DEFAULTS
# ============================================================================

DEFAULT_PRICE = 250  # PLN - fallback if no pricing found
MIN_VALID_PRICE = 0  # PLN - prices must be >= this


# ============================================================================
# TYPE NORMALIZATION
# ============================================================================

TYPE_ALIASES = {
    'kh': 'KH',
    'Kh': 'KH',
    'KH': 'KH',
    'kpir': 'KPIR',
    'KPIR': 'KPIR',
    'Kpir': 'KPIR',
    'ryczałt': 'Ryczałt',
    'RYCZAŁT': 'Ryczałt',
    'ryczalt': 'Ryczałt',
    'Ryczałt': 'Ryczałt',
}

VAT_ALIASES = {
    'tak': 'tak',
    'true': 'tak',
    '1': 'tak',
    'yes': 'tak',
    'True': 'tak',
    'TAK': 'tak',
    'nie': 'nie',
    'false': 'nie',
    '0': 'nie',
    'no': 'nie',
    'False': 'nie',
    'NIE': 'nie',
}

VALID_TYPES = ['KH', 'KPIR', 'Ryczałt']
VALID_VATS = ['tak', 'nie']

PRICE_RANGES = ['1-10', '11-20', '21-50', '51-100', '100+']


# ============================================================================
# DATAFRAME CONTRACTS
# ============================================================================

REQUIRED_DATA_COLUMNS = [
    'ID',                   # Client ID
    'Nazwa',                # Client name
    'Typ_Umowy',           # Client type (KH, KPIR, Ryczałt)
    'VAT',                 # VAT status (tak/nie)
    'Doc_Marzec',          # Documents in March
    'Doc_Luty',            # Documents in February
    'Doc_Styczeń',         # Documents in January
    'Doc_Avg',             # Average documents (computed or provided)
    'Cena_Stara',          # Old price (what they paid)
    'Miał_Rabat_10%',      # Had 10% discount (0 or 1)
]

COMPUTED_DATA_COLUMNS = [
    'Cena_Range',          # Computed: price range based on Doc_Avg
    'Cena_Docelowa',       # Computed: target price from Unit 0
    'Cena_Faktyczna',      # Computed: actual price (with/without discount)
    'Wzrost_Kwota',        # Computed: price increase (PLN)
    'Wzrost_%',            # Computed: price increase (%)
    'Grupa_Klienta',       # Computed: client segment (Standard/VIP/FREE)
]

REQUIRED_PRICING_COLUMNS = [
    'Typ',                 # Client type
    'VAT',                 # VAT status
    '1-10',                # Price for 1-10 documents
    '11-20',               # Price for 11-20 documents
    '21-50',               # Price for 21-50 documents
    '51-100',              # Price for 51-100 documents
    '100+',                # Price per package (25 docs) for 100+ documents
]

PRICE_TABLE_DISPLAY_COLUMNS = [
    'ID',
    'Nazwa',
    'Typ',
    '📊 Status',
    'Widełka',
    'Cennik (bez rabatu)',
    'Miał rabat?',
    'Płacili (mc)',
    '👑 Grupa Klienta',
    '💰 Nowa Cena',
    '💳 Sugerowany rabat (PLN)',
    'Wzrost PLN',
    'Wzrost % (z rabatem)',
    'Wzrost % (gdyby brak rabatu)',
]


# ============================================================================
# COLOR/STATUS CONFIGURATION
# ============================================================================

CLIENT_SEGMENTS = {
    'Zielony': {
        'description': 'Wzrost ≤ 10%',
        'color': '#28a745',
        'emoji': '🟢',
    },
    'Żółty': {
        'description': 'Wzrost 10-20%',
        'color': '#ffc107',
        'emoji': '🟡',
    },
    'Czerwony': {
        'description': 'Wzrost > 20% + miał rabat',
        'color': '#dc3545',
        'emoji': '🔴',
    },
    'Czarny': {
        'description': 'Wzrost > 20% + NO rabat (RYZYKO!)',
        'color': '#000000',
        'emoji': '⚫',
    },
}

DISCOUNT_OFFERS = {
    'before_3rd_day': {
        'amount': 10,  # PLN
        'description': 'za dokumenty do 3. dnia miesiąca',
    },
    'payment_3_days': {
        'amount': 10,  # PLN
        'description': 'za płatność faktury w 3 dni',
    },
    'vacation_request': {
        'amount': 0,   # Free
        'description': 'wniosek o wakacje składkowe',
    },
}


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_data_columns(df) -> None:
    """
    Validate that DataFrame has all required columns for client data.
    Raises ValueError if columns are missing.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValueError: If required columns are missing
    """
    import pandas as pd
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    missing = set(REQUIRED_DATA_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}\n"
            f"Required: {sorted(REQUIRED_DATA_COLUMNS)}\n"
            f"Found: {sorted(df.columns)}"
        )


def validate_pricing_columns(df) -> None:
    """
    Validate that DataFrame has all required columns for pricing table.
    Raises ValueError if columns are missing.
    
    Args:
        df: Pricing DataFrame to validate
        
    Raises:
        ValueError: If required columns are missing
    """
    import pandas as pd
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("Pricing table is empty")
    
    missing = set(REQUIRED_PRICING_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing pricing columns: {sorted(missing)}\n"
            f"Required: {sorted(REQUIRED_PRICING_COLUMNS)}\n"
            f"Found: {sorted(df.columns)}"
        )


def normalize_type(typ_str: str) -> str:
    """
    Normalize client type string using TYPE_ALIASES.
    
    Args:
        typ_str: Type string from any source
        
    Returns:
        Normalized type string (KH, KPIR, or Ryczałt)
        
    Raises:
        ValueError: If type is not recognized
    """
    if not isinstance(typ_str, str):
        typ_str = str(typ_str)
    
    typ_str = typ_str.strip()
    
    if typ_str in TYPE_ALIASES:
        return TYPE_ALIASES[typ_str]
    
    raise ValueError(
        f"Unknown type: '{typ_str}'. "
        f"Valid types: {sorted(set(TYPE_ALIASES.values()))}"
    )


def normalize_vat(vat_str: str) -> str:
    """
    Normalize VAT status string using VAT_ALIASES.
    
    Args:
        vat_str: VAT string from any source
        
    Returns:
        Normalized VAT string ('tak' or 'nie')
        
    Raises:
        ValueError: If VAT status is not recognized
    """
    if not isinstance(vat_str, str):
        vat_str = str(vat_str)
    
    vat_str = vat_str.strip()
    
    if vat_str in VAT_ALIASES:
        return VAT_ALIASES[vat_str]
    
    raise ValueError(
        f"Unknown VAT status: '{vat_str}'. "
        f"Valid values: {sorted(set(VAT_ALIASES.values()))}"
    )
