"""Streamlit dashboard for the NeuroSheet analysis workflow."""

from __future__ import annotations

from itertools import cycle
from typing import Any

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from src.analyzer import DataAnalysisError, analyze_dataframe
from src.data_cleaner import DataCleaningError, clean_dataframe
from src.data_loader import DataLoadError, load_excel_folder, load_uploaded_excel_files
from src.exporter import ExportError, export_results
from src.insights import generate_insights
from src.predictor import PredictionError, predict_trend
from src.utils import format_value


st.set_page_config(
    page_title="NeuroSheet",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)


THEME_PALETTES = {
    "Dark": {
        "bg": "#040507",
        "bg_secondary": "#0a0d12",
        "panel": "rgba(10, 13, 18, 0.95)",
        "panel_soft": "rgba(18, 22, 30, 0.88)",
        "text": "#f3eee0",
        "muted": "#a2a8b4",
        "accent": "#b89445",
        "accent_strong": "#f0c86e",
        "border": "rgba(184, 148, 69, 0.26)",
        "success": "#89d8a9",
        "warning": "#f0c96b",
        "danger": "#ef8b88",
        "shadow": "0 26px 70px rgba(0, 0, 0, 0.56)",
        "hero_bg": """
            linear-gradient(135deg, rgba(8, 10, 14, 0.98), rgba(5, 7, 10, 0.97)),
            radial-gradient(circle at top left, rgba(240, 200, 110, 0.08), transparent 30%)
        """,
        "page_bg": """
            radial-gradient(circle at 12% 10%, rgba(240, 200, 110, 0.10), transparent 22%),
            radial-gradient(circle at 88% 76%, rgba(184, 148, 69, 0.10), transparent 24%),
            radial-gradient(circle at top right, rgba(255, 255, 255, 0.03), transparent 18%),
            linear-gradient(180deg, #030406 0%, #07090d 38%, #040507 100%)
        """,
        "sidebar_bg": "linear-gradient(180deg, rgba(6, 8, 11, 0.99), rgba(12, 15, 21, 0.97))",
        "chart_bar": "#c6a04d",
        "chart_bar_alt": "#8f6a23",
        "chart_line": "#f0c86e",
        "chart_grid": "rgba(240, 200, 110, 0.10)",
        "chart_axis": "#d8c8a4",
        "table_bg": "rgba(9, 11, 16, 0.96)",
        "table_bg_alt": "rgba(15, 18, 24, 0.94)",
        "input_bg": "rgba(13, 16, 22, 0.95)",
        "button_bg": "linear-gradient(180deg, rgba(184, 148, 69, 0.98), rgba(143, 106, 35, 0.98))",
        "button_text": "#0b0d11",
        "tab_bg": "rgba(255, 255, 255, 0.03)",
        "widget_bg": "rgba(15, 18, 24, 0.92)",
        "widget_text": "#f3eee0",
        "widget_selected_bg": "rgba(184, 148, 69, 0.20)",
        "chart_bg": "rgba(10, 13, 18, 0.94)",
    },
    "Light": {
        "bg": "#f6f1e6",
        "bg_secondary": "#eee6d6",
        "panel": "rgba(255, 251, 244, 0.98)",
        "panel_soft": "rgba(247, 241, 230, 0.96)",
        "text": "#1f2530",
        "muted": "#59616e",
        "accent": "#9c7120",
        "accent_strong": "#7f5a16",
        "border": "rgba(156, 113, 32, 0.24)",
        "success": "#2d8f5d",
        "warning": "#a57a1f",
        "danger": "#b04c4a",
        "shadow": "0 18px 44px rgba(88, 74, 42, 0.12)",
        "hero_bg": """
            linear-gradient(135deg, rgba(255, 252, 246, 0.99), rgba(243, 235, 219, 0.97)),
            radial-gradient(circle at top left, rgba(156, 113, 32, 0.08), transparent 34%)
        """,
        "page_bg": """
            radial-gradient(circle at top left, rgba(156, 113, 32, 0.10), transparent 23%),
            radial-gradient(circle at 84% 76%, rgba(156, 113, 32, 0.08), transparent 20%),
            linear-gradient(180deg, #faf5eb 0%, #f0e7d8 48%, #f7f1e6 100%)
        """,
        "sidebar_bg": "linear-gradient(180deg, rgba(248, 243, 234, 0.99), rgba(239, 232, 218, 0.98))",
        "chart_bar": "#a37a28",
        "chart_bar_alt": "#7d5c18",
        "chart_line": "#8b651f",
        "chart_grid": "rgba(156, 113, 32, 0.14)",
        "chart_axis": "#4b4336",
        "table_bg": "rgba(255, 251, 244, 0.98)",
        "table_bg_alt": "rgba(246, 239, 227, 0.95)",
        "input_bg": "rgba(255, 251, 244, 0.98)",
        "button_bg": "linear-gradient(180deg, rgba(156, 113, 32, 0.98), rgba(127, 90, 22, 0.98))",
        "button_text": "#fff9ef",
        "tab_bg": "rgba(156, 113, 32, 0.05)",
        "widget_bg": "rgba(255, 250, 242, 0.98)",
        "widget_text": "#1f2530",
        "widget_selected_bg": "rgba(156, 113, 32, 0.14)",
        "chart_bg": "rgba(255, 250, 242, 0.98)",
    },
}


def build_theme_css(mode: str) -> str:
    """Build CSS from the selected appearance palette."""
    palette = THEME_PALETTES[mode]
    return f"""
    <style>
        :root {{
            --bg: {palette['bg']};
            --bg-secondary: {palette['bg_secondary']};
            --bg-panel: {palette['panel']};
            --bg-panel-soft: {palette['panel_soft']};
            --text: {palette['text']};
            --muted: {palette['muted']};
            --accent: {palette['accent']};
            --accent-strong: {palette['accent_strong']};
            --border: {palette['border']};
            --success: {palette['success']};
            --warning: {palette['warning']};
            --danger: {palette['danger']};
            --shadow: {palette['shadow']};
            --table-bg: {palette['table_bg']};
            --table-bg-alt: {palette['table_bg_alt']};
            --input-bg: {palette['input_bg']};
            --button-bg: {palette['button_bg']};
            --button-text: {palette['button_text']};
            --tab-bg: {palette['tab_bg']};
            --widget-bg: {palette['widget_bg']};
            --widget-text: {palette['widget_text']};
            --widget-selected-bg: {palette['widget_selected_bg']};
            --chart-bg: {palette['chart_bg']};
        }}

        .stApp {{
            background: {palette['page_bg']};
            color: var(--text);
        }}

        header[data-testid="stHeader"] {{
            height: 2.2rem !important;
            min-height: 2.2rem !important;
            background: transparent !important;
            border: none !important;
            top: 0.2rem !important;
        }}

        [data-testid="stDecoration"],
        #MainMenu,
        footer {{
            display: none !important;
        }}

        [data-testid="stSidebarCollapsedControl"] {{
            display: flex !important;
            position: fixed !important;
            top: 1.25rem !important;
            left: 0.9rem !important;
            z-index: 1000 !important;
            background: var(--bg-panel) !important;
            border: 1px solid var(--border) !important;
            border-radius: 999px !important;
            box-shadow: var(--shadow) !important;
        }}

        [data-testid="stSidebarCollapsedControl"] button {{
            color: var(--text) !important;
        }}

        section[data-testid="stSidebar"] {{
            background: {palette['sidebar_bg']};
            border-right: 1px solid var(--border);
            transition: background 240ms ease;
            padding-top: 0 !important;
        }}

        section[data-testid="stSidebar"] * {{
            color: var(--text) !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
            height: 3.35rem !important;
            min-height: 3.35rem !important;
            padding: 0.75rem 0.7rem 0.2rem 0.7rem !important;
            margin: 0 !important;
            border: none !important;
            overflow: visible !important;
            display: flex !important;
            align-items: flex-start !important;
            justify-content: flex-start !important;
            background: transparent !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button {{
            color: var(--text) !important;
            background: var(--bg-panel) !important;
            border: 1px solid var(--border) !important;
            border-radius: 999px !important;
            box-shadow: var(--shadow) !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button:hover {{
            border-color: var(--accent) !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {{
            color: var(--text) !important;
        }}

        .block-container {{
            padding-top: 0.45rem;
            padding-bottom: 2rem;
            max-width: 1280px;
            animation: contentRise 460ms ease-out;
        }}

        section[data-testid="stSidebar"] .block-container {{
            padding-top: 0.1rem !important;
            padding-bottom: 1.2rem !important;
            margin-top: 0 !important;
        }}

        section[data-testid="stSidebar"] > div:first-child {{
            padding-top: 0 !important;
            margin-top: 0 !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            padding-top: 0 !important;
            margin-top: 0 !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
            margin-top: 0.15rem !important;
            padding-top: 0 !important;
        }}

        .sidebar-workspace-title {{
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            color: var(--text);
            margin: 0.3rem 0 0.75rem 0;
            padding: 0;
        }}

        [data-testid="column"] {{
            display: flex;
            align-self: stretch;
        }}

        [data-testid="column"] > div {{
            width: 100%;
        }}

        h1, h2, h3, h4, h5, h6, p, span, label, div {{
            color: var(--text);
        }}

        @keyframes contentRise {{
            from {{
                opacity: 0;
                transform: translateY(12px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes panelReveal {{
            from {{
                opacity: 0;
                transform: translateY(18px) scale(0.99);
            }}
            to {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}

        @keyframes fieldReveal {{
            from {{
                opacity: 0;
                transform: translateY(8px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes heroGlowShift {{
            0% {{
                transform: translate3d(-2%, 0, 0) scale(1);
                opacity: 0.42;
            }}
            50% {{
                transform: translate3d(3%, -2%, 0) scale(1.08);
                opacity: 0.65;
            }}
            100% {{
                transform: translate3d(-2%, 0, 0) scale(1);
                opacity: 0.42;
            }}
        }}

        @keyframes heroBeamSweep {{
            0% {{
                transform: translateX(-10%) rotate(0deg);
                opacity: 0.08;
            }}
            50% {{
                transform: translateX(8%) rotate(2deg);
                opacity: 0.18;
            }}
            100% {{
                transform: translateX(-10%) rotate(0deg);
                opacity: 0.08;
            }}
        }}

        .hero-shell {{
            border: 1px solid var(--border);
            border-radius: 26px;
            padding: 2.2rem 2.35rem;
            background: {palette['hero_bg']};
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
            animation: panelReveal 420ms ease-out;
        }}

        .hero-shell::before {{
            content: "";
            position: absolute;
            inset: -18% auto auto -8%;
            width: 52%;
            height: 135%;
            background:
                radial-gradient(circle at 30% 40%, rgba(240, 200, 110, 0.16), transparent 45%),
                linear-gradient(135deg, rgba(240, 200, 110, 0.10), transparent 60%);
            filter: blur(18px);
            pointer-events: none;
            animation: heroGlowShift 10s ease-in-out infinite;
        }}

        .hero-shell::after {{
            content: "";
            position: absolute;
            width: 42%;
            height: 150%;
            right: -8%;
            bottom: -52%;
            background:
                radial-gradient(circle, rgba(240, 200, 110, 0.18), transparent 54%),
                linear-gradient(120deg, transparent 10%, rgba(240, 200, 110, 0.08) 45%, transparent 75%);
            pointer-events: none;
            animation: heroBeamSweep 12s ease-in-out infinite;
        }}

        .eyebrow {{
            text-transform: uppercase;
            letter-spacing: 0.22em;
            font-size: 0.74rem;
            color: var(--accent-strong);
            margin-bottom: 0.8rem;
            font-weight: 700;
        }}

        .hero-title {{
            font-size: 3rem;
            line-height: 1.02;
            margin: 0 0 0.9rem 0;
            font-weight: 800;
        }}

        .hero-copy {{
            color: var(--muted);
            font-size: 1.02rem;
            line-height: 1.78;
            max-width: 860px;
            margin: 0;
        }}

        .badge-row {{
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-top: 1.35rem;
        }}

        .status-badge {{
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.04);
            border-radius: 999px;
            padding: 0.52rem 0.85rem;
            font-size: 0.86rem;
            color: var(--text);
        }}

        .section-title {{
            margin-top: 1.75rem;
            margin-bottom: 0.75rem;
            font-size: 1.08rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--muted);
        }}

        .panel-card {{
            border: 1px solid var(--border);
            background:
                linear-gradient(180deg, var(--bg-panel), var(--bg-panel-soft)),
                radial-gradient(circle at top right, rgba(240, 200, 110, 0.04), transparent 26%);
            border-radius: 22px;
            padding: 1.2rem 1.2rem 1.1rem 1.2rem;
            box-shadow: var(--shadow);
            margin-bottom: 1.15rem;
            animation: panelReveal 520ms ease-out;
            transition: transform 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
            overflow: hidden;
        }}

        .sidebar-note {{
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            background: linear-gradient(180deg, var(--bg-panel), var(--bg-panel-soft));
            margin-top: 0.55rem;
        }}

        .sidebar-note strong {{
            display: block;
            margin-bottom: 0.35rem;
            color: var(--accent-strong);
        }}

        .metric-card {{
            border: 1px solid var(--border);
            background:
                linear-gradient(180deg, var(--bg-panel), var(--bg-panel-soft)),
                radial-gradient(circle at bottom right, rgba(240, 200, 110, 0.04), transparent 24%);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            min-height: 132px;
            box-shadow: var(--shadow);
            animation: panelReveal 560ms ease-out;
            transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
        }}

        .panel-card:hover,
        .metric-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(201, 169, 100, 0.38);
        }}

        .metric-label {{
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: var(--muted);
            margin-bottom: 0.85rem;
        }}

        .metric-value {{
            font-size: 1.78rem;
            font-weight: 800;
            color: var(--accent-strong);
            margin-bottom: 0.45rem;
        }}

        .metric-caption {{
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.55;
        }}

        .insight-card {{
            border-left: 3px solid var(--accent-strong);
            padding: 1rem 1rem 1rem 1.05rem;
            border-radius: 16px;
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(240, 200, 110, 0.02));
            margin-bottom: 0.85rem;
        }}

        .insight-card strong {{
            color: var(--accent-strong);
            display: block;
            margin-bottom: 0.3rem;
        }}

        .subtle-note {{
            color: var(--muted);
            font-size: 0.93rem;
            line-height: 1.62;
        }}

        .forecast-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.9rem;
            margin-top: 0.75rem;
        }}

        .forecast-tile {{
            border: 1px solid var(--border);
            border-radius: 16px;
            background: linear-gradient(180deg, var(--bg-panel), var(--bg-panel-soft));
            padding: 0.95rem 1rem;
        }}

        .chart-shell {{
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 0.85rem;
            background: linear-gradient(180deg, var(--chart-bg), var(--bg-panel-soft));
            margin-top: 0.25rem;
        }}

        .forecast-label {{
            font-size: 0.76rem;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 0.45rem;
        }}

        .forecast-value {{
            font-size: 1.02rem;
            font-weight: 700;
            color: var(--text);
        }}

        [data-testid="stTextInputRoot"],
        [data-testid="stFileUploader"],
        [data-testid="stRadio"],
        [data-testid="stSegmentedControl"],
        [data-testid="stButton"] {{
            animation: fieldReveal 260ms ease-out;
        }}

        [data-testid="stFileUploader"] section,
        [data-testid="stTextInputRoot"] > div > div,
        [data-testid="stTextInputRoot"] input {{
            transition: border-color 180ms ease, box-shadow 180ms ease, background-color 180ms ease;
            background: var(--input-bg) !important;
            color: var(--text) !important;
        }}

        [data-testid="stTextInputRoot"] input::placeholder {{
            color: var(--muted) !important;
            opacity: 1 !important;
        }}

        [data-testid="stFileUploader"]:hover section,
        [data-testid="stTextInputRoot"] input:focus,
        [data-testid="stTextInputRoot"] input:hover {{
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 1px var(--accent) inset;
        }}

        [data-testid="stFileUploader"] section {{
            border-radius: 18px !important;
            border: 1px dashed var(--border) !important;
        }}

        [data-testid="stSegmentedControl"] {{
            background: transparent !important;
        }}

        [data-testid="stSegmentedControl"] [role="radiogroup"] {{
            background: var(--widget-bg) !important;
            border: 1px solid var(--border) !important;
            border-radius: 999px !important;
            padding: 0.2rem !important;
        }}

        [data-testid="stSegmentedControl"] [role="radio"] {{
            color: var(--widget-text) !important;
            border-radius: 999px !important;
        }}

        [data-testid="stSegmentedControl"] [aria-checked="true"] {{
            background: var(--widget-selected-bg) !important;
            color: var(--text) !important;
        }}

        [data-testid="stRadio"] [role="radiogroup"] {{
            gap: 0.55rem;
        }}

        [data-testid="stRadio"] [role="radio"] {{
            background: var(--widget-bg) !important;
            border: 1px solid var(--border) !important;
            border-radius: 999px !important;
            padding: 0.35rem 0.85rem !important;
            color: var(--widget-text) !important;
        }}

        [data-testid="stRadio"] [aria-checked="true"] {{
            background: var(--widget-selected-bg) !important;
            border-color: var(--accent) !important;
        }}

        [data-testid="stHorizontalBlock"] > div {{
            animation: panelReveal 480ms ease-out;
        }}

        [data-testid="stTabs"] {{
            margin-top: 0.2rem;
        }}

        [data-testid="stTabs"] [role="tablist"] {{
            gap: 0.5rem;
            margin-bottom: 0.85rem;
        }}

        [data-testid="stTabs"] [role="tab"] {{
            border-radius: 999px;
            padding: 0.55rem 0.95rem;
            border: 1px solid var(--border);
            background: var(--tab-bg);
        }}

        [data-testid="stDataFrame"],
        div[data-testid="stTable"] {{
            border-radius: 16px;
            border: 1px solid var(--border);
            background: linear-gradient(180deg, var(--table-bg), var(--table-bg-alt));
        }}

        [data-testid="stDataFrame"] > div {{
            background: linear-gradient(180deg, var(--table-bg), var(--table-bg-alt)) !important;
        }}

        [data-testid="stDataFrame"] [role="grid"],
        [data-testid="stDataFrame"] [role="rowgroup"],
        [data-testid="stDataFrame"] [role="columnheader"],
        [data-testid="stDataFrame"] [role="gridcell"] {{
            color: var(--text) !important;
        }}

        [data-testid="stDataFrame"] [role="columnheader"] {{
            font-weight: 700 !important;
            letter-spacing: 0.02em;
            background: rgba(255, 255, 255, 0.02) !important;
        }}

        [data-testid="stDataFrame"] [role="gridcell"] {{
            font-size: 0.93rem !important;
            background: transparent !important;
        }}

        [data-testid="stButton"] button,
        [data-testid="stDownloadButton"] button {{
            background: var(--button-bg) !important;
            color: var(--button-text) !important;
            border: none !important;
            border-radius: 14px !important;
            min-height: 2.8rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.02em;
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
            transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease;
        }}

        [data-testid="stButton"] button:hover,
        [data-testid="stDownloadButton"] button:hover {{
            transform: translateY(-1px);
            filter: brightness(1.03);
        }}

        [data-testid="stDownloadButton"] {{
            width: 100%;
        }}

        [data-testid="stMetric"] {{
            background: transparent !important;
        }}

        [data-testid="stMetric"] label,
        [data-testid="stMetric"] [data-testid="stMetricLabel"],
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: var(--text) !important;
        }}

        .status-note {{
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            background: rgba(255, 255, 255, 0.03);
            margin-top: 0.7rem;
            margin-bottom: 1rem;
        }}

        .status-note strong {{
            display: block;
            margin-bottom: 0.35rem;
            color: var(--accent-strong);
        }}
    </style>
    """


def inject_theme(mode: str) -> None:
    """Apply the selected dashboard theme."""
    st.markdown(build_theme_css(mode), unsafe_allow_html=True)


def get_chart_palette(mode: str) -> dict[str, str]:
    """Return chart colors for the active theme."""
    palette = THEME_PALETTES[mode]
    return {
        "bar": palette["chart_bar"],
        "bar_alt": palette["chart_bar_alt"],
        "line": palette["chart_line"],
        "grid": palette["chart_grid"],
        "axis": palette["chart_axis"],
    }


def format_chart_number(value: float) -> str:
    """Format numbers for chart labels and tooltips."""
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    if float(value).is_integer():
        return f"{int(value)}"
    return f"{value:.2f}"


def render_hero(has_results: bool) -> None:
    """Render the top hero section."""
    status_badges = [
        "Workbook ingestion",
        "Data cleaning",
        "Insight summary",
        "Forecast support",
    ]
    if has_results:
        status_badges.append("Results loaded")

    badge_markup = "".join(f'<span class="status-badge">{badge}</span>' for badge in status_badges)
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="eyebrow">Smart Excel Analysis</div>
            <h1 class="hero-title">NeuroSheet</h1>
            <p class="hero-copy">
                Analyze operational spreadsheets with a cleaner, more readable workflow.
                Load one or more Excel files, inspect the merged dataset, review key metrics,
                detect quality issues, and surface summary insights from a single workspace.
            </p>
            <div class="badge-row">{badge_markup}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def convert_dataframe_for_preview(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Convert datetime values into strings for a cleaner UI preview."""
    preview = dataframe.copy()
    for column in preview.columns:
        if pd.api.types.is_datetime64_any_dtype(preview[column]):
            preview[column] = preview[column].dt.strftime("%Y-%m-%d")
    return preview


def render_metric_card(label: str, value: str, caption: str) -> None:
    """Render one metric card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(title: str) -> None:
    """Render a themed section heading."""
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def dataframe_to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    """Convert a dataframe into CSV bytes for download."""
    export_frame = convert_dataframe_for_preview(dataframe)
    return export_frame.to_csv(index=False).encode("utf-8")


def sanitize_chart_labels(series: pd.Series) -> pd.Series:
    """Convert chart labels into readable text without NaN-style output."""
    cleaned = series.copy()
    cleaned = cleaned.where(~cleaned.isna(), "Unknown")
    return cleaned.astype(str)


def text_to_bytes(lines: list[str], prediction: dict[str, Any]) -> bytes:
    """Create a simple text report for download."""
    content: list[str] = ["NeuroSheet Report", ""]
    content.append("Insights")
    content.extend(f"- {line}" for line in lines)
    content.append("")
    content.append("Forecast")
    if prediction["available"]:
        content.append(f"- Method: {prediction['method']}")
        content.append(f"- Next label: {prediction['next_label']}")
        content.append(f"- Predicted value: {prediction['predicted_value']}")
        content.append(f"- Direction: {prediction['direction']}")
        content.append(f"- R2 score: {prediction['r2_score']}")
        content.append(f"- Confidence note: {prediction.get('confidence_note', 'Not available')}")
    else:
        content.append(f"- Status: {prediction['reason']}")
    content.append("")
    return "\n".join(content).encode("utf-8")


def build_forecast_guidance(results: dict[str, Any]) -> list[str]:
    """Create professional fallback guidance when forecasting is unavailable."""
    analysis = results["analysis"]
    metrics = analysis["summary_metrics"]
    suggestions: list[str] = []

    if metrics["numeric_column_count"] == 0:
        suggestions.append("Add at least one measurable numeric field such as sales, revenue, quantity, cost, or profit.")
    elif not metrics.get("target_column"):
        suggestions.append("Rename the main business metric clearly, for example sales_amount, revenue, total_cost, or profit.")

    if metrics["date_column_count"] == 0:
        suggestions.append("Include a date column to unlock time-based trend lines and future-value forecasting.")

    suggestions.append("Keep identifier fields such as customer number, postal code, or employee code separate from business measures.")
    suggestions.append("Once a valid metric and timeline exist, the forecast panel will project the next period automatically.")
    return suggestions


def load_showcase_dataset() -> dict[str, Any]:
    """Build a demo-ready dataset that exercises analysis, visuals, and forecasting."""
    months = pd.date_range("2024-01-01", periods=12, freq="MS")
    regions = ["Gotham Central", "North Harbor", "Metro East", "Old Town"]
    categories = ["Electronics", "Operations", "Healthcare", "Logistics"]
    products = ["Nova Hub", "Pulse Kit", "Vector Desk", "Aegis Pack"]
    base_sales = [42000, 46500, 49800, 54000, 58600, 61200, 64800, 68300, 72100, 76800, 80100, 84500]
    region_factor = {
        "Gotham Central": 1.18,
        "North Harbor": 1.04,
        "Metro East": 0.96,
        "Old Town": 0.88,
    }

    rows: list[dict[str, Any]] = []
    category_cycle = cycle(categories)
    product_cycle = cycle(products)

    for month_index, month in enumerate(months):
        for region_index, region in enumerate(regions):
            sales = round(base_sales[month_index] * region_factor[region] + region_index * 950)
            orders = 115 + month_index * 6 + region_index * 4
            cost = round(sales * (0.58 + region_index * 0.02))
            profit = sales - cost
            rows.append(
                {
                    "Date": month,
                    "Region": region,
                    "Category": next(category_cycle),
                    "Product": next(product_cycle),
                    "Sales": sales,
                    "Orders": orders,
                    "Cost": cost,
                    "Profit": profit,
                    "source_file": "showcase_dataset.xlsx",
                }
            )

    showcase_df = pd.DataFrame(rows)
    summary = {
        "files_found": 1,
        "files_loaded": 1,
        "loaded_file_names": ["showcase_dataset.xlsx"],
        "skipped_files": [],
        "total_rows_loaded": int(len(showcase_df)),
        "detected_columns": showcase_df.columns.tolist(),
    }
    return {
        "data": showcase_df,
        "summary": summary,
    }


def run_pipeline(
    source_mode: str,
    folder_path: str,
    uploaded_files: list[Any],
) -> dict[str, Any]:
    """Execute the full analysis pipeline for the selected input mode."""
    if source_mode == "Folder":
        load_result = load_excel_folder(folder_path)
    elif source_mode == "Showcase":
        load_result = load_showcase_dataset()
    else:
        load_result = load_uploaded_excel_files(uploaded_files)

    clean_result = clean_dataframe(load_result["data"])
    analysis_result = analyze_dataframe(clean_result["data"])
    insight_result = generate_insights(clean_result["data"], analysis_result)
    prediction_result = predict_trend(clean_result["data"])

    return {
        "load": load_result,
        "clean": clean_result,
        "analysis": analysis_result,
        "insights": insight_result,
        "prediction": prediction_result,
    }


def save_outputs(results: dict[str, Any]) -> dict[str, Any]:
    """Persist current results into the outputs directory."""
    return export_results(
        cleaned_data=results["clean"]["data"],
        load_summary=results["load"]["summary"],
        clean_summary=results["clean"]["summary"],
        analysis_result=results["analysis"],
        insights=results["insights"],
        prediction=results["prediction"],
        output_dir="outputs",
    )


def render_sidebar() -> tuple[str, str, list[Any], bool, str]:
    """Render sidebar controls and return the selected inputs."""
    st.sidebar.markdown('<div class="sidebar-workspace-title">Workspace</div>', unsafe_allow_html=True)
    appearance = st.sidebar.segmented_control(
        "Appearance",
        options=["Dark", "Light"],
        default=st.session_state.get("appearance_mode", "Dark"),
        key="appearance_mode",
    )

    st.sidebar.markdown("### Data Source")
    source_mode = st.sidebar.radio(
        "Mode",
        options=["Folder", "Upload", "Showcase"],
        horizontal=True,
        label_visibility="collapsed",
    )
    folder_path = ""
    uploaded_files: list[Any] = []

    if source_mode == "Folder":
        folder_path = st.sidebar.text_input("Folder path", value="data", placeholder="data")
        st.sidebar.caption("Point to a folder containing one or more `.xlsx` workbooks.")
    elif source_mode == "Showcase":
        st.sidebar.markdown(
            """
            <div class="sidebar-note">
                <strong>Showcase dataset</strong>
                Uses a built-in monthly business dataset with valid metric and date columns so prediction,
                timeline summary, and time-trend visuals can all be demonstrated reliably.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        uploaded_files = st.sidebar.file_uploader(
            "Excel files",
            type=["xlsx"],
            accept_multiple_files=True,
            help="Upload one or more workbooks to merge and analyze.",
        )

    run_clicked = st.sidebar.button("Analyze Data", type="primary", use_container_width=True)
    st.sidebar.markdown("### Workflow")
    st.sidebar.markdown(
        """
        <div class="sidebar-note">
            <strong>Suggested flow</strong>
            Load the workbook set, review the cleaned dataset, inspect the visual analysis, then export the result set.
        </div>
        """,
        unsafe_allow_html=True,
    )
    return source_mode, folder_path, uploaded_files, run_clicked, appearance


def render_empty_state() -> None:
    """Render the initial dashboard state before any analysis runs."""
    render_section_title("Ready")
    st.markdown(
        """
        <div class="panel-card">
            <p class="subtle-note">
                Select a folder or upload Excel files from the sidebar, then run the analysis to populate
                the preview tables, operational summary, insights, and forecast section.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_processing_overview(results: dict[str, Any]) -> None:
    """Render a summary of load and cleaning activity."""
    load_summary = results["load"]["summary"]
    clean_summary = results["clean"]["summary"]

    render_section_title("Processing Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            "Files accepted",
            format_value(load_summary["files_loaded"]),
            "Workbooks included in the merged dataset.",
        )
    with col2:
        render_metric_card(
            "Records ready",
            format_value(clean_summary["final_rows"]),
            "Rows available after cleanup and standardization.",
        )
    with col3:
        render_metric_card(
            "Duplicates removed",
            format_value(clean_summary["duplicate_rows_removed"]),
            "Repeated records removed from the final table.",
        )
    with col4:
        render_metric_card(
            "Missing values resolved",
            format_value(clean_summary["missing_values_before_fill"] - clean_summary["missing_values_after_fill"]),
            "Fields completed during the cleaning pass.",
        )

    skipped = load_summary["skipped_files"]
    if skipped:
        st.markdown(
            f"""
            <div class="status-note">
                <strong>Review required</strong>
                {len(skipped)} file(s) were skipped during ingestion.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(pd.DataFrame(skipped), use_container_width=True, hide_index=True)
    else:
        st.markdown(
            """
            <div class="status-note">
                <strong>Ingestion complete</strong>
                All discovered Excel files were processed successfully.
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_preview(results: dict[str, Any]) -> None:
    """Render raw and cleaned dataset previews."""
    render_section_title("Dataset Preview")
    cleaned_preview, raw_preview = st.tabs(["Cleaned dataset", "Merged raw dataset"])

    with cleaned_preview:
        st.dataframe(
            convert_dataframe_for_preview(results["clean"]["data"].head(50)),
            use_container_width=True,
            hide_index=True,
            height=360,
            row_height=36,
        )

    with raw_preview:
        st.dataframe(
            convert_dataframe_for_preview(results["load"]["data"].head(50)),
            use_container_width=True,
            hide_index=True,
            height=360,
            row_height=36,
        )


def render_analysis_dashboard(results: dict[str, Any], appearance: str) -> None:
    """Render analysis KPIs, grouped breakdowns, and trend information."""
    analysis = results["analysis"]
    metrics = analysis["summary_metrics"]
    chart_palette = get_chart_palette(appearance)

    render_section_title("Operational Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Rows", format_value(metrics["row_count"]), "Total records in the cleaned dataset.")
    with col2:
        render_metric_card("Columns", format_value(metrics["column_count"]), "Detected columns after normalization.")
    with col3:
        render_metric_card(
            "Numeric fields",
            format_value(metrics["numeric_column_count"]),
            "Columns available for measured analysis.",
        )
    with col4:
        render_metric_card(
            "Date fields",
            format_value(metrics["date_column_count"]),
            "Columns that can support trend-aware analytics.",
        )

    spotlight_col, totals_col = st.columns([1.1, 1.9])
    with spotlight_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("### Dataset Structure")
        st.markdown(
            f"""
            <p class="subtle-note">
                Primary metric: <strong>{metrics.get('target_column') or 'Not identified'}</strong><br>
                Grouping field: <strong>{metrics.get('group_column') or 'Not identified'}</strong><br>
                Timeline field: <strong>{metrics.get('date_column') or 'Not identified'}</strong>
            </p>
            """,
            unsafe_allow_html=True,
        )
        if "target_total" in metrics:
            st.metric("Metric total", format_value(metrics["target_total"]))
        if "target_average" in metrics:
            st.metric("Metric average", format_value(metrics["target_average"]))
        st.markdown("</div>", unsafe_allow_html=True)

    with totals_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("### Numeric Profile")
        if analysis["numeric_overview"]:
            numeric_frame = pd.DataFrame(analysis["numeric_overview"]).T.reset_index()
            numeric_frame.rename(columns={"index": "column"}, inplace=True)
            st.dataframe(
                convert_dataframe_for_preview(numeric_frame),
                use_container_width=True,
                hide_index=True,
                height=320,
                row_height=36,
            )
        else:
            st.info("No usable numeric measures are available in the current dataset.")
        st.markdown("</div>", unsafe_allow_html=True)

    grouped_col, trend_col = st.columns(2)
    with grouped_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("### Group Summary Table")
        grouped = analysis["grouped_summary"]
        if not grouped.empty:
            st.dataframe(
                convert_dataframe_for_preview(grouped),
                use_container_width=True,
                hide_index=True,
                height=320,
                row_height=36,
            )
        else:
            st.info("A reliable grouping field was not detected for grouped analysis.")
        st.markdown("</div>", unsafe_allow_html=True)

    with trend_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("### Timeline Summary Table")
        trend = analysis["trend_summary"]
        if not trend.empty:
            st.dataframe(
                convert_dataframe_for_preview(trend),
                use_container_width=True,
                hide_index=True,
                height=320,
                row_height=36,
            )
        else:
            st.info("Timeline analysis is unavailable because no valid date field was detected.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_visual_analytics(results: dict[str, Any], appearance: str) -> None:
    """Render phase 8 visual analytics."""
    analysis = results["analysis"]
    grouped = analysis["grouped_summary"]
    trend = analysis["trend_summary"]
    chart_palette = get_chart_palette(appearance)

    render_section_title("Visual Analytics")
    comparison_col, share_col = st.columns(2)

    with comparison_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("### Group Comparison")
        if not grouped.empty:
            chart_value = "total_value" if "total_value" in grouped.columns else "record_count"
            category_column = grouped.columns[0]
            chart_source = grouped[[category_column, chart_value]].copy()
            chart_source = chart_source[chart_source[chart_value].fillna(0) > 0].copy()
            chart_source[category_column] = sanitize_chart_labels(chart_source[category_column])
            chart_source = chart_source.head(10)
        else:
            chart_source = pd.DataFrame()

        if not chart_source.empty:
            bar_chart = (
                alt.Chart(chart_source)
                .mark_bar(
                    cornerRadiusTopRight=7,
                    cornerRadiusBottomRight=7,
                    color=chart_palette["bar"],
                    size=24,
                )
                .encode(
                    x=alt.X(
                        f"{chart_value}:Q",
                        title=chart_value.replace("_", " ").title(),
                        axis=alt.Axis(labelExpr="datum.value >= 1000000 ? format(datum.value/1000000, '.1f') + 'M' : datum.value >= 1000 ? format(datum.value/1000, '.1f') + 'K' : datum.value"),
                    ),
                    y=alt.Y(f"{category_column}:N", sort="-x", title=category_column.replace("_", " ").title()),
                    tooltip=[
                        alt.Tooltip(f"{category_column}:N", title=category_column.replace("_", " ").title()),
                        alt.Tooltip(f"{chart_value}:Q", title=chart_value.replace("_", " ").title(), format=",.2f"),
                    ],
                )
                .properties(height=max(250, len(chart_source) * 34))
                .configure_view(stroke=None)
                .configure_axis(
                    labelColor=chart_palette["axis"],
                    titleColor=chart_palette["axis"],
                    gridColor=chart_palette["grid"],
                    domainColor=chart_palette["grid"],
                    tickColor=chart_palette["grid"],
                )
            )
            st.markdown('<div class="chart-shell">', unsafe_allow_html=True)
            st.altair_chart(bar_chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Group comparison becomes available when a grouping field is detected.")
        st.markdown("</div>", unsafe_allow_html=True)

    with share_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown("### Contribution Share")
        if not grouped.empty:
            share_value = "total_value" if "total_value" in grouped.columns else "record_count"
            category_column = grouped.columns[0]
            share_source = grouped[[category_column, share_value]].copy()
            share_source = share_source[share_source[share_value].fillna(0) > 0].head(6)
            share_source[category_column] = sanitize_chart_labels(share_source[category_column])
        else:
            share_source = pd.DataFrame()

        if not share_source.empty:
            share_chart = (
                alt.Chart(share_source)
                .mark_arc(innerRadius=60, outerRadius=115)
                .encode(
                    theta=alt.Theta(f"{share_value}:Q"),
                    color=alt.Color(
                        f"{category_column}:N",
                        scale=alt.Scale(range=[
                            chart_palette["bar"],
                            chart_palette["bar_alt"],
                            chart_palette["line"],
                            "#e0b95f",
                            "#7f5a16",
                            "#d8c8a4",
                        ]),
                        legend=alt.Legend(title=category_column.replace("_", " ").title(), labelColor=chart_palette["axis"], titleColor=chart_palette["axis"]),
                    ),
                    tooltip=[
                        alt.Tooltip(f"{category_column}:N", title=category_column.replace("_", " ").title()),
                        alt.Tooltip(f"{share_value}:Q", title=share_value.replace("_", " ").title(), format=",.2f"),
                    ],
                )
                .properties(height=320)
                .configure_view(stroke=None)
            )
            st.markdown('<div class="chart-shell">', unsafe_allow_html=True)
            st.altair_chart(share_chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Contribution share is shown when grouped analysis data is available.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("### Time Trend")
    if not trend.empty:
        y_column = "total_value" if "total_value" in trend.columns else "record_count"
        time_column = trend.columns[0]
        trend_source = trend[[time_column, y_column]].copy()
        trend_source = trend_source[trend_source[y_column].notna()].copy()
        line_chart = (
            alt.Chart(trend_source)
            .mark_line(color=chart_palette["line"], strokeWidth=3, point=alt.OverlayMarkDef(size=70))
            .encode(
                x=alt.X(f"{time_column}:T", title=time_column.replace("_", " ").title()),
                y=alt.Y(
                    f"{y_column}:Q",
                    title=y_column.replace("_", " ").title(),
                    axis=alt.Axis(labelExpr="datum.value >= 1000000 ? format(datum.value/1000000, '.1f') + 'M' : datum.value >= 1000 ? format(datum.value/1000, '.1f') + 'K' : datum.value"),
                ),
                tooltip=[
                    alt.Tooltip(f"{time_column}:T", title=time_column.replace("_", " ").title()),
                    alt.Tooltip(f"{y_column}:Q", title=y_column.replace("_", " ").title(), format=",.2f"),
                ],
            )
            .configure_view(stroke=None)
            .configure_axis(
                labelColor=chart_palette["axis"],
                titleColor=chart_palette["axis"],
                gridColor=chart_palette["grid"],
                domainColor=chart_palette["grid"],
                tickColor=chart_palette["grid"],
            )
            .properties(height=340)
        )
        st.markdown('<div class="chart-shell">', unsafe_allow_html=True)
        st.altair_chart(line_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Time trend visualization requires a valid date field in the dataset.")
    st.markdown("</div>", unsafe_allow_html=True)


def render_insight_section(results: dict[str, Any]) -> None:
    """Render human-readable insights."""
    render_section_title("Key Findings")
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    for index, insight in enumerate(results["insights"], start=1):
        st.markdown(
            f"""
            <div class="insight-card">
                <strong>Finding {index}</strong>
                <div>{insight}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_prediction_section(results: dict[str, Any]) -> None:
    """Render the forecast output or a readiness panel."""
    prediction = results["prediction"]
    render_section_title("Forecast")
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    if prediction["available"]:
        st.markdown("### Forecast Outlook")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Next period", str(prediction["next_label"]))
        with col2:
            st.metric("Predicted value", format_value(prediction["predicted_value"]))
        with col3:
            st.metric("Direction", str(prediction["direction"]).title())

        st.caption(
            f"{prediction['method']} using {prediction['historical_points']} historical points "
            f"with R² score {prediction['r2_score']}. {prediction.get('confidence_note', '')}"
        )
        historical_data = prediction["historical_data"]
        if not historical_data.empty:
            st.dataframe(
                convert_dataframe_for_preview(historical_data),
                use_container_width=True,
                hide_index=True,
                height=320,
                row_height=36,
            )
    else:
        guidance = build_forecast_guidance(results)
        st.markdown("### Forecast Readiness")
        st.markdown(
            f"""
            <p class="subtle-note">
                A forecast was not generated for the current dataset. {prediction["reason"]}
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="forecast-grid">
                <div class="forecast-tile">
                    <div class="forecast-label">Current status</div>
                    <div class="forecast-value">Forecast unavailable</div>
                </div>
                <div class="forecast-tile">
                    <div class="forecast-label">Recommended input</div>
                    <div class="forecast-value">One business metric + one timeline field</div>
                </div>
                <div class="forecast-tile">
                    <div class="forecast-label">Examples</div>
                    <div class="forecast-value">Sales, revenue, quantity, orders, cost, profit</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("#### How to enable forecasting")
        for suggestion in guidance:
            st.markdown(f"- {suggestion}")

    st.markdown("</div>", unsafe_allow_html=True)


def render_export_section(results: dict[str, Any]) -> None:
    """Render download controls for the current dashboard state."""
    render_section_title("Exports")
    cleaned_data = results["clean"]["data"]
    insights = results["insights"]
    prediction = results["prediction"]

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    save_clicked = st.button("Save outputs to outputs folder", use_container_width=True)
    if save_clicked:
        try:
            st.session_state["export_result"] = save_outputs(results)
        except ExportError as error:
            st.session_state["export_result"] = {"status": "error", "message": str(error)}

    export_result = st.session_state.get("export_result")
    if export_result:
        if export_result["status"] == "success":
            st.markdown(
                f"""
                <div class="status-note">
                    <strong>Exports saved</strong>
                    CSV: {export_result['cleaned_data_path']}<br>
                    Report: {export_result['report_path']}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="status-note">
                    <strong>Export failed</strong>
                    {export_result['message']}
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download cleaned CSV",
            data=dataframe_to_csv_bytes(cleaned_data),
            file_name="neurosheet_cleaned_data.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "Download summary report",
            data=text_to_bytes(insights, prediction),
            file_name="neurosheet_report.txt",
            mime="text/plain",
            use_container_width=True,
        )


def main() -> None:
    """Run the Streamlit dashboard."""
    source_mode, folder_path, uploaded_files, run_clicked, appearance = render_sidebar()
    inject_theme(appearance)
    render_hero(has_results="results" in st.session_state)

    if run_clicked:
        try:
            with st.spinner("Analyzing workbook set..."):
                st.session_state["results"] = run_pipeline(
                    source_mode,
                    folder_path,
                    uploaded_files,
                )
        except (DataLoadError, DataCleaningError, DataAnalysisError, PredictionError, ValueError) as error:
            st.session_state.pop("results", None)
            st.error(str(error))
        except Exception as error:  # pragma: no cover - defensive UI guard.
            st.session_state.pop("results", None)
            st.error(f"Unexpected failure while running the pipeline: {error}")

    results = st.session_state.get("results")
    if not results:
        render_empty_state()
        return

    render_processing_overview(results)
    render_preview(results)
    render_analysis_dashboard(results, appearance)
    render_visual_analytics(results, appearance)
    render_insight_section(results)
    render_prediction_section(results)
    render_export_section(results)


if __name__ == "__main__":
    main()
