"""
ReviewSense - UI Theme & Design System
Linear / Vercel / Stripe-inspired Dark Theme System
"""

# Color Palette Constants
THEME_COLORS = {
    "bg_primary": "#0B0F19",
    "bg_secondary": "#111827",
    "bg_card": "#151C2C",
    "bg_elevated": "#1C2537",
    "accent_primary": "#8B7CFF",
    "accent_secondary": "#38BDF8",
    "positive": "#22C55E",
    "negative": "#F87171",
    "neutral": "#FBBF24",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "border_subtle": "#1E293B",
    "border_card": "rgba(255, 255, 255, 0.07)",
}

SENTIMENT_COLORS = {
    "positive": "#22C55E",
    "negative": "#F87171",
    "neutral": "#FBBF24",
}

ASPECT_COLORS = {
    "Quality": "#818CF8",   # Indigo
    "Shipping": "#38BDF8",  # Sky Blue
    "Price": "#F472B6",     # Rose Pink
}

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

/* Base Styles */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #F8FAFC;
}

h1, h2, h3, h4, .font-heading {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    letter-spacing: -0.02em;
}

/* App Background */
.stApp {
    background-color: #0B0F19;
    background-image: 
        radial-gradient(ellipse at 15% 0%, rgba(139, 124, 255, 0.05) 0%, transparent 50%),
        radial-gradient(ellipse at 85% 0%, rgba(56, 189, 248, 0.04) 0%, transparent 50%);
    background-attachment: fixed;
    color: #F8FAFC;
}

/* Sidebar Clean Styling */
[data-testid="stSidebar"] {
    background-color: #0B0F19 !important;
    border-right: 1px solid #1E293B !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.6rem;
}

/* Brand Header in Sidebar */
.brand-container {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 4px 16px 4px;
    border-bottom: 1px solid #1E293B;
    margin-bottom: 8px;
}

.brand-icon {
    width: 36px;
    height: 36px;
    border-radius: 9px;
    background: linear-gradient(135deg, #8B7CFF 0%, #6366F1 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 700;
    color: #0B0F19;
    box-shadow: 0 4px 12px rgba(139, 124, 255, 0.25);
}

.brand-text-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: -0.01em;
    line-height: 1.2;
}

.brand-text-subtitle {
    font-size: 11px;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 500;
}

/* Navigation Radio Styling */
[data-testid="stSidebar"] [data-testid="stRadio"] > label {
    display: none;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
    gap: 4px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    color: #94A3B8 !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    padding: 9px 12px !important;
    transition: all 0.15s ease-in-out;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #111827;
    color: #F8FAFC !important;
    border-color: #1E293B;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: #151C2C !important;
    color: #F8FAFC !important;
    font-weight: 600 !important;
    border-color: rgba(139, 124, 255, 0.35) !important;
    border-left: 3px solid #8B7CFF !important;
}

/* Main Top Header */
.top-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 0 24px 0;
    border-bottom: 1px solid #1E293B;
    margin-bottom: 24px;
}

.top-header-title {
    font-size: 24px;
    font-weight: 700;
    color: #F8FAFC;
    margin: 0;
}

.top-header-subtitle {
    font-size: 13.5px;
    color: #94A3B8;
    margin-top: 4px;
    margin-bottom: 0;
}

.status-badge-container {
    display: flex;
    align-items: center;
    gap: 8px;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.02em;
}

.status-pill-online {
    background: rgba(34, 197, 94, 0.1);
    color: #22C55E;
    border: 1px solid rgba(34, 197, 94, 0.25);
}

.status-pill-fallback {
    background: rgba(251, 191, 36, 0.1);
    color: #FBBF24;
    border: 1px solid rgba(251, 191, 36, 0.25);
}

.pulse-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: currentColor;
}

/* Modern Card System */
.saas-card {
    background: #151C2C;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 16px;
    transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
}

.saas-card:hover {
    border-color: rgba(139, 124, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}

.saas-card-static {
    background: #151C2C;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 16px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
}

/* KPI Cards */
.kpi-card {
    background: #151C2C;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    padding: 18px 20px;
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.kpi-card:hover {
    border-color: rgba(139, 124, 255, 0.35);
    transform: translateY(-2px);
}

.kpi-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.kpi-title {
    color: #94A3B8;
    font-size: 11.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.kpi-icon {
    font-size: 16px;
    opacity: 0.85;
}

.kpi-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1.1;
    letter-spacing: -0.02em;
    margin-bottom: 6px;
}

.kpi-subtext {
    font-size: 12px;
    color: #64748B;
    font-weight: 400;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Sentiment Badges */
.sentiment-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.sentiment-positive {
    background: rgba(34, 197, 94, 0.12);
    color: #22C55E;
    border: 1px solid rgba(34, 197, 94, 0.28);
}

.sentiment-negative {
    background: rgba(248, 113, 113, 0.12);
    color: #F87171;
    border: 1px solid rgba(248, 113, 113, 0.28);
}

.sentiment-neutral {
    background: rgba(251, 191, 36, 0.12);
    color: #FBBF24;
    border: 1px solid rgba(251, 191, 36, 0.28);
}

/* Aspect Tags */
.aspect-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    margin-right: 6px;
    margin-bottom: 4px;
}

.aspect-quality {
    background: rgba(129, 140, 248, 0.12);
    color: #818CF8;
    border: 1px solid rgba(129, 140, 248, 0.28);
}

.aspect-shipping {
    background: rgba(56, 189, 248, 0.12);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.28);
}

.aspect-price {
    background: rgba(244, 114, 182, 0.12);
    color: #F472B6;
    border: 1px solid rgba(244, 114, 182, 0.28);
}

.aspect-none {
    background: rgba(148, 163, 184, 0.08);
    color: #94A3B8;
    border: 1px solid rgba(148, 163, 184, 0.18);
}

/* Confidence Meter Bar */
.confidence-container {
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid #1E293B;
}

.confidence-header {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #94A3B8;
    margin-bottom: 6px;
}

.confidence-bar-bg {
    width: 100%;
    height: 7px;
    background: #1E293B;
    border-radius: 4px;
    overflow: hidden;
}

.confidence-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s ease;
}

/* Buttons */
.stButton > button {
    background: #8B7CFF !important;
    color: #0B0F19 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    transition: all 0.15s ease-in-out !important;
    box-shadow: 0 2px 8px rgba(139, 124, 255, 0.25) !important;
}

.stButton > button:hover {
    background: #9D91FF !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(139, 124, 255, 0.38) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

/* Secondary Button / Outline */
button[kind="secondary"] {
    background: #151C2C !important;
    color: #F8FAFC !important;
    border: 1px solid #1E293B !important;
    box-shadow: none !important;
}

button[kind="secondary"]:hover {
    background: #1C2537 !important;
    border-color: #334155 !important;
}

/* Input Fields & Text Area */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox div[data-baseweb="select"] {
    background-color: #111827 !important;
    border: 1px solid #1E293B !important;
    border-radius: 8px !important;
    color: #F8FAFC !important;
    font-size: 14px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #8B7CFF !important;
    box-shadow: 0 0 0 1px #8B7CFF !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1E293B;
    gap: 16px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #94A3B8 !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    padding: 10px 4px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
}

.stTabs [aria-selected="true"] {
    color: #8B7CFF !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #8B7CFF !important;
}

/* Metric Display override */
[data-testid="stMetric"] {
    background: #151C2C;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 10px;
    padding: 14px 16px;
}

[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-size: 12px !important;
}

[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
}

/* Clean Empty State */
.empty-state {
    text-align: center;
    padding: 48px 24px;
    background: #151C2C;
    border: 1px dashed #1E293B;
    border-radius: 12px;
    margin: 16px 0;
}

.empty-state-icon {
    font-size: 32px;
    margin-bottom: 12px;
    opacity: 0.7;
}

.empty-state-title {
    font-size: 16px;
    font-weight: 600;
    color: #F8FAFC;
    margin-bottom: 4px;
}

.empty-state-desc {
    font-size: 13px;
    color: #94A3B8;
    max-width: 400px;
    margin: 0 auto;
}

/* Presets Container */
.presets-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;
}

.preset-chip {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 6px;
    background: #151C2C;
    border: 1px solid #1E293B;
    color: #94A3B8;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s ease;
}

.preset-chip:hover {
    color: #F8FAFC;
    border-color: #8B7CFF;
    background: #1C2537;
}

/* Micro Footers & Dividers */
hr {
    border: none;
    border-top: 1px solid #1E293B !important;
    margin: 24px 0 !important;
}

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
"""
