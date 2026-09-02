"""
Módulo de gestión de estilos y temas (Modo Oscuro / Modo Claro).
"""

def get_theme_css(theme: str = "dark") -> str:
    """
    Genera el CSS necesario para aplicar modo oscuro o modo claro a la aplicación Streamlit.
    """
    if theme == "dark":
        return """
        <style>
        /* === TEMA OSCURO === */
        :root {
            --bg-main: #0b0f19;
            --bg-card: #151c2c;
            --bg-card-hover: #1e293b;
            --bg-sidebar: #0f172a;
            --border-color: #334155;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --accent-primary: #3b82f6;
            --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
            --accent-glow: rgba(59, 130, 246, 0.25);
            --input-bg: #0f172a;
        }

        /* Fondo general */
        .stApp {
            background-color: var(--bg-main) !important;
            color: var(--text-main) !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--bg-sidebar) !important;
            border-right: 1px solid var(--border-color) !important;
        }

        [data-testid="stSidebar"] * {
            color: var(--text-main);
        }

        /* Encabezados y títulos */
        h1, h2, h3, h4, h5, h6, .stHeading {
            color: #ffffff !important;
            font-weight: 700 !important;
        }

        /* Párrafos y textos */
        p, span, label, div {
            color: var(--text-main);
        }

        /* Tarjetas de Métricas */
        [data-testid="stMetric"] {
            background: var(--bg-card) !important;
            padding: 16px 20px !important;
            border-radius: 12px !important;
            border: 1px solid var(--border-color) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: var(--text-muted) !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }

        [data-testid="stMetricValue"] {
            color: #38bdf8 !important;
            font-weight: 800 !important;
            font-size: 1.6rem !important;
        }

        /* Botones Primarios */
        .stButton > button[kind="primary"] {
            background: var(--accent-gradient) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 14px var(--accent-glow) !important;
            transition: all 0.2s ease-in-out !important;
        }

        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
        }

        /* Botones Secundarios */
        .stButton > button:not([kind="primary"]),
        .stDownloadButton > button {
            background-color: var(--bg-card) !important;
            color: var(--text-main) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease-in-out !important;
        }

        .stButton > button:not([kind="primary"]):hover,
        .stDownloadButton > button:hover {
            background-color: var(--bg-card-hover) !important;
            border-color: #60a5fa !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
        }

        /* Campos de texto e inputs */
        .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
            background-color: var(--input-bg) !important;
            color: #ffffff !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }

        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: #38bdf8 !important;
            box-shadow: 0 0 0 1px #38bdf8 !important;
        }

        /* Desplegables Select */
        div[data-baseweb="select"] > div {
            background-color: var(--input-bg) !important;
            color: #ffffff !important;
            border-color: var(--border-color) !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--text-main) !important;
            font-weight: 600 !important;
        }

        div[data-testid="stExpander"] {
            border: none !important;
            margin-bottom: 12px !important;
        }

        /* File Uploader */
        [data-testid="stFileUploader"] {
            background-color: var(--bg-card) !important;
            padding: 18px !important;
            border-radius: 12px !important;
            border: 2px dashed var(--border-color) !important;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: #38bdf8 !important;
        }

        /* Barra de progreso */
        .stProgress > div > div > div > div {
            background: var(--accent-gradient) !important;
        }

        /* Divisores */
        hr {
            border-color: var(--border-color) !important;
        }
        </style>
        """
    else:
        return """
        <style>
        /* === TEMA CLARO === */
        :root {
            --bg-main: #f8fafc;
            --bg-card: #ffffff;
            --bg-card-hover: #f1f5f9;
            --bg-sidebar: #ffffff;
            --border-color: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --accent-primary: #2563eb;
            --accent-gradient: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
            --accent-glow: rgba(37, 99, 235, 0.2);
            --input-bg: #ffffff;
        }

        /* Fondo general */
        .stApp {
            background-color: var(--bg-main) !important;
            color: var(--text-main) !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--bg-sidebar) !important;
            border-right: 1px solid var(--border-color) !important;
        }

        [data-testid="stSidebar"] * {
            color: var(--text-main);
        }

        /* Encabezados y títulos */
        h1, h2, h3, h4, h5, h6, .stHeading {
            color: #0f172a !important;
            font-weight: 700 !important;
        }

        /* Párrafos y textos */
        p, span, label, div {
            color: var(--text-main);
        }

        /* Tarjetas de Métricas */
        [data-testid="stMetric"] {
            background: var(--bg-card) !important;
            padding: 16px 20px !important;
            border-radius: 12px !important;
            border: 1px solid var(--border-color) !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: var(--text-muted) !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }

        [data-testid="stMetricValue"] {
            color: #2563eb !important;
            font-weight: 800 !important;
            font-size: 1.6rem !important;
        }

        /* Botones Primarios */
        .stButton > button[kind="primary"] {
            background: var(--accent-gradient) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 14px var(--accent-glow) !important;
            transition: all 0.2s ease-in-out !important;
        }

        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35) !important;
        }

        /* Botones Secundarios */
        .stButton > button:not([kind="primary"]),
        .stDownloadButton > button {
            background-color: var(--bg-card) !important;
            color: var(--text-main) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease-in-out !important;
        }

        .stButton > button:not([kind="primary"]):hover,
        .stDownloadButton > button:hover {
            background-color: var(--bg-card-hover) !important;
            border-color: #94a3b8 !important;
            color: #0f172a !important;
            transform: translateY(-1px) !important;
        }

        /* Campos de texto e inputs */
        .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
            background-color: var(--input-bg) !important;
            color: #0f172a !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }

        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 1px #2563eb !important;
        }

        /* Desplegables Select */
        div[data-baseweb="select"] > div {
            background-color: var(--input-bg) !important;
            color: #0f172a !important;
            border-color: var(--border-color) !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--text-main) !important;
            font-weight: 600 !important;
        }

        div[data-testid="stExpander"] {
            border: none !important;
            margin-bottom: 12px !important;
        }

        /* File Uploader */
        [data-testid="stFileUploader"] {
            background-color: var(--bg-card) !important;
            padding: 18px !important;
            border-radius: 12px !important;
            border: 2px dashed var(--border-color) !important;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: #2563eb !important;
        }

        /* Barra de progreso */
        .stProgress > div > div > div > div {
            background: var(--accent-gradient) !important;
        }

        /* Divisores */
        hr {
            border-color: var(--border-color) !important;
        }
        </style>
        """
