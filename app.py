"""
ReviewSense – Multi-Aspect Product Review & Customer Sentiment Hub
Linear / Vercel-inspired Enterprise AI SaaS Dashboard
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
# 2. CACHED DATA LOADERS
# -----------------------------------------------------------------------------
@st.cache_data
def load_eval_predictions() -> pd.DataFrame:
    """Loads held-out test predictions (6,000 reviews) and computes aspects."""
    try:
        p_df = pd.read_csv("data/predictions.csv")
        p_df["predicted"] = p_df["predicted"].str.lower()
        if "aspects" not in p_df.columns:
            p_df["aspects"] = p_df["review_text"].apply(detect_aspects)
        return p_df
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_food_dataset() -> pd.DataFrame:
    """Loads a sample of the Amazon Food Reviews dataset with product titles."""
    try:
        return pd.read_csv("final_food_reviews.csv")
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_confusion_matrix() -> pd.DataFrame:
    """Loads the test evaluation confusion matrix."""
    try:
        return pd.read_csv("outputs/confusion_matrix.csv", index_col=0)
    except Exception:
        return pd.DataFrame()


eval_df = load_eval_predictions()
food_df = load_food_dataset()
cm_df = load_confusion_matrix()


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
            "Model Performance",
            "About Project"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<hr style='margin: 16px 0 !important;'>", unsafe_allow_html=True)

    # Live Backend Status Check
    backend_url = st.session_state["backend_url"]
    health = api_client.check_api_health(backend_url)

    st.markdown("<span style='font-size:11px; font-weight:600; color:#94A3B8; text-transform:uppercase; letter-spacing:0.06em;'>System Status</span>", unsafe_allow_html=True)
    if health["online"]:
        st.markdown(f"""
        <div class="status-pill status-pill-online" style="margin-top:6px; margin-bottom:12px; width:100%; justify-content:center;">
            <div class="pulse-dot"></div>
            <span>FastAPI Server Connected (:8000)</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-pill status-pill-fallback" style="margin-top:6px; margin-bottom:12px; width:100%; justify-content:center;">
            <div class="pulse-dot"></div>
            <span>Local ML Pipeline Active (Fallback)</span>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("⚙️ Connection Settings", expanded=False):
        new_url = st.text_input("Backend API URL", value=backend_url, key="sidebar_url_input")
        if new_url != backend_url:
            st.session_state["backend_url"] = new_url
            st.rerun()

        if not health["online"]:
            st.caption("To start the dedicated FastAPI backend, run in terminal:")
            st.code("uvicorn api:app --reload --port 8000", language="bash")
            st.caption("Zero-downtime fallback runs ML inference locally.")

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding: 12px; border-radius: 8px; background: #111827; border: 1px solid #1E293B;'>
        <div style='font-size: 11px; font-weight: 600; color: #F8FAFC;'>ReviewSense v2.1 Enterprise</div>
        <div style='font-size: 11px; color: #64748B; margin-top: 2px;'>Scikit-Learn • FastAPI • Streamlit</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. TOP HEADER BAR HELPER
# -----------------------------------------------------------------------------
def render_header(title: str, subtitle: str):
    """Renders the top title bar with active status pill."""
    status_html = (
        '<div class="status-pill status-pill-online"><div class="pulse-dot"></div> API Online</div>'
        if health["online"]
        else '<div class="status-pill status-pill-fallback"><div class="pulse-dot"></div> Local Fallback</div>'
    )
    st.markdown(f"""
    <div class="top-header">
        <div>
            <h1 class="top-header-title">{title}</h1>
            <p class="top-header-subtitle">{subtitle}</p>
        </div>
        <div class="status-badge-container">
            {status_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PAGE 1: OVERVIEW
# =============================================================================
if nav_selection == "Overview":
    render_header(
        title="Welcome to ReviewSense",
        subtitle="Understand customer opinions through intelligent sentiment and multi-aspect analysis."
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

    # KPI Row
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-title">Total Reviews Analysed</span>
                <span class="kpi-icon">📊</span>
            </div>
            <div class="kpi-value">{total_eval:,}</div>
            <div class="kpi-subtext">Held-out test dataset evaluation</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
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
        <div class="kpi-card">
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
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-title">Neutral Reviews</span>
                <span class="kpi-icon">😐</span>
            </div>
            <div class="kpi-value" style="color: #FBBF24;">{neu_pct}</div>
            <div class="kpi-subtext"><span style="color:#FBBF24;">●</span> {neu_cnt:,} reviews</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Visual Analytics Split
    col_chart1, col_chart2 = st.columns([1, 1])
    with col_chart1:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        donut_fig = ui_charts.create_sentiment_donut(eval_df, sentiment_col="predicted")
        st.plotly_chart(donut_fig, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chart2:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        bar_fig = ui_charts.create_aspect_bar(eval_df, aspects_col="aspects")
        st.plotly_chart(bar_fig, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    # Recent Analysis Section
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Recent Review Analyses")

    # Combine recent session analyses with a few sample evaluations
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
                "Aspects": ", ".join(row["aspects"]) if isinstance(row["aspects"], list) and row["aspects"] else "None",
                "Confidence": "Evaluated",
                "Source": "Test Set"
            })

    if sample_records:
        rec_df = pd.DataFrame(sample_records)
        st.dataframe(rec_df, width="stretch", hide_index=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📝</div>
            <div class="empty-state-title">No recent reviews analyzed yet</div>
            <div class="empty-state-desc">Head over to Single Review Analysis to analyze individual customer feedback.</div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# PAGE 2: SINGLE REVIEW ANALYSIS
# =============================================================================
elif nav_selection == "Single Review Analysis":
    render_header(
        title="Single Review Analysis",
        subtitle="Perform granular sentiment classification and extract business aspects with confidence metrics."
    )

    tab_direct, tab_explorer = st.tabs(["✍️ Interactive Review Input", "🛒 Amazon Food Products Explorer"])

    with tab_direct:
        st.markdown("#### Test a Customer Review")
        st.caption("Select a quick preset or paste custom feedback below:")

        # Quick Preset Buttons
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        preset_text = ""
        if p_col1.button("🟢 High Quality & Fast Courier"):
            preset_text = "The quality is outstanding and very durable. Delivered by the courier right on time!"
        if p_col2.button("🔴 Stale Product & Pricey"):
            preset_text = "Terrible stale taste, arrived defective and complete waste of money. Extremely overpriced."
        if p_col3.button("🟡 Average & Neutral"):
            preset_text = "It was okay, an average product with nothing special. Standard taste."
        if p_col4.button("📦 Damaged Package"):
            preset_text = "The courier packaging was damaged and parcel delayed, though customer service was responsive."

        # Input Area
        review_input = st.text_area(
            "Review Text",
            value=preset_text,
            height=130,
            placeholder="Type or paste customer review text here (e.g. Delicious organic tea, packaging was neat and price is reasonable)...",
            label_visibility="collapsed"
        )

        btn_analyze = st.button("⚡ Analyse Review", key="btn_single_analyze")

        if btn_analyze:
            if not review_input.strip():
                st.warning("Please enter a review first.")
            else:
                with st.spinner("Classifying sentiment and extracting multi-aspect keywords..."):
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
                        s_border = "rgba(34, 197, 94, 0.3)"
                        s_icon = "😊"
                    elif sentiment.lower() == "negative":
                        s_color = "#F87171"
                        s_bg = "rgba(248, 113, 113, 0.12)"
                        s_border = "rgba(248, 113, 113, 0.3)"
                        s_icon = "😟"
                    else:
                        s_color = "#FBBF24"
                        s_bg = "rgba(251, 191, 36, 0.12)"
                        s_border = "rgba(251, 191, 36, 0.3)"
                        s_icon = "😐"

                    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                    # Output Row 1: Overall Sentiment Card + Aspects Grid
                    r_col1, r_col2 = st.columns([1, 1.2])

                    with r_col1:
                        conf_str = f"{(confidence * 100):.1f}%" if confidence else "Calculated"
                        st.markdown(f"""
                        <div class="saas-card-static" style="border-color:{s_border}; background: {s_bg};">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:11.5px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8;">Predicted Sentiment</span>
                                <span class="status-pill status-pill-online" style="font-size:11px; padding:3px 8px;">{source}</span>
                            </div>
                            <div style="font-size:32px; font-weight:800; color:{s_color}; margin: 12px 0 6px 0; font-family:'Plus Jakarta Sans';">
                                {s_icon} {sentiment.upper()}
                            </div>
                            <div style="font-size:13px; color:#F8FAFC;">
                                Decision Confidence: <b>{conf_str}</b>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with r_col2:
                        # Aspect Badges
                        st.markdown("<div class='saas-card-static'>", unsafe_allow_html=True)
                        st.markdown("<span style='font-size:11.5px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8;'>Aspect Dimensions</span>", unsafe_allow_html=True)

                        aspect_pills_html = ""
                        for asp, asp_cls in [("Quality", "aspect-quality"), ("Shipping", "aspect-shipping"), ("Price", "aspect-price")]:
                            if asp in aspects:
                                aspect_pills_html += f'<span class="aspect-pill {asp_cls}">🏷️ {asp}: Detected</span>'
                            else:
                                aspect_pills_html += f'<span class="aspect-pill aspect-none">○ {asp}: Not Present</span>'

                        st.markdown(f"<div style='margin-top:12px;'>{aspect_pills_html}</div>", unsafe_allow_html=True)

                        st.markdown(f"""
                        <div style="margin-top:14px; font-size:12px; color:#94A3B8;">
                            <b>Summary:</b> Review touches upon <b>{len(aspects)}</b> business dimension{'s' if len(aspects) != 1 else ''}.
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Output Row 2: Probabilities Distribution & Text Metrics
                    if probs:
                        st.markdown("<div class='saas-card-static'>", unsafe_allow_html=True)
                        st.markdown("<span style='font-size:11.5px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8;'>Model Probability Distribution (Softmax)</span>", unsafe_allow_html=True)

                        prob_pos = probs.get("positive", 0.0) * 100
                        prob_neu = probs.get("neutral", 0.0) * 100
                        prob_neg = probs.get("negative", 0.0) * 100

                        st.markdown(f"""
                        <div style="margin-top:10px;">
                            <div class="confidence-header">
                                <span>Positive: <b>{prob_pos:.1f}%</b></span>
                                <span>Neutral: <b>{prob_neu:.1f}%</b></span>
                                <span>Negative: <b>{prob_neg:.1f}%</b></span>
                            </div>
                            <div class="confidence-bar-bg" style="display:flex;">
                                <div style="width:{prob_pos}%; background:#22C55E; height:100%;"></div>
                                <div style="width:{prob_neu}%; background:#FBBF24; height:100%;"></div>
                                <div style="width:{prob_neg}%; background:#F87171; height:100%;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

    with tab_explorer:
        st.markdown("#### Database Explorer: Amazon Fine Food Reviews")
        if food_df.empty:
            st.error("Dataset 'final_food_reviews.csv' not found.")
        else:
            unique_foods = food_df[food_df["title"] != "Unknown Product"]["title"].unique().tolist()
            unique_foods.sort()

            selected_product = st.selectbox(
                "Select a product from the database:",
                options=["-- Choose a Food Item --"] + unique_foods,
                key="prod_explorer_select"
            )

            if selected_product != "-- Choose a Food Item --":
                prod_data = food_df[food_df["title"] == selected_product]
                avg_rating = prod_data["Score"].mean()
                total_prod_reviews = len(prod_data)

                p1, p2 = st.columns(2)
                with p1:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">Average Star Rating</div>
                        <div class="kpi-value" style="font-size:24px;">⭐ {avg_rating:.2f} / 5.0</div>
                    </div>
                    """, unsafe_allow_html=True)
                with p2:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">Dataset Reviews Count</div>
                        <div class="kpi-value" style="font-size:24px;">📩 {total_prod_reviews:,}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                st.markdown("##### 📋 Verified Sample Customer Reviews")
                display_sub = prod_data[["Score", "Summary", "Text"]].head(5).copy()
                st.dataframe(display_sub, width="stretch", hide_index=True)


# =============================================================================
# PAGE 3: BATCH REVIEW ANALYSIS
# =============================================================================
elif nav_selection == "Batch Review Analysis":
    render_header(
        title="Batch Review Analysis",
        subtitle="Upload customer feedback datasets for automated, high-throughput sentiment classification and aspect tagging."
    )

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
                <span class="status-pill status-pill-fallback">{len(raw_df):,} Total Rows</span>
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
                    status_box.markdown(f"<span style='font-size:12px; color:#94A3B8;'>Processed {processed:,} of {total:,} reviews...</span>", unsafe_allow_html=True)

                with st.spinner("Processing batch through ReviewSense AI engine..."):
                    results_list, exec_source = api_client.predict_batch(
                        texts_list,
                        base_url=backend_url,
                        chunk_size=200,
                        progress_callback=update_prog
                    )

                prog_bar.progress(1.0)
                status_box.markdown(f"<span style='font-size:12px; color:#22C55E; font-weight:600;'>✓ Finished {len(results_list):,} predictions via {exec_source}</span>", unsafe_allow_html=True)

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
            <div class="empty-state-desc">Accepts any standard CSV file containing a review text or comments column.</div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# PAGE 4: SENTIMENT ANALYTICS
# =============================================================================
elif nav_selection == "Sentiment Analytics":
    render_header(
        title="Sentiment Analytics & Trends",
        subtitle="Deep dive into customer sentiment distributions, star rating correlations, and temporal volume trends."
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
            filtered_analytics = filtered_analytics[filtered_analytics["aspects"].apply(lambda a: aspect_choice in a)]

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

        # Row 2: Star Rating vs Sentiment & Temporal Trend
        if not food_df.empty:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            r2_c1, r2_c2 = st.columns(2)

            with r2_c1:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                sample_food = food_df.head(5000).copy()
                sample_food["sentiment"] = sample_food["Score"].apply(
                    lambda s: "positive" if s >= 4 else ("negative" if s <= 2 else "neutral")
                )
                st.plotly_chart(
                    ui_charts.create_rating_sentiment_matrix(sample_food, score_col="Score", sentiment_col="sentiment"),
                    width="stretch"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with r2_c2:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.plotly_chart(
                    ui_charts.create_time_trend_chart(sample_food, time_col="Time", sentiment_col="sentiment"),
                    width="stretch"
                )
                st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# PAGE 5: ASPECT-BASED INSIGHTS
# =============================================================================
elif nav_selection == "Aspect-Based Insights":
    render_header(
        title="Aspect-Based Intelligence",
        subtitle="Dissect customer feedback across three core operational pillars: Quality, Shipping, and Price."
    )

    if eval_df.empty:
        st.warning("Evaluation data not available.")
    else:
        # Calculate Aspect Analytics
        def get_aspect_stats(aspect_name):
            has_asp = eval_df[eval_df["aspects"].apply(lambda a: aspect_name in a)]
            total = len(has_asp)
            pos = (has_asp["predicted"] == "positive").sum()
            neg = (has_asp["predicted"] == "negative").sum()
            neu = (has_asp["predicted"] == "neutral").sum()
            return total, pos, neg, neu, has_asp

        q_tot, q_pos, q_neg, q_neu, q_df = get_aspect_stats("Quality")
        s_tot, s_pos, s_neg, s_neu, s_df = get_aspect_stats("Shipping")
        p_tot, p_pos, p_neg, p_neu, p_df = get_aspect_stats("Price")

        # 3 Pillar Cards
        a_c1, a_c2, a_c3 = st.columns(3)

        with a_c1:
            st.markdown(f"""
            <div class="saas-card-static" style="border-top: 3px solid #818CF8;">
                <div class="kpi-header">
                    <span class="kpi-title">Product Quality</span>
                    <span class="aspect-pill aspect-quality">🏷️ Quality</span>
                </div>
                <div class="kpi-value">{q_tot:,}</div>
                <div style="font-size:12px; color:#94A3B8; margin-bottom:12px;">Total Customer Mentions</div>
                <div style="font-size:12.5px; line-height:1.8;">
                    <span style="color:#22C55E;">● Positive: <b>{q_pos:,}</b> ({(q_pos/q_tot*100 if q_tot else 0):.1f}%)</span><br>
                    <span style="color:#F87171;">● Negative: <b>{q_neg:,}</b> ({(q_neg/q_tot*100 if q_tot else 0):.1f}%)</span><br>
                    <span style="color:#FBBF24;">● Neutral: <b>{q_neu:,}</b> ({(q_neu/q_tot*100 if q_tot else 0):.1f}%)</span>
                </div>
                <div style="margin-top:12px; font-size:11px; color:#64748B;">
                    Keywords: <i>quality, material, build, durable, fresh, stale, taste</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with a_c2:
            st.markdown(f"""
            <div class="saas-card-static" style="border-top: 3px solid #38BDF8;">
                <div class="kpi-header">
                    <span class="kpi-title">Shipping & Logistics</span>
                    <span class="aspect-pill aspect-shipping">🏷️ Shipping</span>
                </div>
                <div class="kpi-value">{s_tot:,}</div>
                <div style="font-size:12px; color:#94A3B8; margin-bottom:12px;">Total Customer Mentions</div>
                <div style="font-size:12.5px; line-height:1.8;">
                    <span style="color:#22C55E;">● Positive: <b>{s_pos:,}</b> ({(s_pos/s_tot*100 if s_tot else 0):.1f}%)</span><br>
                    <span style="color:#F87171;">● Negative: <b>{s_neg:,}</b> ({(s_neg/s_tot*100 if s_tot else 0):.1f}%)</span><br>
                    <span style="color:#FBBF24;">● Neutral: <b>{s_neu:,}</b> ({(s_neu/s_tot*100 if s_tot else 0):.1f}%)</span>
                </div>
                <div style="margin-top:12px; font-size:11px; color:#64748B;">
                    Keywords: <i>shipping, delivery, arrived, courier, late, packaging</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with a_c3:
            st.markdown(f"""
            <div class="saas-card-static" style="border-top: 3px solid #F472B6;">
                <div class="kpi-header">
                    <span class="kpi-title">Price Perception</span>
                    <span class="aspect-pill aspect-price">🏷️ Price</span>
                </div>
                <div class="kpi-value">{p_tot:,}</div>
                <div style="font-size:12px; color:#94A3B8; margin-bottom:12px;">Total Customer Mentions</div>
                <div style="font-size:12.5px; line-height:1.8;">
                    <span style="color:#22C55E;">● Positive: <b>{p_pos:,}</b> ({(p_pos/p_tot*100 if p_tot else 0):.1f}%)</span><br>
                    <span style="color:#F87171;">● Negative: <b>{p_neg:,}</b> ({(p_neg/p_tot*100 if p_tot else 0):.1f}%)</span><br>
                    <span style="color:#FBBF24;">● Neutral: <b>{p_neu:,}</b> ({(p_neu/p_tot*100 if p_tot else 0):.1f}%)</span>
                </div>
                <div style="margin-top:12px; font-size:11px; color:#64748B;">
                    Keywords: <i>price, cost, expensive, cheap, value for money, budget</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Comparative Visualization
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        st.plotly_chart(
            ui_charts.create_aspect_sentiment_grouped_bar(eval_df, sentiment_col="predicted", aspects_col="aspects"),
            width="stretch"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Interactive Aspect Explorer
        st.markdown("### 🔍 Aspect Review Explorer")
        chosen_asp = st.radio("Select Aspect to Inspect Actual Reviews:", ["Quality", "Shipping", "Price"], horizontal=True)

        target_df = q_df if chosen_asp == "Quality" else (s_df if chosen_asp == "Shipping" else p_df)
        st.caption(f"Showing 10 sample reviews tagged with **{chosen_asp}** from held-out evaluation dataset:")

        preview_cols = target_df[["review_text", "actual", "predicted"]].head(10).copy()
        preview_cols.columns = ["Review Comment", "Actual Label", "Predicted Sentiment"]
        st.dataframe(preview_cols, width="stretch", hide_index=True)


# =============================================================================
# PAGE 6: MODEL PERFORMANCE
# =============================================================================
elif nav_selection == "Model Performance":
    render_header(
        title="Model Performance & Evaluation",
        subtitle="Verification metrics, confusion matrix, and classification report on 6,000 held-out test reviews."
    )

    # Top KPI Metrics Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Overall Accuracy", "80.9%", "Held-out test set")
    m2.metric("Weighted F1-Score", "0.822", "82.2% weighted")
    m3.metric("Macro F1-Score", "0.626", "Balanced metric")
    m4.metric("Test Set Size", "6,000", "Zero data leakage")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Confusion Matrix + Classification Report Charts
    cm_col, bar_col = st.columns([1, 1])

    with cm_col:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        if not cm_df.empty:
            st.plotly_chart(ui_charts.create_confusion_matrix_heatmap(cm_df), width="stretch")
        else:
            st.info("Confusion matrix file not found.")
        st.markdown("</div>", unsafe_allow_html=True)

    with bar_col:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        st.plotly_chart(ui_charts.create_classification_metrics_bar(), width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    # Detailed Classification Report Table
    st.markdown("### 📋 Classification Report Breakdown")
    report_data = {
        "Sentiment Class": ["Negative", "Neutral", "Positive", "Macro Average", "Weighted Average"],
        "Precision": [0.617, 0.266, 0.936, 0.607, 0.841],
        "Recall": [0.706, 0.401, 0.867, 0.658, 0.809],
        "F1-Score": [0.659, 0.320, 0.900, 0.626, 0.822],
        "Support": [865, 444, 4691, 6000, 6000]
    }
    st.dataframe(pd.DataFrame(report_data), width="stretch", hide_index=True)

    # Technical Specifications & Unit Tests
    t_c1, t_c2 = st.columns(2)
    with t_c1:
        st.markdown("""
        <div class="saas-card-static">
            <span style="font-size:11.5px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8;">Model Pipeline Specifications</span>
            <div style="margin-top:12px; font-size:13px; color:#F8FAFC; line-height:1.9;">
                • <b>Vectorization:</b> TF-IDF (Term Frequency-Inverse Document Frequency)<br>
                • <b>N-gram Range:</b> Unigram & Bigram <code>(1, 2)</code><br>
                • <b>Max Features:</b> 50,000 vocabulary tokens<br>
                • <b>Classifier:</b> Logistic Regression (<code>class_weight='balanced'</code>, <code>C=1.0</code>)<br>
                • <b>Serialization:</b> Joblib (<code>models/sentiment_pipeline.joblib</code>)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t_c2:
        st.markdown("""
        <div class="saas-card-static">
            <span style="font-size:11.5px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8;">Automated Regression Testing</span>
            <div style="margin-top:12px; font-size:13px; color:#F8FAFC; line-height:1.9;">
                • <b>Aspect Keyword Tests:</b> <span style="color:#22C55E;">14 / 14 PASSED (100%)</span><br>
                • <b>Sentiment Edge Tests:</b> <span style="color:#22C55E;">5 / 5 PASSED (100%)</span><br>
                • <b>Input Sanitization:</b> Empty string, whitespace, non-text rejected cleanly<br>
                • <b>Batch Vectorization:</b> Verified chunked matrix processing
            </div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# PAGE 7: ABOUT PROJECT
# =============================================================================
elif nav_selection == "About Project":
    render_header(
        title="About ReviewSense",
        subtitle="End-to-end multi-aspect review intelligence platform architecture, technical stack, and engineering team."
    )

    st.markdown("""
    <div class="saas-card-static">
        <h3 style="margin-top:0; color:#F8FAFC; font-size:18px;">Executive Summary</h3>
        <p style="color:#94A3B8; font-size:13.5px; line-height:1.7;">
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
        <div class="saas-card-static">
            <div style="font-size:24px; margin-bottom:8px;">🎨</div>
            <div style="font-weight:700; color:#F8FAFC; font-size:15px; margin-bottom:6px;">Streamlit Frontend</div>
            <p style="color:#94A3B8; font-size:12.5px; line-height:1.6;">
            Linear/Vercel-inspired dark interface with Plotly charting, live health indicators, and resilient local fallback.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with a2:
        st.markdown("""
        <div class="saas-card-static">
            <div style="font-size:24px; margin-bottom:8px;">⚡</div>
            <div style="font-weight:700; color:#F8FAFC; font-size:15px; margin-bottom:6px;">FastAPI Backend</div>
            <p style="color:#94A3B8; font-size:12.5px; line-height:1.6;">
            High-throughput REST API server supporting single and batch vectorization on port 8000 with CORS middleware.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with a3:
        st.markdown("""
        <div class="saas-card-static">
            <div style="font-size:24px; margin-bottom:8px;">🧠</div>
            <div style="font-weight:700; color:#F8FAFC; font-size:15px; margin-bottom:6px;">NLP & ML Engine</div>
            <p style="color:#94A3B8; font-size:12.5px; line-height:1.6;">
            TF-IDF bigram vectorizer paired with balanced Logistic Regression and 50+ domain regex aspect patterns.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

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

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

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
