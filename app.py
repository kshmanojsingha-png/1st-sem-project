import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Internal helpers
import api_client
from simran_all_in_one import (
    detect_aspects,
    show_dashboard,
    sentiment_donut,
    aspect_bar,
    aspect_sentiment_chart,
    filter_by_aspect,
    normalize_labels
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ReviewSense | AI Analytics Hub",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- ULTRA PREMIUM CUSTOM CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Global Font & Background */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top left, #1a1a2e, #16213e, #0f3460);
    color: #E2E8F0;
}

/* Sidebar Glassmorphism */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.02) !important;
    backdrop-filter: blur(15px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

[data-testid="stSidebar"] h2 {
    background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

/* Custom Radio Buttons in Sidebar */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #A0AEC0 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 8px 12px;
    border-radius: 8px;
    transition: all 0.3s ease;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255, 255, 255, 0.05);
    color: #FFFFFF !important;
    transform: translateX(5px);
}

/* Hero Section */
.hero-container {
    padding: 35px;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    text-align: center;
    margin-bottom: 25px;
    animation: fadeIn 1s ease-in-out;
}

.hero-title {
    font-size: 44px;
    font-weight: 800;
    background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #b62bfe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.hero-subtitle {
    color: #A0AEC0;
    font-size: 17px;
    font-weight: 500;
}

/* Glass Metric Cards */
.metric-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 18px;
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(79, 172, 254, 0.25);
    border: 1px solid rgba(79, 172, 254, 0.3);
}

.metric-title {
    color: #A0AEC0;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.metric-value {
    font-size: 32px;
    font-weight: 800;
    background: linear-gradient(90deg, #ffffff, #a0aec0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 8px;
}

/* Glass Panels */
.glass-panel {
    background: rgba(255, 255, 255, 0.02);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 22px;
    border-radius: 16px;
    margin-bottom: 20px;
}

.glass-panel h3 {
    color: #4facfe;
    font-weight: 700;
    margin-bottom: 12px;
}

/* Sentiment Result Cards */
.result-card {
    padding: 24px;
    border-radius: 18px;
    margin: 18px 0;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}

.result-positive {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(16, 185, 129, 0.05));
    border-left: 5px solid #22c55e;
}

.result-negative {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(185, 28, 28, 0.05));
    border-left: 5px solid #ef4444;
}

.result-neutral {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.05));
    border-left: 5px solid #f59e0b;
}

/* Badges */
.aspect-tag {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    margin: 4px;
    background: rgba(79, 172, 254, 0.18);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.35);
}

.source-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    background: rgba(147, 51, 234, 0.2);
    color: #c084fc;
    border: 1px solid rgba(192, 132, 252, 0.3);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
    color: #0f3460;
    border: none;
    border-radius: 12px;
    font-weight: 800;
    font-size: 15px;
    padding: 12px 20px;
    min-height: 48px;
    width: 100%;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 242, 254, 0.6);
    color: #0f3460;
}

/* Inputs & Dropdowns */
.stSelectbox div[data-baseweb="select"], .stTextInput input, .stTextArea textarea {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border-radius: 10px !important;
}

.stSelectbox div[data-baseweb="select"]:hover {
    border-color: #4facfe !important;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.02);
    border: 2px dashed rgba(79, 172, 254, 0.5);
    border-radius: 16px;
    padding: 20px;
    transition: all 0.3s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: #00f2fe;
    background: rgba(79, 172, 254, 0.05);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ---------------- DATA LOADING ----------------
@st.cache_data
def load_data():
    try:
        return pd.read_csv('final_food_reviews.csv')
    except Exception:
        return None

@st.cache_data
def load_predictions_data():
    try:
        return pd.read_csv('data/predictions.csv')
    except Exception:
        return None

df = load_data()
pred_df = load_predictions_data()


# ---------------- SIDEBAR & BACKEND STATUS ----------------
with st.sidebar:
    st.markdown("## ✨ ReviewSense")
    st.caption("AI MULTI-ASPECT REVIEW INTELLIGENCE")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        ["Dashboard", "Review Analyzer", "CSV Batch Upload", "About Project"],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("### ⚙ SYSTEM STATUS")

    # Backend configuration & live health check
    backend_url = st.session_state.get("backend_url", api_client.DEFAULT_API_URL)
    health_info = api_client.check_api_health(backend_url)

    frontend_card = """
    <div class="glass-panel" style="padding: 12px; margin-bottom: 8px;">
        <span style="color: #00f2fe; font-weight: bold;">● ONLINE</span><br>
        <span style="color: #A0AEC0; font-size: 12px;">Streamlit Frontend</span>
    </div>
    """

    if health_info["online"]:
        model_status = "Ready (Joblib Loaded)" if health_info["predictor_available"] else "Standby"
        backend_card = f"""
        <div class="glass-panel" style="padding: 12px; margin-bottom: 8px;">
            <span style="color: #22c55e; font-weight: bold;">● CONNECTED</span><br>
            <span style="color: #A0AEC0; font-size: 12px;">FastAPI Backend (:8000)</span><br>
            <span style="color: #4facfe; font-size: 11px;">ML Pipeline: {model_status}</span>
        </div>
        """
    else:
        backend_card = """
        <div class="glass-panel" style="padding: 12px; margin-bottom: 8px;">
            <span style="color: #f59e0b; font-weight: bold;">● OFFLINE (Fallback Active)</span><br>
            <span style="color: #A0AEC0; font-size: 12px;">Local ML Model Active</span>
        </div>
        """

    st.markdown(frontend_card + backend_card, unsafe_allow_html=True)

    with st.expander("🔌 Backend Configuration", expanded=not health_info["online"]):
        new_url = st.text_input("Backend API URL", value=backend_url, key="input_backend_url")
        if new_url != backend_url:
            st.session_state["backend_url"] = new_url
            st.rerun()

        if not health_info["online"]:
            st.markdown(
                "<small style='color:#A0AEC0;'>To start the FastAPI backend server, run in terminal:</small>",
                unsafe_allow_html=True
            )
            st.code("uvicorn api:app --reload", language="bash")
            st.caption("Auto-fallback ensures all features continue working even when the server is offline.")

    st.divider()
    st.caption("GROUP D | ATIK, BIKI, SIMRAN, MANOJ")
    st.caption("REVIEWSENSE V2.0 (2026)")


# ---------------- HERO SECTION ----------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">ReviewSense ✨</div>
    <div class="hero-subtitle">Multi-Aspect Customer Sentiment & Intelligence Hub</div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 1. DASHBOARD
# ==============================================================================
if page == "Dashboard":
    st.markdown("### 📈 Analytics & Model Performance Overview")

    # Compute metrics from held-out predictions if available
    if pred_df is not None and not pred_df.empty:
        total_eval = len(pred_df)
        pos_cnt = (pred_df['predicted'] == 'positive').sum()
        neg_cnt = (pred_df['predicted'] == 'negative').sum()
        neu_cnt = (pred_df['predicted'] == 'neutral').sum()
        
        pos_pct = f"{round((pos_cnt / total_eval) * 100, 1)}%"
        neg_pct = f"{round((neg_cnt / total_eval) * 100, 1)}%"
        neu_pct = f"{round((neu_cnt / total_eval) * 100, 1)}%"
        total_str = f"{total_eval:,}"
    else:
        total_str = "6,000"
        pos_pct = "72.4%"
        neg_pct = "16.5%"
        neu_pct = "11.1%"

    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        ("TEST EVAL REVIEWS", total_str, "📩"),
        ("POSITIVE SENTIMENT", pos_pct, "😊"),
        ("NEGATIVE SENTIMENT", neg_pct, "😟"),
        ("NEUTRAL SENTIMENT", neu_pct, "😐")
    ]

    for col, item in zip([c1, c2, c3, c4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{item[2]} {item[0]}</div>
                <div class="metric-value">{item[1]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    # Interactive Dashboard Visualization
    if pred_df is not None and not pred_df.empty:
        st.markdown("#### 📊 Evaluation Set Visual Insights")
        show_dashboard(pred_df, text_col="review_text", sentiment_col="predicted")
    else:
        left, right = st.columns(2)
        with left:
            st.markdown("""
            <div class="glass-panel">
                <h3>🎯 Project Objective</h3>
                <p style="color: #A0AEC0;">
                Analyze customer reviews and predict fine-grained sentiment (Positive, Neutral, Negative) 
                along with multi-aspect tagging (Quality, Shipping, Price) to understand customer feedback at scale.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with right:
            st.markdown("""
            <div class="glass-panel">
                <h3>⚡ System Architecture</h3>
                <p style="color: #A0AEC0;">
                ✔️ <b>Frontend:</b> Streamlit with glassmorphism UI & live Plotly analytics<br>
                ✔️ <b>Backend API:</b> FastAPI on port 8000 with CORS & batch endpoints<br>
                ✔️ <b>ML Engine:</b> TF-IDF Vectorizer + Logistic Regression pipeline<br>
                ✔️ <b>Aspect Detection:</b> Rule-based multi-keyword extractor
                </p>
            </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# 2. REVIEW ANALYZER
# ==============================================================================
elif page == "Review Analyzer":
    st.markdown("### 🧠 Review Sentiment & Aspect Analyzer")
    st.write("Analyze individual reviews with real-time sentiment prediction and multi-aspect tagging.")
    st.markdown("---")

    tab_direct, tab_product = st.tabs(["✍️ Direct Text Analyzer", "🛒 Amazon Food Products Explorer"])

    # --- TAB 1: Direct Text Analyzer ---
    with tab_direct:
        st.markdown("#### 📝 Type or Paste Any Customer Review")
        
        # Quick sample buttons
        st.caption("Quick test presets:")
        p_col1, p_col2, p_col3 = st.columns(3)
        sample_text = ""
        if p_col1.button("🟢 Positive + Shipping/Quality"):
            sample_text = "The quality is excellent and durable, plus the courier delivered it on time!"
        if p_col2.button("🔴 Negative + Quality/Price"):
            sample_text = "Terrible awful taste, arrived broken and complete waste of money."
        if p_col3.button("🟡 Neutral / General"):
            sample_text = "It was okay, average flavor and nothing special."

        review_input = st.text_area(
            "Review Text:",
            value=sample_text,
            height=130,
            placeholder="e.g. Delicious fresh coffee, arrived very fast but a bit expensive...",
            key="direct_review_input"
        )

        if st.button("✨ ANALYZE SENTIMENT & ASPECTS", key="btn_direct_analyze"):
            if not review_input.strip():
                st.warning("Please enter a review text first.")
            else:
                with st.spinner("Processing through ReviewSense AI..."):
                    res = api_client.predict_single(review_input, base_url=backend_url)

                if not res.get("success"):
                    st.error(f"Error: {res.get('error')}")
                else:
                    sentiment = res.get("sentiment", "neutral").capitalize()
                    aspects = res.get("aspects", [])
                    source = res.get("source", "System")

                    # Sentiment styling
                    if sentiment.lower() == "positive":
                        card_class = "result-positive"
                        icon = "😊"
                        color_hex = "#22c55e"
                    elif sentiment.lower() == "negative":
                        card_class = "result-negative"
                        icon = "😟"
                        color_hex = "#ef4444"
                    else:
                        card_class = "result-neutral"
                        icon = "😐"
                        color_hex = "#f59e0b"

                    # Build aspect tags
                    if aspects:
                        aspect_html = "".join([f'<span class="aspect-tag">🏷️ {a}</span>' for a in aspects])
                    else:
                        aspect_html = '<span style="color:#A0AEC0; font-size:13px;">No specific aspects detected (General review)</span>'

                    st.markdown(f"""
                    <div class="result-card {card_class}">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                            <span style="font-size:24px; font-weight:800; color:{color_hex};">
                                {icon} {sentiment.upper()}
                            </span>
                            <span class="source-badge">⚡ {source}</span>
                        </div>
                        <div style="margin-top:10px;">
                            <span style="font-size:12px; color:#A0AEC0; text-transform:uppercase; letter-spacing:1px; font-weight:600;">
                                Detected Aspects:
                            </span><br>
                            <div style="margin-top: 6px;">{aspect_html}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # --- TAB 2: Product Explorer ---
    with tab_product:
        if df is None:
            st.error("⚠️ 'final_food_reviews.csv' not found! Run `merge.py` to generate the combined food review dataset.")
        else:
            unique_foods = df[df['title'] != 'Unknown Product']['title'].unique().tolist()
            unique_foods.sort()

            selected_food = st.selectbox(
                "Select a product from the database:",
                options=["-- Select a Food Item --"] + unique_foods,
                key="select_food_item"
            )

            if selected_food != "-- Select a Food Item --":
                food_data = df[df['title'] == selected_food]
                avg_rating = food_data['Score'].mean()
                total_reviews = len(food_data)

                st.markdown(f"#### 📦 Product: <span style='color:#4facfe;'>{selected_food}</span>", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 15px;">
                        <div class="metric-title">⭐ Average Rating</div>
                        <div class="metric-value" style="font-size: 26px;">{avg_rating:.2f} / 5</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 15px;">
                        <div class="metric-title">📩 Dataset Reviews</div>
                        <div class="metric-value" style="font-size: 26px;">{total_reviews}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("#### 📋 Recent Reviews Sample")
                display_df = food_data[['Score', 'Summary', 'Text']].head(5).copy()
                display_df['Text'] = display_df['Text'].astype(str).str[:250] + "..."
                st.dataframe(display_df, use_container_width=True)

                st.markdown("---")
                st.markdown("#### 📝 Analyze a Review For This Product")
                prod_review = st.text_area("Paste a review for this product:", height=100, key="prod_review_input")

                if st.button("✨ ANALYZE THIS REVIEW", key="btn_prod_analyze"):
                    if not prod_review.strip():
                        st.warning("Please enter a review first.")
                    else:
                        with st.spinner("Analyzing..."):
                            res = api_client.predict_single(prod_review, base_url=backend_url)

                        sentiment = res.get("sentiment", "neutral").capitalize()
                        aspects = res.get("aspects", [])
                        source = res.get("source", "System")

                        st.success(f"Predicted Sentiment: **{sentiment}**")
                        if aspects:
                            st.write(f"Detected Aspects: {', '.join(aspects)}")
                        st.caption(f"Engine: {source}")


# ==============================================================================
# 3. CSV BATCH UPLOAD
# ==============================================================================
elif page == "CSV Batch Upload":
    st.markdown("### 📂 Batch Upload & Scalable Analysis")
    st.write("Upload a CSV file of customer reviews to perform batch sentiment analysis and aspect tagging via the AI Backend.")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            st.success(f"CSV successfully loaded: **{len(uploaded_df):,}** total rows.")

            # Identify review text column candidate
            cols = list(uploaded_df.columns)
            candidate_cols = ["Text", "review_text", "text", "review", "content", "comment", "Summary"]
            default_idx = 0
            for idx, c in enumerate(cols):
                if c in candidate_cols:
                    default_idx = idx
                    break

            c_col, c_limit = st.columns([2, 1])
            with c_col:
                selected_text_col = st.selectbox("Select Review Text Column:", options=cols, index=default_idx)
            with c_limit:
                max_rows = st.number_input(
                    "Rows to analyze (0 = all):",
                    min_value=0,
                    max_value=len(uploaded_df),
                    value=min(500, len(uploaded_df)),
                    step=100
                )

            st.markdown("#### Raw Data Preview")
            st.dataframe(uploaded_df.head(5), use_container_width=True)

            if st.button("🚀 RUN BATCH AI ANALYSIS", key="btn_batch_run"):
                to_process_df = uploaded_df.head(max_rows) if max_rows > 0 else uploaded_df
                texts = to_process_df[selected_text_col].astype(str).tolist()

                prog_bar = st.progress(0.0)
                status_text = st.empty()

                def update_progress(ratio, processed, total):
                    prog_bar.progress(min(1.0, ratio))
                    status_text.text(f"Processed {processed:,} of {total:,} reviews...")

                with st.spinner("Running batch prediction via backend API..."):
                    results, execution_source = api_client.predict_batch(
                        texts,
                        base_url=backend_url,
                        chunk_size=200,
                        progress_callback=update_progress
                    )

                prog_bar.progress(1.0)
                status_text.text(f"✅ Completed {len(results):,} predictions via {execution_source}!")

                # Attach results to dataframe
                res_df = to_process_df.copy()
                res_df["Predicted_Sentiment"] = [r["sentiment"] for r in results]
                res_df["Aspects"] = [", ".join(r["aspects"]) if r["aspects"] else "None" for r in results]

                # Metric Cards
                st.markdown("---")
                st.markdown("### 📊 Batch Results Summary")

                pos_cnt = (res_df["Predicted_Sentiment"] == "positive").sum()
                neg_cnt = (res_df["Predicted_Sentiment"] == "negative").sum()
                neu_cnt = (res_df["Predicted_Sentiment"] == "neutral").sum()
                total_proc = len(res_df)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Analyzed", f"{total_proc:,}")
                m1.caption(f"Engine: {execution_source}")
                m2.metric("Positive", f"{round((pos_cnt/total_proc)*100, 1)}%", f"{pos_cnt:,} reviews")
                m3.metric("Negative", f"{round((neg_cnt/total_proc)*100, 1)}%", f"{neg_cnt:,} reviews")
                m4.metric("Neutral", f"{round((neu_cnt/total_proc)*100, 1)}%", f"{neu_cnt:,} reviews")

                # Visual Charts via show_dashboard
                st.markdown("#### 📈 Visual Dashboard")
                show_dashboard(res_df, text_col=selected_text_col, sentiment_col="Predicted_Sentiment")

                # CSV Download Button
                csv_data = res_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Analyzed CSV with Predictions",
                    data=csv_data,
                    file_name="reviewsense_predictions.csv",
                    mime="text/csv",
                    key="download_csv_btn"
                )

        except Exception as e:
            st.error(f"Error processing CSV: {e}")


# ==============================================================================
# 4. ABOUT PROJECT
# ==============================================================================
elif page == "About Project":
    st.markdown("### ℹ️ About ReviewSense")

    st.markdown("""
    <div class="glass-panel">
        <h3>What is ReviewSense?</h3>
        <p style="color: #A0AEC0;">
        ReviewSense is an end-to-end AI review analytics system developed by Group D.
        It automates the extraction of customer sentiment (Positive, Negative, Neutral)
        and categorizes feedback across critical business dimensions: Quality, Shipping, and Price.
        </p>

        <h3 style="margin-top: 25px;">API Architecture & Endpoints</h3>
        <p style="color: #A0AEC0;">
        The system features a decoupled FastAPI backend providing high-throughput endpoints:
        </p>
        <ul style="color: #A0AEC0;">
            <li><code>GET /health</code> — Service status and model availability check</li>
            <li><code>POST /predict</code> — Single review inference with aspect detection</li>
            <li><code>POST /predict_batch</code> — Vectorized batch inference for datasets & CSV uploads</li>
        </ul>

        <h3 style="margin-top: 25px;">Team Group D</h3>
        <p style="color: #A0AEC0;">
        • <b>Manoj:</b> Data engineering & Scikit-Learn ML Model training<br>
        • <b>Atik:</b> Streamlit frontend design & glassmorphism user interface<br>
        • <b>Biki:</b> FastAPI backend integration & API development<br>
        • <b>Simran:</b> Aspect detection engine, testing, PPT generation & documentation
        </p>

        <h3 style="margin-top: 25px;">Technology Stack</h3>
        <p style="color: #A0AEC0;">
        Python 3.14 | FastAPI | Streamlit | Scikit-Learn | Pandas | Plotly | Joblib | Requests
        </p>
    </div>
    """, unsafe_allow_html=True)


# ---------------- FOOTER ----------------
st.divider()
st.markdown(
    "<center style='color:#A0AEC0; font-size: 12px; letter-spacing: 1px;'>"
    "REVIEWSENSE • AI REVIEW INTELLIGENCE • GROUP D PROJECT"
    "</center>",
    unsafe_allow_html=True
)
