import streamlit as st

# Centralized theme manager for CSS injection

def get_css_for_theme(theme: str) -> str:
    """Return CSS string for the given theme name ("dark" or "light")."""
    # Common CSS to control widget widths and button sizing (applies to both themes)
    common = r"""
    <style>
    /* Limit the maximum width of input widgets so they don't span the full page */
    div.stTextInput, div.stNumberInput, div.stSelectbox, div.stTextArea, div.stDateInput, div.stMultiSelect {
        max-width: 680px;
    }

    /* Limit button width and avoid full-width buttons visually */
    div.stButton > button {
        min-width: 120px;
        max-width: 260px;
        padding: 8px 14px;
        border-radius: 8px;
        border: none;
    }

    /* Avoid moving the button on :active - remove transform */
    div.stButton > button:active { transform: none !important; }

    /* Make the app container use a nice readable max width for content columns */
    .block-container { max-width: 1300px; }

    /* Make small adjustments for column spacing */
    .css-1lcbmhc { gap: 10px; }
    </style>
    """

    if theme == 'light':
        light = r"""
        <style>
        /* Light pastel theme */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        .stApp, .block-container { background: linear-gradient(135deg, #fff7fb 0%, #f7fbff 100%); color: #111827; font-family: 'Inter', sans-serif; }
        .css-1d391kg { background: transparent; }
        /* Buttons */
        div.stButton > button { background-color: #6ea8fe; color: #07204a; }
        div.stButton > button.secondary { background-color: #ffd6a5; }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #07204a; }
        /* Card styling for light theme */
        .card-style { background: rgba(255,255,255,0.9); box-shadow: 0 8px 24px rgba(12, 24, 51, 0.06); border-radius: 12px; padding: 18px; }
        .card-large { height:140px; }
        </style>"""
        return common + light
    else:
        dark = r"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        /* Dark modern theme tweaks */
        .stApp, .block-container { background: #0b0f14; color: #e6eef8; font-family: 'Inter', sans-serif; }
        .css-1d391kg { background: transparent; }
        /* Buttons */
        div.stButton > button { background-color: #0f766e; color: #ffffff; }
        div.stButton > button.secondary { background-color: #ef4444; }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #ffffff; }
        /* Card helper class for dark cards */
        .card-style { background: #0b1220; color: #fff; border-radius: 14px; box-shadow: 0 6px 18px rgba(0,0,0,0.4); padding: 18px; }
        .card-large { height:140px; }
        /* Sidebar tweaks */
        .css-18e3th9 { background: linear-gradient(180deg, #0b1220 0%, #071024 100%); }
        </style>
        """
        return common + dark


def apply_theme(theme: str = 'dark'):
    """Inject CSS for the selected theme into the Streamlit app."""
    css = get_css_for_theme(theme)
    # Use st.html() to inject CSS into the page header (not visible as text)
    # This hides the style block and actually applies the styles
    st.html(css)
