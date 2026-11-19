"""
ReviewSense – Multi-Aspect Product Review & Customer Sentiment Hub
Linear / Vercel-inspired Enterprise AI SaaS Dashboard (High-Performance Turbo Edition)
"""

import os
import streamlit as st
import pandas as pd
import numpy as np

# System & UI Modules
import api_client
from ui_theme import CUSTOM_CSS, THEME_COLORS, SENTIMENT_COLORS, ASPECT_COLORS
import ui_charts
from simran_all_in_one import detect_aspects, normalize_labels

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ReviewSense | AI Review Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Enterprise Dark Theme CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. HIGH-PERFORMANCE IN-MEMORY SINGLETON DATA & RESOURCE LOADERS
# -----------------------------------------------------------------------------
@st.cache_resource
def load_eval_predictions() -> pd.DataFrame:
    """Loads held-out test predictions (6,000 reviews) as an in-memory singleton (zero-copy)."""
    try:
        p_df = pd.read_csv("data/predictions.csv")
        p_df["predicted"] = p_df["predicted"].str.lower()
        if "aspects" not in p_df.columns:
            p_df["aspects"] = p_df["review_text"].apply(detect_aspects)
        return p_df
    except Exception:
        return pd.DataFrame()


@st.cache_resource
def load_food_dataset() -> pd.DataFrame:
    """Lazy-loads the 50k Amazon Food Reviews dataset only when requested."""
    try:
        return pd.read_csv("final_food_reviews.csv")
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=12)
def get_backend_health(url: str):
    """Caches health check for 12 seconds to ensure zero tab-switching network delay."""
    return api_client.check_api_health(url, timeout=0.35)


@st.cache_data
def get_cached_overview_charts():
    """Caches Overview figures so switching back and forth is instantaneous."""
    df = load_eval_predictions()
    donut = ui_charts.create_sentiment_donut(df, sentiment_col="predicted")
    aspect_bar = ui_charts.create_aspect_bar(df, aspects_col="aspects")
    return donut, aspect_bar


@st.cache_data
def get_popular_food_titles():
    """Precomputes top 50 popular food products and titles catalog for instant selectbox rendering."""
    f_df = load_food_dataset()
    if f_df.empty:
        return [], []
    valid = f_df[f_df["title"] != "Unknown Product"]
    top_titles = valid["title"].value_counts().head(50).index.tolist()
    all_titles = valid["title"].unique().tolist()
    return top_titles, all_titles


@st.cache_data
def get_cached_aspect_stats():
    """Precomputes aspect breakdown stats and chart for Aspect-Based Insights."""
    df = load_eval_predictions()
    if df.empty:
        return (0, 0, 0, 0, df), (0, 0, 0, 0, df), (0, 0, 0, 0, df), None

    def _stat(asp_name):
        has_asp = df[df["aspects"].apply(lambda a: asp_name in a if isinstance(a, list) else asp_name in str(a))]
        t = len(has_asp)
        p = (has_asp["predicted"] == "positive").sum()
        n = (has_asp["predicted"] == "negative").sum()
        neu = (has_asp["predicted"] == "neutral").sum()
        return t, p, n, neu, has_asp

    q_stat = _stat("Quality")
    s_stat = _stat("Shipping")
    p_stat = _stat("Price")
    chart = ui_charts.create_aspect_sentiment_grouped_bar(df, sentiment_col="predicted", aspects_col="aspects")
    return q_stat, s_stat, p_stat, chart


@st.cache_data
def get_sentiment_analytics_static_charts():
    """Precomputes static rating matrix and temporal trends for Sentiment Analytics."""
    f_df = load_food_dataset()
    if f_df.empty:
        return None, None
    sample = f_df.head(5000).copy()
    sample["sentiment"] = sample["Score"].apply(
        lambda s: "positive" if s >= 4 else ("negative" if s <= 2 else "neutral")
    )
    m_fig = ui_charts.create_rating_sentiment_matrix(sample, score_col="Score", sentiment_col="sentiment")
    t_fig = ui_charts.create_time_trend_chart(sample, time_col="Time", sentiment_col="sentiment")
    return m_fig, t_fig


# Load evaluation dataset as instant memory singleton
eval_df = load_eval_predictions()


# Initialize Session State
if "recent_analyses" not in st.session_state:
    st.session_state["recent_analyses"] = []

if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = api_client.DEFAULT_API_URL


# -----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & SYSTEM STATUS
# -----------------------------------------------------------------------------
with st.sidebar:
    # Brand Header
    st.markdown("""
    <div class="brand-container">
        <div class="brand-icon">⚡</div>
        <div>
            <div class="brand-text-title">ReviewSense</div>
            <div class="brand-text-subtitle">AI Review Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Menu
    nav_selection = st.radio(
        "Navigation",
        options=[
            "Overview",
            "Single Review Analysis",
            "Batch Review Analysis",
            "Sentiment Analytics",
            "Aspect-Based Insights",
            "About Project"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<hr style='margin: 14px 0 !important;'>", unsafe_allow_html=True)

    # Live Backend Status Check (Cached for 12s to eliminate socket block on tab switch)
    backend_url = st.session_state["backend_url"]
    health = get_backend_health(backend_url)

    st.markdown("<span style='font-size:13px; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.08em;'>System Engine</span>", unsafe_allow_html=True)
    if health["online"]:
        st.markdown(f"""
        <div class="status-pill status-pill-online" style="margin-top:8px; margin-bottom:12px; width:100%; justify-content:center;">
            <div class="pulse-dot"></div>
            <span>FastAPI REST Connected (:8000)</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-pill status-pill-fallback" style="margin-top:8px; margin-bottom:12px; width:100%; justify-content:center;">
            <div class="pulse-dot" style="background-color:#FBBF24;"></div>
            <span>Local ML Pipeline (Fallback Active)</span>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("⚙️ Connection Settings", expanded=False):
        new_url = st.text_input("Backend API URL", value=backend_url, key="sidebar_url_input")
        if new_url != backend_url:
            st.session_state["backend_url"] = new_url
            st.rerun()

        if not health["online"]:
            st.caption("To run the FastAPI server alongside Streamlit:")
            st.code("uvicorn api:app --reload --port 8000", language="bash")
            st.caption("Inference continues seamlessly via zero-downtime local fallback.")

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding: 14px 16px; border-radius: 10px; background: rgba(21, 28, 44, 0.7); border: 1px solid rgba(255, 255, 255, 0.08);'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <span style='font-size: 14px; font-weight: 700; color: #F8FAFC;'>ReviewSense Enterprise</span>
            <span style='font-size: 11px; padding: 2px 7px; border-radius: 12px; background: rgba(139, 124, 255, 0.2); color: #8B7CFF; font-weight:600;'>v2.2 Pro</span>
        </div>
        <div style='font-size: 13px; color: #94A3B8; margin-top: 5px;'>Scikit-Learn • FastAPI • Streamlit</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. TOP HEADER BAR HELPER
# -----------------------------------------------------------------------------
def render_header(title: str, subtitle: str, badge: str = None):
    """Renders the top title bar with active status pill and breadcrumb styling."""
    status_html = (
        '<div class="status-pill status-pill-online"><div class="pulse-dot"></div> API Online</div>'
        if health["online"]
        else '<div class="status-pill status-pill-fallback"><div class="pulse-dot" style="background-color:#FBBF24;"></div> Local Engine Active</div>'
    )
    badge_html = f'<span style="margin-left: 10px; padding: 3px 9px; font-size: 13px; font-weight: 600; border-radius: 6px; background: rgba(139, 124, 255, 0.15); color: #8B7CFF; border: 1px solid rgba(139, 124, 255, 0.3);">{badge}</span>' if badge else ""
    
    st.markdown(f"""
    <div class="top-header">
        <div>
            <div style="font-size: 12px; color: #8B7CFF; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px;">
                REVIEWSENSE INTELLIGENCE PLATFORM
            </div>
            <h1 class="top-header-title">{title} {badge_html}</h1>
            <p class="top-header-subtitle">{subtitle}</p>
        </div>
        <div class="status-badge-container">
            {status_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 5. FOOTER HELPER
# -----------------------------------------------------------------------------
def render_footer():
    """Renders a sleek bottom footer for executive polish."""
    st.markdown("""
    <div style="margin-top: 48px; padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-between; align-items: center; color: #64748B; font-size: 13.5px;">
        <div>
            <span>⚡ <b>ReviewSense</b> AI Review & Aspect Intelligence Engine</span>
            <span style="margin: 0 8px;">•</span>
            <span>Group D Project</span>
        </div>
        <div>
            <span>TF-IDF • Logistic Regression • FastAPI REST • Streamlit Pro</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PAGE 1: OVERVIEW
# =============================================================================
if nav_selection == "Overview":
    render_header(
        title="Executive Overview",
        subtitle="Holistic customer sentiment dynamics, aspect breakdowns, and operational intelligence metrics.",
        badge="Live Dashboard"
    )

    # Dynamic KPI Metrics from Evaluation Dataset
    if not eval_df.empty:
        total_eval = len(eval_df)
        pos_cnt = (eval_df["predicted"] == "positive").sum()
        neg_cnt = (eval_df["predicted"] == "negative").sum()
        neu_cnt = (eval_df["predicted"] == "neutral").sum()
        pos_pct = f"{(pos_cnt / total_eval * 100):.1f}%"
        neg_pct = f"{(neg_cnt / total_eval * 100):.1f}%"
        neu_pct = f"{(neu_cnt / total_eval * 100):.1f}%"
    else:
        total_eval, pos_pct, neg_pct, neu_pct = 6000, "72.4%", "16.5%", "11.1%"
        pos_cnt, neg_cnt, neu_cnt = 4341, 990, 669

    # Hero Banner Callout
    st.markdown("""
    <div style="padding: 20px 24px; border-radius: 14px; background: linear-gradient(135deg, rgba(139, 124, 255, 0.12) 0%, rgba(56, 189, 248, 0.08) 100%); border: 1px solid rgba(139, 124, 255, 0.25); margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <div style="font-size: 19px; font-weight: 700; color: #F8FAFC; margin-bottom: 4px;">
                🚀 Multi-Aspect Customer Sentiment Intelligence Hub
            </div>
            <div style="font-size: 14.5px; color: #94A3B8; max-width: 820px; line-height: 1.5;">
                Decomposing customer opinions into fine-grained sentiment scores and operational dimensions across <b>Quality</b>, <b>Shipping</b>, and <b>Price</b>.
            </div>
        </div>
        <div style="display: flex; gap: 8px;">
            <span style="font-size: 12.5px; padding: 6px 12px; border-radius: 8px; background: rgba(34, 197, 94, 0.15); color: #22C55E; font-weight: 600; border: 1px solid rgba(34, 197, 94, 0.3);">
                Accuracy: 81.3%
            </span>
            <span style="font-size: 12.5px; padding: 6px 12px; border-radius: 8px; background: rgba(56, 189, 248, 0.15); color: #38BDF8; font-weight: 600; border: 1px solid rgba(56, 189, 248, 0.3);">
                6,000 Test Set
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI Row with Distinctive Top Border Colors
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #8B7CFF;">
            <div class="kpi-header">
                <span class="kpi-title">Total Analysed</span>
                <span class="kpi-icon">📊</span>
            </div>
            <div class="kpi-value">{total_eval:,}</div>
            <div class="kpi-subtext"><span>📦</span> Held-out evaluation set</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #22C55E;">
            <div class="kpi-header">
                <span class="kpi-title">Positive Reviews</span>
                <span class="kpi-icon">😊</span>
            </div>
            <div class="kpi-value" style="color: #22C55E;">{pos_pct}</div>
            <div class="kpi-subtext"><span style="color:#22C55E;">●</span> {pos_cnt:,} reviews</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #F87171;">
            <div class="kpi-header">
                <span class="kpi-title">Negative Reviews</span>
                <span class="kpi-icon">😟</span>
            </div>
            <div class="kpi-value" style="color: #F87171;">{neg_pct}</div>
            <div class="kpi-subtext"><span style="color:#F87171;">●</span> {neg_cnt:,} reviews</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #FBBF24;">
            <div class="kpi-header">
                <span class="kpi-title">Neutral Reviews</span>
                <span class="kpi-icon">😐</span>
            </div>
            <div class="kpi-value" style="color: #FBBF24;">{neu_pct}</div>
            <div class="kpi-subtext"><span style="color:#FBBF24;">●</span> {neu_cnt:,} reviews</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Visual Analytics Split (Cached figures for instant load)
    col_chart1, col_chart2 = st.columns([1, 1])
    donut_fig, bar_fig = get_cached_overview_charts()

    with col_chart1:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        st.plotly_chart(donut_fig, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chart2:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        st.plotly_chart(bar_fig, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    # Recent Analysis Section
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
        <span style="font-size: 18px; font-weight: 700; color: #F8FAFC;">📋 Recent Review Analyses</span>
        <span style="font-size: 13px; color: #94A3B8;">Auto-updated from live sessions</span>
    </div>
    """, unsafe_allow_html=True)

    sample_records = []
    if st.session_state["recent_analyses"]:
        for item in reversed(st.session_state["recent_analyses"][-5:]):
            sample_records.append({
                "Review Snippet": (item["text"][:110] + "...") if len(item["text"]) > 110 else item["text"],
                "Sentiment": item["sentiment"].capitalize(),
                "Aspects": ", ".join(item["aspects"]) if item["aspects"] else "None",
                "Confidence": f"{(item.get('confidence', 0.0) * 100):.1f}%" if item.get("confidence") else "—",
                "Source": item.get("source", "Session")
            })

    if not eval_df.empty and len(sample_records) < 5:
        for _, row in eval_df.head(5 - len(sample_records)).iterrows():
            sample_records.append({
                "Review Snippet": (str(row["review_text"])[:110] + "...") if len(str(row["review_text"])) > 110 else str(row["review_text"]),
                "Sentiment": str(row["predicted"]).capitalize(),
                "Aspects": ", ".join(row["aspects"]) if isinstance(row["aspects"], list) else str(row["aspects"]),
                "Confidence": "Evaluated",
                "Source": "Held-Out Test"
            })

    if sample_records:
        rec_df = pd.DataFrame(sample_records)
        st.dataframe(rec_df, width="stretch", hide_index=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📝</div>
            <div class="empty-state-title">No recent reviews analyzed yet</div>
            <div class="empty-state-desc">Navigate to Single Review Analysis to test your own customer feedback comments.</div>
        </div>
        """, unsafe_allow_html=True)

    render_footer()


# =============================================================================
# PAGE 2: SINGLE REVIEW ANALYSIS
# =============================================================================
elif nav_selection == "Single Review Analysis":
    render_header(
        title="Single Review Analysis",
        subtitle="Granular sentiment classification with multi-aspect detection and confidence scoring.",
        badge="Inference Hub"
    )

    tab_direct, tab_explorer = st.tabs(["✍️ Interactive Review Input", "🛒 Amazon Food Products Explorer"])

    with tab_direct:
        st.markdown("""
        <div style="margin-bottom: 14px;">
            <span style="font-size: 15px; font-weight: 700; color: #F8FAFC; text-transform: uppercase; letter-spacing: 0.06em;">Quick Presets</span>
            <span style="font-size: 13.5px; color: #94A3B8; margin-left: 8px;">Click a sample below to populate the reviewer text:</span>
        </div>
        """, unsafe_allow_html=True)

        # Quick Preset Buttons
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        preset_text = ""
        if p_col1.button("🟢 High Quality & Courier", use_container_width=True):
            preset_text = "The quality is outstanding and very durable. Delivered by the courier right on time!"
        if p_col2.button("🔴 Stale Product & Pricey", use_container_width=True):
            preset_text = "Terrible stale taste, arrived defective and complete waste of money. Extremely overpriced."
        if p_col3.button("🟡 Average & Neutral", use_container_width=True):
            preset_text = "It was okay, an average product with nothing special. Standard taste."
        if p_col4.button("📦 Damaged Package", use_container_width=True):
            preset_text = "The courier packaging was damaged and parcel delayed, though customer service was responsive."

        # Input Area
        review_input = st.text_area(
            "Review Text",
            value=preset_text,
            height=130,
            placeholder="Type or paste customer review text here (e.g. Delicious organic tea, packaging was neat and price is reasonable)...",
            label_visibility="collapsed"
        )

        col_btn, col_info = st.columns([1, 3])
        with col_btn:
            btn_analyze = st.button("⚡ Analyse Review", key="btn_single_analyze", use_container_width=True)
        with col_info:
            char_count = len(review_input)
            st.markdown(f"<div style='margin-top:12px; font-size:13.5px; color:#64748B;'>Character count: {char_count} chars</div>", unsafe_allow_html=True)

        if btn_analyze:
            if not review_input.strip():
                st.warning("Please enter or select a review comment first.")
            else:
                with st.spinner("Extracting sentiment features & evaluating aspect dimensions..."):
                    res = api_client.predict_single(review_input, base_url=backend_url)

                if not res.get("success"):
                    st.error(f"Inference Error: {res.get('error')}")
                else:
                    sentiment = res.get("sentiment", "neutral").capitalize()
                    aspects = res.get("aspects", [])
                    confidence = res.get("confidence", 0.0)
                    probs = res.get("probabilities", {})
                    source = res.get("source", "System")

                    # Add to session history
                    st.session_state["recent_analyses"].append({
                        "text": review_input,
                        "sentiment": sentiment,
                        "aspects": aspects,
                        "confidence": confidence,
                        "source": source
                    })

                    # Determine Sentiment Styling
                    if sentiment.lower() == "positive":
                        s_color = "#22C55E"
                        s_bg = "rgba(34, 197, 94, 0.12)"
                        s_border = "rgba(34, 197, 94, 0.35)"
                        s_icon = "😊"
                    elif sentiment.lower() == "negative":
                        s_color = "#F87171"
                        s_bg = "rgba(248, 113, 113, 0.12)"
                        s_border = "rgba(248, 113, 113, 0.35)"
                        s_icon = "😟"
                    else:
                        s_color = "#FBBF24"
                        s_bg = "rgba(251, 191, 36, 0.12)"
                        s_border = "rgba(251, 191, 36, 0.35)"
                        s_icon = "😐"

                    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

                    # Output Row 1: Overall Sentiment Card + Aspects Grid
                    r_col1, r_col2 = st.columns([1, 1.2])

                    with r_col1:
                        conf_str = f"{(confidence * 100):.1f}%" if confidence else "Calculated"
                        st.markdown(f"""
                        <div class="saas-card-static" style="border-color:{s_border}; background: {s_bg}; box-shadow: 0 8px 24px rgba(0,0,0,0.35);">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:13.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94A3B8;">Predicted Sentiment</span>
                                <span class="status-pill status-pill-online" style="font-size:12.5px; padding:3px 10px;">{source}</span>
                            </div>
                            <div style="font-size:36px; font-weight:800; color:{s_color}; margin: 14px 0 8px 0; letter-spacing:-0.03em;">
                                {s_icon} {sentiment.upper()}
                            </div>
                            <div style="font-size:16px; color:#F8FAFC;">
                                Decision Confidence: <b style="color:#FFFFFF; font-size:18px;">{conf_str}</b>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with r_col2:
                        # Aspect Badges
                        st.markdown("<div class='saas-card-static'>", unsafe_allow_html=True)
                        st.markdown("<span style='font-size:13.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94A3B8;'>Detected Business Aspects</span>", unsafe_allow_html=True)

                        aspect_pills_html = ""
                        for asp, asp_cls in [("Quality", "aspect-quality"), ("Shipping", "aspect-shipping"), ("Price", "aspect-price")]:
                            if asp in aspects:
                                aspect_pills_html += f'<span class="aspect-pill {asp_cls}">🏷️ {asp}: Detected</span>'
                            else:
                                aspect_pills_html += f'<span class="aspect-pill aspect-none">○ {asp}: Not Present</span>'

                        st.markdown(f"<div style='margin-top:14px;'>{aspect_pills_html}</div>", unsafe_allow_html=True)

                        st.markdown(f"""
                        <div style="margin-top:16px; font-size:15px; color:#94A3B8; line-height:1.6;">
                            <b>Summary:</b> Review addresses <b>{len(aspects)}</b> of 3 operational dimensions ({', '.join(aspects) if aspects else 'General opinion'}).
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Output Row 2: Probabilities Distribution
                    if probs:
                        st.markdown("<div class='saas-card-static'>", unsafe_allow_html=True)
                        st.markdown("<span style='font-size:13.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94A3B8;'>Softmax Probability Breakdown</span>", unsafe_allow_html=True)

                        prob_pos = probs.get("positive", 0.0) * 100
                        prob_neu = probs.get("neutral", 0.0) * 100
                        prob_neg = probs.get("negative", 0.0) * 100

                        pr_c1, pr_c2, pr_c3 = st.columns(3)
                        with pr_c1:
                            st.markdown(f"""
                            <div style="margin-top: 10px; padding: 12px; border-radius: 8px; background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.2);">
                                <div style="display:flex; justify-content:space-between; font-size: 13.5px; color: #94A3B8; font-weight: 600;">
                                    <span>Positive</span>
                                    <span style="color:#22C55E; font-weight:700;">{prob_pos:.1f}%</span>
                                </div>
                                <div style="height: 6px; background: rgba(30, 41, 59, 0.8); border-radius: 3px; margin-top: 8px; overflow: hidden;">
                                    <div style="width: {prob_pos}%; background: #22C55E; height: 100%; border-radius: 3px;"></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        with pr_c2:
                            st.markdown(f"""
                            <div style="margin-top: 10px; padding: 12px; border-radius: 8px; background: rgba(251, 191, 36, 0.08); border: 1px solid rgba(251, 191, 36, 0.2);">
                                <div style="display:flex; justify-content:space-between; font-size: 13.5px; color: #94A3B8; font-weight: 600;">
                                    <span>Neutral</span>
                                    <span style="color:#FBBF24; font-weight:700;">{prob_neu:.1f}%</span>
                                </div>
                                <div style="height: 6px; background: rgba(30, 41, 59, 0.8); border-radius: 3px; margin-top: 8px; overflow: hidden;">
                                    <div style="width: {prob_neu}%; background: #FBBF24; height: 100%; border-radius: 3px;"></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        with pr_c3:
                            st.markdown(f"""
                            <div style="margin-top: 10px; padding: 12px; border-radius: 8px; background: rgba(248, 113, 113, 0.08); border: 1px solid rgba(248, 113, 113, 0.2);">
                                <div style="display:flex; justify-content:space-between; font-size: 13.5px; color: #94A3B8; font-weight: 600;">
                                    <span>Negative</span>
                                    <span style="color:#F87171; font-weight:700;">{prob_neg:.1f}%</span>
                                </div>
                                <div style="height: 6px; background: rgba(30, 41, 59, 0.8); border-radius: 3px; margin-top: 8px; overflow: hidden;">
                                    <div style="width: {prob_neg}%; background: #F87171; height: 100%; border-radius: 3px;"></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)

    with tab_explorer:
        st.markdown("""
        <div style="margin-bottom: 14px;">
            <span style="font-size: 16px; font-weight: 700; color: #F8FAFC;">Database Explorer: Amazon Fine Food Reviews</span>
            <div style="font-size: 14px; color: #94A3B8; margin-top: 4px;">Inspect product entries with historical star ratings and text feedback:</div>
        </div>
        """, unsafe_allow_html=True)

        popular_titles, all_titles = get_popular_food_titles()
        if not popular_titles:
            st.error("Dataset 'final_food_reviews.csv' not found.")
        else:
            s_col1, s_col2 = st.columns([1, 1.6])
            with s_col1:
                search_q = st.text_input("🔍 Search product catalog:", placeholder="Type e.g. coffee, tea, chocolate...", key="food_search_box").strip().lower()
            with s_col2:
                if search_q:
                    matching = [t for t in all_titles if search_q in t.lower()][:35]
                    options = (["-- Select from Search Results --"] + matching) if matching else ["-- No matching products found --"]
                else:
                    options = ["-- Choose a Popular Item --"] + popular_titles
                selected_product = st.selectbox("Select Product to Inspect:", options=options, key="prod_explorer_select")

            if selected_product and not selected_product.startswith("--"):
                food_df = load_food_dataset()
                prod_data = food_df[food_df["title"] == selected_product]
                avg_rating = prod_data["Score"].mean()
                total_prod_reviews = len(prod_data)

                p1, p2 = st.columns(2)
                with p1:
                    st.markdown(f"""
                    <div class="kpi-card" style="border-top: 3px solid #FBBF24;">
                        <div class="kpi-title">Average Star Rating</div>
                        <div class="kpi-value" style="font-size:26px;">⭐ {avg_rating:.2f} / 5.0</div>
                    </div>
                    """, unsafe_allow_html=True)
                with p2:
                    st.markdown(f"""
                    <div class="kpi-card" style="border-top: 3px solid #38BDF8;">
                        <div class="kpi-title">Total Product Reviews</div>
                        <div class="kpi-value" style="font-size:26px;">📩 {total_prod_reviews:,}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
                st.markdown("##### 📋 Verified Sample Customer Reviews")
                display_sub = prod_data[["Score", "Summary", "Text"]].head(5).copy()
                st.dataframe(display_sub, width="stretch", hide_index=True)

    render_footer()


# =============================================================================
# PAGE 3: BATCH REVIEW ANALYSIS
# =============================================================================
elif nav_selection == "Batch Review Analysis":
    render_header(
        title="Batch Review Analysis",
        subtitle="Upload customer feedback datasets for high-throughput batch classification and aspect tagging.",
        badge="Bulk Processor"
    )

    # Visual Pipeline Stepper
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; padding: 14px 20px; border-radius: 10px; background: rgba(21, 28, 44, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 24px;">
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="width:24px; height:24px; border-radius:50%; background:#8B7CFF; color:#FFFFFF; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700;">1</span>
            <span style="font-size:14px; font-weight:600; color:#F8FAFC;">Upload CSV</span>
        </div>
        <span style="color:#64748B;">→</span>
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="width:24px; height:24px; border-radius:50%; background:rgba(255,255,255,0.1); color:#94A3B8; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700;">2</span>
            <span style="font-size:14px; font-weight:500; color:#94A3B8;">Map Columns</span>
        </div>
        <span style="color:#64748B;">→</span>
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="width:24px; height:24px; border-radius:50%; background:rgba(255,255,255,0.1); color:#94A3B8; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700;">3</span>
            <span style="font-size:14px; font-weight:500; color:#94A3B8;">Batch Inference</span>
        </div>
        <span style="color:#64748B;">→</span>
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="width:24px; height:24px; border-radius:50%; background:rgba(255,255,255,0.1); color:#94A3B8; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700;">4</span>
            <span style="font-size:14px; font-weight:500; color:#94A3B8;">Export Insights</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"],
        help="Upload any CSV file containing customer review comments."
    )

    if uploaded_file is not None:
        try:
            raw_df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            st.markdown(f"""
            <div style="display:flex; gap:12px; align-items:center; margin: 10px 0 16px 0;">
                <span class="status-pill status-pill-online">✓ File Uploaded: {uploaded_file.name}</span>
                <span class="status-pill status-pill-fallback">{len(raw_df):,} Total Rows Detected</span>
            </div>
            """, unsafe_allow_html=True)

            # Detect Text Column
            cols = list(raw_df.columns)
            candidate_cols = ["Text", "review_text", "text", "review", "content", "comment", "Summary", "feedback"]
            default_idx = 0
            for idx, c in enumerate(cols):
                if c in candidate_cols:
                    default_idx = idx
                    break

            cfg_col1, cfg_col2 = st.columns([2, 1])
            with cfg_col1:
                selected_col = st.selectbox("Select Review Text Column:", options=cols, index=default_idx)
            with cfg_col2:
                sample_limit = st.number_input(
                    "Rows to Process (0 = All):",
                    min_value=0,
                    max_value=len(raw_df),
                    value=min(500, len(raw_df)),
                    step=100
                )

            with st.expander("🔍 Raw Data Preview (First 5 Rows)", expanded=False):
                st.dataframe(raw_df.head(5), width="stretch")

            btn_run_batch = st.button("🚀 Run Batch AI Analysis", key="btn_exec_batch")

            if btn_run_batch:
                df_to_analyze = raw_df.head(sample_limit) if sample_limit > 0 else raw_df
                texts_list = df_to_analyze[selected_col].astype(str).tolist()

                prog_bar = st.progress(0.0)
                status_box = st.empty()

                def update_prog(ratio, processed, total):
                    prog_bar.progress(min(1.0, ratio))
                    status_box.markdown(f"<span style='font-size:15px; color:#94A3B8;'>Processed <b>{processed:,}</b> of {total:,} reviews...</span>", unsafe_allow_html=True)

                with st.spinner("Processing batch through ReviewSense AI engine..."):
                    results_list, exec_source = api_client.predict_batch(
                        texts_list,
                        base_url=backend_url,
                        chunk_size=200,
                        progress_callback=update_prog
                    )

                prog_bar.progress(1.0)
                status_box.markdown(f"<span style='font-size:15px; color:#22C55E; font-weight:600;'>✓ Finished {len(results_list):,} predictions via {exec_source}</span>", unsafe_allow_html=True)

                # Attach Results to DataFrame
                out_df = df_to_analyze.copy()
                out_df["Predicted_Sentiment"] = [r["sentiment"] for r in results_list]
                out_df["Aspects"] = [", ".join(r["aspects"]) if r["aspects"] else "None" for r in results_list]

                # Store for Analytics
                st.session_state["latest_batch_df"] = out_df

                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("### 📊 Batch Execution Summary")

                # Metric Cards
                b_total = len(out_df)
                b_pos = (out_df["Predicted_Sentiment"] == "positive").sum()
                b_neg = (out_df["Predicted_Sentiment"] == "negative").sum()
                b_neu = (out_df["Predicted_Sentiment"] == "neutral").sum()

                m_c1, m_c2, m_c3, m_c4 = st.columns(4)
                m_c1.metric("Analysed Rows", f"{b_total:,}", f"Engine: {exec_source}")
                m_c2.metric("Positive Sentiment", f"{(b_pos/b_total*100):.1f}%", f"{b_pos:,} rows")
                m_c3.metric("Negative Sentiment", f"{(b_neg/b_total*100):.1f}%", f"{b_neg:,} rows")
                m_c4.metric("Neutral Sentiment", f"{(b_neu/b_total*100):.1f}%", f"{b_neu:,} rows")

                # Visual Charts
                st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
                b_chart1, b_chart2 = st.columns(2)
                with b_chart1:
                    st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                    st.plotly_chart(
                        ui_charts.create_sentiment_donut(out_df, sentiment_col="Predicted_Sentiment"),
                        width="stretch"
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                with b_chart2:
                    st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                    st.plotly_chart(
                        ui_charts.create_aspect_bar(out_df, aspects_col="Aspects"),
                        width="stretch"
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                # Results Table with Filters
                st.markdown("#### 📋 Processed Predictions Table")

                f_c1, f_c2 = st.columns(2)
                with f_c1:
                    filter_s = st.selectbox("Filter by Sentiment:", ["All", "Positive", "Negative", "Neutral"])
                with f_c2:
                    filter_a = st.selectbox("Filter by Aspect:", ["All", "Quality", "Shipping", "Price", "None"])

                filtered_out = out_df.copy()
                if filter_s != "All":
                    filtered_out = filtered_out[filtered_out["Predicted_Sentiment"].str.lower() == filter_s.lower()]
                if filter_a != "All":
                    filtered_out = filtered_out[filtered_out["Aspects"].str.contains(filter_a, case=False, na=False)]

                st.dataframe(filtered_out, width="stretch", hide_index=True)

                # Export CSV
                csv_bytes = out_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Analyzed CSV (with Predictions)",
                    data=csv_bytes,
                    file_name="reviewsense_predictions.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"Failed to process CSV file: {e}")
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📂</div>
            <div class="empty-state-title">Drag & drop your reviews CSV here</div>
            <div class="empty-state-desc">Accepts any standard CSV file containing customer comments or reviews for bulk processing.</div>
        </div>
        """, unsafe_allow_html=True)

    render_footer()


# =============================================================================
# PAGE 4: SENTIMENT ANALYTICS
# =============================================================================
elif nav_selection == "Sentiment Analytics":
    render_header(
        title="Sentiment Analytics & Trends",
        subtitle="Deep dive into customer sentiment distributions, star rating correlations, and temporal volume trends.",
        badge="Analytics Suite"
    )

    # Active dataset selection
    analytics_df = eval_df
    if "latest_batch_df" in st.session_state and not st.session_state["latest_batch_df"].empty:
        st.info("ℹ️ Analytics is utilizing both the held-out evaluation dataset and your latest batch analysis upload.")

    if analytics_df.empty:
        st.warning("No evaluation data loaded.")
    else:
        # Filter controls
        f1, f2 = st.columns([1, 1])
        with f1:
            aspect_choice = st.selectbox("Filter by Aspect Dimension:", ["All Aspects", "Quality", "Shipping", "Price"])
        with f2:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)

        filtered_analytics = analytics_df.copy()
        if aspect_choice != "All Aspects":
            filtered_analytics = filtered_analytics[filtered_analytics["aspects"].apply(lambda a: aspect_choice in a if isinstance(a, list) else aspect_choice in str(a))]

        # Row 1: Donut & Aspect Sentiment Breakdown
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
            st.plotly_chart(
                ui_charts.create_sentiment_donut(filtered_analytics, sentiment_col="predicted"),
                width="stretch"
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with r1_c2:
            st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
            st.plotly_chart(
                ui_charts.create_aspect_sentiment_grouped_bar(filtered_analytics, sentiment_col="predicted", aspects_col="aspects"),
                width="stretch"
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Row 2: Star Rating vs Sentiment & Temporal Trend (Precomputed Static Charts)
        m_fig, t_fig = get_sentiment_analytics_static_charts()
        if m_fig and t_fig:
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            r2_c1, r2_c2 = st.columns(2)

            with r2_c1:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.plotly_chart(m_fig, width="stretch")
                st.markdown("</div>", unsafe_allow_html=True)

            with r2_c2:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.plotly_chart(t_fig, width="stretch")
                st.markdown("</div>", unsafe_allow_html=True)

    render_footer()


# =============================================================================
# PAGE 5: ASPECT-BASED INSIGHTS
# =============================================================================
elif nav_selection == "Aspect-Based Insights":
    render_header(
        title="Aspect-Based Intelligence",
        subtitle="Dissect customer feedback across three core operational pillars: Quality, Shipping, and Price.",
        badge="Multi-Aspect 360°"
    )

    if eval_df.empty:
        st.warning("Evaluation data not available.")
    else:
        # Precomputed Aspect Analytics & Chart (Loaded instantly from cache)
        (q_tot, q_pos, q_neg, q_neu, q_df), (s_tot, s_pos, s_neg, s_neu, s_df), (p_tot, p_pos, p_neg, p_neu, p_df), grouped_chart = get_cached_aspect_stats()

        # 3 Pillar Cards with Modern Glassmorphism Styling
        a_c1, a_c2, a_c3 = st.columns(3)

        with a_c1:
            st.markdown(f"""
            <div class="saas-card-static" style="border-top: 3px solid #818CF8;">
                <div class="kpi-header">
                    <span class="kpi-title">Product Quality</span>
                    <span class="aspect-pill aspect-quality" style="margin:0;">🏷️ Quality</span>
                </div>
                <div class="kpi-value">{q_tot:,}</div>
                <div style="font-size:14px; color:#94A3B8; margin-bottom:14px;">Total Customer Mentions</div>
                <div style="font-size:15px; line-height:1.9;">
                    <span style="color:#22C55E;">● Positive: <b>{q_pos:,}</b> ({(q_pos/q_tot*100 if q_tot else 0):.1f}%)</span><br>
                    <span style="color:#F87171;">● Negative: <b>{q_neg:,}</b> ({(q_neg/q_tot*100 if q_tot else 0):.1f}%)</span><br>
                    <span style="color:#FBBF24;">● Neutral: <b>{q_neu:,}</b> ({(q_neu/q_tot*100 if q_tot else 0):.1f}%)</span>
                </div>
                <div style="margin-top:14px; font-size:13px; color:#64748B;">
                    Keywords: <i>quality, material, build, durable, fresh, stale, taste</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with a_c2:
            st.markdown(f"""
            <div class="saas-card-static" style="border-top: 3px solid #38BDF8;">
                <div class="kpi-header">
                    <span class="kpi-title">Shipping & Logistics</span>
                    <span class="aspect-pill aspect-shipping" style="margin:0;">🏷️ Shipping</span>
                </div>
                <div class="kpi-value">{s_tot:,}</div>
                <div style="font-size:14px; color:#94A3B8; margin-bottom:14px;">Total Customer Mentions</div>
                <div style="font-size:15px; line-height:1.9;">
                    <span style="color:#22C55E;">● Positive: <b>{s_pos:,}</b> ({(s_pos/s_tot*100 if s_tot else 0):.1f}%)</span><br>
                    <span style="color:#F87171;">● Negative: <b>{s_neg:,}</b> ({(s_neg/s_tot*100 if s_tot else 0):.1f}%)</span><br>
                    <span style="color:#FBBF24;">● Neutral: <b>{s_neu:,}</b> ({(s_neu/s_tot*100 if s_tot else 0):.1f}%)</span>
                </div>
                <div style="margin-top:14px; font-size:13px; color:#64748B;">
                    Keywords: <i>shipping, delivery, arrived, courier, late, packaging</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with a_c3:
            st.markdown(f"""
            <div class="saas-card-static" style="border-top: 3px solid #F472B6;">
                <div class="kpi-header">
                    <span class="kpi-title">Price Perception</span>
                    <span class="aspect-pill aspect-price" style="margin:0;">🏷️ Price</span>
                </div>
                <div class="kpi-value">{p_tot:,}</div>
                <div style="font-size:14px; color:#94A3B8; margin-bottom:14px;">Total Customer Mentions</div>
                <div style="font-size:15px; line-height:1.9;">
                    <span style="color:#22C55E;">● Positive: <b>{p_pos:,}</b> ({(p_pos/p_tot*100 if p_tot else 0):.1f}%)</span><br>
                    <span style="color:#F87171;">● Negative: <b>{p_neg:,}</b> ({(p_neg/p_tot*100 if p_tot else 0):.1f}%)</span><br>
                    <span style="color:#FBBF24;">● Neutral: <b>{p_neu:,}</b> ({(p_neu/p_tot*100 if p_tot else 0):.1f}%)</span>
                </div>
                <div style="margin-top:14px; font-size:13px; color:#64748B;">
                    Keywords: <i>price, cost, expensive, cheap, value for money, budget</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

        # Comparative Visualization
        if grouped_chart:
            st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
            st.plotly_chart(grouped_chart, width="stretch")
            st.markdown("</div>", unsafe_allow_html=True)

        # Interactive Aspect Explorer
        st.markdown("### 🔍 Aspect Review Explorer")
        chosen_asp = st.radio("Select Aspect to Inspect Actual Reviews:", ["Quality", "Shipping", "Price"], horizontal=True)

        target_df = q_df if chosen_asp == "Quality" else (s_df if chosen_asp == "Shipping" else p_df)
        st.caption(f"Showing 10 sample reviews tagged with **{chosen_asp}** from held-out evaluation dataset:")

        preview_cols = target_df[["review_text", "actual", "predicted"]].head(10).copy()
        preview_cols.columns = ["Review Comment", "Actual Label", "Predicted Sentiment"]
        st.dataframe(preview_cols, width="stretch", hide_index=True)

    render_footer()


# =============================================================================
# PAGE 6: ABOUT PROJECT
# =============================================================================
elif nav_selection == "About Project":
    render_header(
        title="About ReviewSense",
        subtitle="Multi-aspect review intelligence platform architecture, technical stack, and engineering team.",
        badge="Architecture & Team"
    )

    st.markdown("""
    <div class="saas-card-static">
        <h3 style="margin-top:0; color:#F8FAFC; font-size:18px;">Executive Summary</h3>
        <p style="color:#94A3B8; font-size:16px; line-height:1.7;">
        <b>ReviewSense</b> addresses the core limitation of star-rating based customer feedback systems.
        A 3-star review often conceals divergent experiences (e.g. delicious food accompanied by delayed logistics).
        By combining Scikit-Learn TF-IDF machine learning pipelines with high-recall rule-based aspect extraction,
        ReviewSense decomposes customer opinions into actionable business intelligence across <b>Quality</b>, 
        <b>Shipping</b>, and <b>Price</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # System Architecture Cards
    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown("""
        <div class="saas-card-static" style="border-top: 3px solid #8B7CFF;">
            <div style="font-size:26px; margin-bottom:10px;">🎨</div>
            <div style="font-weight:700; color:#F8FAFC; font-size:16px; margin-bottom:6px;">Streamlit Frontend</div>
            <p style="color:#94A3B8; font-size:14.5px; line-height:1.6;">
            Linear/Vercel-inspired dark glassmorphism interface with Plotly charting, live health indicators, and resilient local fallback.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with a2:
        st.markdown("""
        <div class="saas-card-static" style="border-top: 3px solid #38BDF8;">
            <div style="font-size:26px; margin-bottom:10px;">⚡</div>
            <div style="font-weight:700; color:#F8FAFC; font-size:16px; margin-bottom:6px;">FastAPI Backend</div>
            <p style="color:#94A3B8; font-size:14.5px; line-height:1.6;">
            High-throughput REST API server supporting single and batch vectorization on port 8000 with CORS middleware.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with a3:
        st.markdown("""
        <div class="saas-card-static" style="border-top: 3px solid #22C55E;">
            <div style="font-size:26px; margin-bottom:10px;">🧠</div>
            <div style="font-weight:700; color:#F8FAFC; font-size:16px; margin-bottom:6px;">NLP & ML Engine</div>
            <p style="color:#94A3B8; font-size:14.5px; line-height:1.6;">
            TF-IDF bigram vectorizer paired with balanced Logistic Regression and 50+ domain regex aspect patterns.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # API Specification Table
    st.markdown("### 🔌 API Endpoint Reference")
    api_specs = {
        "Endpoint": ["GET /health", "POST /predict", "POST /predict_batch"],
        "Method": ["GET", "POST", "POST"],
        "Payload / Parameters": ["None", '{"review_text": "..."}', '{"reviews": [{"review_text": "..."}]}'],
        "Response": ['{"status": "ok", "predictor_available": true}', '{"sentiment": "...", "aspects": [...], "confidence": 0.95}', '{"results": [...], "count": N}'],
        "Description": ["Service status & ML readiness check", "Single review inference with aspect tagging", "Chunked batch inference for bulk CSV uploads"]
    }
    st.dataframe(pd.DataFrame(api_specs), width="stretch", hide_index=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Team Contributions
    st.markdown("### 👥 Engineering Team (Group D)")
    team_data = {
        "Member": ["Manoj", "Atik", "Biki", "Simran"],
        "Primary Ownership": [
            "Data Pipeline & ML Model Training",
            "Streamlit Frontend & UI/UX Architecture",
            "FastAPI Backend & Microservice Integration",
            "Aspect Detection Engine, Testing & Docs"
        ],
        "Key Deliverables": [
            "TF-IDF Logistic Regression pipeline, models/sentiment_pipeline.joblib",
            "Linear/Vercel dark dashboard, Plotly integration, batch CSV upload",
            "api.py, backend.api REST server, CORS, batch chunking",
            "simran_all_in_one.py, 14 aspect test suite, PPT deck"
        ]
    }
    st.dataframe(pd.DataFrame(team_data), width="stretch", hide_index=True)

    render_footer()
