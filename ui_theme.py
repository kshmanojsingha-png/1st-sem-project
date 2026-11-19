"""
ReviewSense - UI Theme & Design System (Ultra-Modern Premium Dark Edition)
Linear / Vercel / Stripe-inspired Dark Glassmorphism Design System
Configured for high-impact presentations and executive dashboard aesthetics
"""

# Color Palette Constants
THEME_COLORS = {
    "bg_primary": "#0B0F19",
    "bg_secondary": "#111827",
    "bg_card": "rgba(21, 28, 44, 0.75)",
    "bg_elevated": "rgba(28, 37, 55, 0.85)",
    "accent_primary": "#8B7CFF",
    "accent_secondary": "#38BDF8",
    "positive": "#22C55E",
    "negative": "#F87171",
    "neutral": "#FBBF24",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "border_subtle": "#1E293B",
    "border_card": "rgba(255, 255, 255, 0.08)",
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
/* -------------------------------------------------------------
   1. Typography & Base System Fonts (Offline-first, high performance)
------------------------------------------------------------- */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", Roboto, Helvetica, Arial, sans-serif;
    color: #F8FAFC;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Informational Paragraphs & Body Content (Projector / Presentation Optimized) */
p, span, li, label, .stMarkdown p, .stMarkdown span, .stMarkdown li {
    font-size: 16.5px;
    line-height: 1.65;
}

h1, h2, h3, h4, .font-heading {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif !important;
    letter-spacing: -0.025em;
    font-weight: 700;
}

/* -------------------------------------------------------------
   2. High-Performance Ambient Mesh Gradient (Optimized Zero-Lag)
------------------------------------------------------------- */
.stApp {
    background-color: #080C14;
    background-image: 
        radial-gradient(circle at 18% 12%, rgba(139, 124, 255, 0.10) 0%, transparent 45%),
        radial-gradient(circle at 82% 18%, rgba(56, 189, 248, 0.08) 0%, transparent 42%),
        radial-gradient(circle at 50% 85%, rgba(16, 185, 129, 0.06) 0%, transparent 50%),
        linear-gradient(180deg, #080C14 0%, #0D1322 100%);
    background-attachment: fixed;
    color: #F8FAFC;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #0B0F19;
}
::-webkit-scrollbar-thumb {
    background: #1E293B;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}
::-webkit-scrollbar-thumb:hover {
    background: #334155;
}

/* -------------------------------------------------------------
   3. Sidebar - Frosted Glass & Navigation Glow
------------------------------------------------------------- */
[data-testid="stSidebar"] {
    background: rgba(11, 15, 25, 0.88) !important;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.65rem;
}

/* Brand Header */
.brand-container {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 6px 18px 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 12px;
}

.brand-icon {
    width: 42px;
    height: 42px;
    border-radius: 11px;
    background: linear-gradient(135deg, #8B7CFF 0%, #4F46E5 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 800;
    color: #FFFFFF;
    box-shadow: 0 4px 16px rgba(139, 124, 255, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.brand-container:hover .brand-icon {
    transform: rotate(8deg) scale(1.08);
}

.brand-text-title {
    font-size: 19px !important;
    font-weight: 800 !important;
    color: #F8FAFC;
    letter-spacing: -0.02em;
    line-height: 1.2;
    background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.brand-text-subtitle {
    font-size: 12.5px !important;
    color: #8B7CFF;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin-top: 1px;
}

/* Sidebar Radio Navigation Items */
[data-testid="stSidebar"] [data-testid="stRadio"] > label {
    display: none;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
    gap: 6px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid transparent;
    border-radius: 9px;
    color: #94A3B8 !important;
    font-size: 15.5px !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    align-items: center;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255, 255, 255, 0.05);
    color: #F8FAFC !important;
    border-color: rgba(255, 255, 255, 0.1);
    transform: translateX(3px);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(139, 124, 255, 0.18) 0%, rgba(139, 124, 255, 0.05) 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: 1px solid rgba(139, 124, 255, 0.35) !important;
    border-left: 3px solid #8B7CFF !important;
    box-shadow: 0 4px 12px rgba(139, 124, 255, 0.15);
    transform: translateX(2px);
}

/* -------------------------------------------------------------
   4. Top Header & Live Status Indicators
------------------------------------------------------------- */
.top-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0 22px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 24px;
    position: relative;
}

.top-header::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 80px;
    height: 2px;
    background: linear-gradient(90deg, #8B7CFF 0%, transparent 100%);
}

.top-header-title {
    font-size: 26px !important;
    font-weight: 800 !important;
    color: #F8FAFC;
    margin: 0;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.top-header-subtitle {
    font-size: 16px !important;
    color: #94A3B8;
    margin-top: 5px;
    margin-bottom: 0;
    line-height: 1.5;
}

.status-badge-container {
    display: flex;
    align-items: center;
    gap: 10px;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px !important;
    border-radius: 20px;
    font-size: 14.5px !important;
    font-weight: 600;
    letter-spacing: 0.02em;
    backdrop-filter: blur(10px);
    transition: all 0.2s ease;
}

.status-pill-online {
    background: rgba(34, 197, 94, 0.12);
    color: #22C55E;
    border: 1px solid rgba(34, 197, 94, 0.3);
    box-shadow: 0 2px 10px rgba(34, 197, 94, 0.15);
}

.status-pill-fallback {
    background: rgba(251, 191, 36, 0.12);
    color: #FBBF24;
    border: 1px solid rgba(251, 191, 36, 0.3);
    box-shadow: 0 2px 10px rgba(251, 191, 36, 0.15);
}

@keyframes pulseRadar {
    0% {
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
    }
    70% {
        box-shadow: 0 0 0 8px rgba(34, 197, 94, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
    }
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: currentColor;
    animation: pulseRadar 2s infinite cubic-bezier(0.4, 0, 0.6, 1);
}

/* -------------------------------------------------------------
   5. Glassmorphism Cards & Enterprise Containers
------------------------------------------------------------- */
.saas-card {
    background: rgba(21, 28, 44, 0.75);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 24px 26px;
    margin-bottom: 20px;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.06);
    position: relative;
    overflow: hidden;
}

.saas-card:hover {
    border-color: rgba(139, 124, 255, 0.38);
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.45), 0 0 20px rgba(139, 124, 255, 0.12);
}

.saas-card-static {
    background: rgba(21, 28, 44, 0.75);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 24px 26px;
    margin-bottom: 20px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

/* -------------------------------------------------------------
   6. Executive KPI Cards with Shimmer & Accents
------------------------------------------------------------- */
.kpi-card {
    background: rgba(21, 28, 44, 0.78);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #8B7CFF 0%, #38BDF8 100%);
    opacity: 0.6;
    transition: opacity 0.25s ease;
}

.kpi-card:hover {
    border-color: rgba(139, 124, 255, 0.4);
    transform: translateY(-3px);
    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.4), 0 0 16px rgba(139, 124, 255, 0.1);
}

.kpi-card:hover::before {
    opacity: 1;
}

.kpi-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.kpi-title {
    color: #94A3B8;
    font-size: 14.5px !important;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

.kpi-icon {
    font-size: 22px;
    opacity: 0.9;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

.kpi-value {
    font-size: 32px !important;
    font-weight: 800 !important;
    color: #F8FAFC;
    line-height: 1.15;
    letter-spacing: -0.03em;
    margin-bottom: 8px;
}

.kpi-subtext {
    font-size: 15px !important;
    color: #94A3B8;
    font-weight: 400;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* -------------------------------------------------------------
   7. Sentiment & Aspect Tags / Badges
------------------------------------------------------------- */
.sentiment-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px !important;
    border-radius: 8px;
    font-size: 15px !important;
    font-weight: 700;
    letter-spacing: 0.02em;
    backdrop-filter: blur(8px);
}

.sentiment-positive {
    background: rgba(34, 197, 94, 0.14);
    color: #22C55E;
    border: 1px solid rgba(34, 197, 94, 0.35);
    box-shadow: 0 2px 8px rgba(34, 197, 94, 0.15);
}

.sentiment-negative {
    background: rgba(248, 113, 113, 0.14);
    color: #F87171;
    border: 1px solid rgba(248, 113, 113, 0.35);
    box-shadow: 0 2px 8px rgba(248, 113, 113, 0.15);
}

.sentiment-neutral {
    background: rgba(251, 191, 36, 0.14);
    color: #FBBF24;
    border: 1px solid rgba(251, 191, 36, 0.35);
    box-shadow: 0 2px 8px rgba(251, 191, 36, 0.15);
}

.aspect-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 15px !important;
    border-radius: 8px;
    font-size: 15px !important;
    font-weight: 600;
    margin-right: 8px;
    margin-bottom: 8px;
    backdrop-filter: blur(8px);
    transition: all 0.2s ease;
}

.aspect-quality {
    background: rgba(129, 140, 248, 0.14);
    color: #A5B4FC;
    border: 1px solid rgba(129, 140, 248, 0.35);
    box-shadow: 0 2px 8px rgba(129, 140, 248, 0.15);
}

.aspect-shipping {
    background: rgba(56, 189, 248, 0.14);
    color: #7DD3FC;
    border: 1px solid rgba(56, 189, 248, 0.35);
    box-shadow: 0 2px 8px rgba(56, 189, 248, 0.15);
}

.aspect-price {
    background: rgba(244, 114, 182, 0.14);
    color: #F472B6;
    border: 1px solid rgba(244, 114, 182, 0.35);
    box-shadow: 0 2px 8px rgba(244, 114, 182, 0.15);
}

.aspect-none {
    background: rgba(148, 163, 184, 0.08);
    color: #94A3B8;
    border: 1px solid rgba(148, 163, 184, 0.2);
}

/* -------------------------------------------------------------
   8. Confidence Meter & Progress Indicators
------------------------------------------------------------- */
.confidence-container {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.confidence-header {
    display: flex;
    justify-content: space-between;
    font-size: 15.5px !important;
    color: #94A3B8;
    margin-bottom: 10px;
}

.confidence-bar-bg {
    width: 100%;
    height: 10px;
    background: rgba(30, 41, 59, 0.8);
    border-radius: 6px;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.4);
}

.confidence-bar-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

/* -------------------------------------------------------------
   9. Buttons - Modern Gradient & Glowing Interactivity
------------------------------------------------------------- */
.stButton > button {
    background: linear-gradient(135deg, #8B7CFF 0%, #6366F1 100%) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 4px 16px rgba(139, 124, 255, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
    cursor: pointer !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #9E91FF 0%, #7579F3 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(139, 124, 255, 0.48), 0 0 12px rgba(139, 124, 255, 0.3) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

button[kind="secondary"] {
    background: rgba(21, 28, 44, 0.85) !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    font-size: 15.5px !important;
}

button[kind="secondary"]:hover {
    background: rgba(30, 41, 59, 0.95) !important;
    border-color: rgba(139, 124, 255, 0.4) !important;
    color: #8B7CFF !important;
}

/* -------------------------------------------------------------
   10. Form Controls, Inputs & Selectors
------------------------------------------------------------- */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox div[data-baseweb="select"] {
    background-color: rgba(17, 24, 39, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #F8FAFC !important;
    font-size: 16.5px !important;
    line-height: 1.55 !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #8B7CFF !important;
    box-shadow: 0 0 0 2px rgba(139, 124, 255, 0.25) !important;
    background-color: rgba(17, 24, 39, 0.95) !important;
}

.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stNumberInput label,
.stRadio label {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #E2E8F0 !important;
}

/* -------------------------------------------------------------
   11. Tabs Styling
------------------------------------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    gap: 20px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #94A3B8 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 12px 8px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #F8FAFC !important;
}

.stTabs [aria-selected="true"] {
    color: #8B7CFF !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #8B7CFF !important;
}

/* -------------------------------------------------------------
   12. Metrics & Tables
------------------------------------------------------------- */
[data-testid="stMetric"] {
    background: rgba(21, 28, 44, 0.75);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 18px 20px;
}

[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-size: 14.5px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-weight: 800 !important;
}

[data-testid="stDataFrame"], [data-testid="stTable"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 52px 28px;
    background: rgba(21, 28, 44, 0.65);
    border: 1.5px dashed rgba(255, 255, 255, 0.14);
    border-radius: 14px;
    margin: 20px 0;
}

.empty-state-icon {
    font-size: 38px;
    margin-bottom: 14px;
    opacity: 0.85;
}

.empty-state-title {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #F8FAFC;
    margin-bottom: 8px;
}

.empty-state-desc {
    font-size: 16px !important;
    color: #94A3B8;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Preset Chips */
.presets-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 14px;
}

.preset-chip {
    display: inline-block;
    padding: 8px 16px !important;
    border-radius: 8px;
    background: rgba(21, 28, 44, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #94A3B8;
    font-size: 15px !important;
    cursor: pointer;
    transition: all 0.2s ease;
}

.preset-chip:hover {
    color: #F8FAFC;
    border-color: #8B7CFF;
    background: rgba(30, 41, 59, 0.9);
}

/* Micro Dividers */
hr {
    border: none;
    border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
    margin: 28px 0 !important;
}

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
"""
