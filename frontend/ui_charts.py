"""
ReviewSense - UI Chart Components (Premium Edition)
Plotly-based charts matching the Linear/Vercel dark SaaS design system
Configured for Projector Presentation Readability (15-18px information text)
Enhanced with premium visual effects: glow lines, gradient fills, smooth animations
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
from ui_theme import SENTIMENT_COLORS, ASPECT_COLORS

# ---------------------------------------------------------------------------
# Global base layout – used as a spread across every chart
# ---------------------------------------------------------------------------
BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94A3B8", size=15),
    margin=dict(l=28, r=28, t=52, b=28),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=15, color="#F8FAFC"),
        bgcolor="rgba(0,0,0,0)",
    ),
    hoverlabel=dict(
        bgcolor="#1C2537",
        font_color="#F8FAFC",
        font_family="Inter, sans-serif",
        font_size=16,
        bordercolor="#334155",
    ),
)

# ---------------------------------------------------------------------------
# Shared animation config applied to every figure
# ---------------------------------------------------------------------------
ANIMATION_CONFIG = dict(
    displayModeBar=False,
    scrollZoom=False,
)

# Shared title builder
def _title(text: str) -> dict:
    return dict(
        text=text,
        font=dict(size=15, color="#F8FAFC", family="Plus Jakarta Sans"),
        x=0.02,
        y=0.98,
    )

# Shared axis defaults
_XAXIS_CLEAN = dict(
    showline=False,
    zeroline=False,
    showgrid=True,
    gridcolor="rgba(30,41,59,0.55)",
    griddash="dot",
    tickfont=dict(color="#94A3B8", size=15, family="Inter, sans-serif"),
)

_YAXIS_CLEAN = dict(
    showline=False,
    zeroline=False,
    showgrid=True,
    gridcolor="rgba(30,41,59,0.55)",
    griddash="dot",
    tickfont=dict(color="#94A3B8", size=15, family="Inter, sans-serif"),
)

def _xaxis(**kwargs):
    d = dict(_XAXIS_CLEAN)
    d.update(kwargs)
    return d

def _yaxis(**kwargs):
    d = dict(_YAXIS_CLEAN)
    d.update(kwargs)
    return d


# ═══════════════════════════════════════════════════════════════════════════
# 1. SENTIMENT DONUT → Premium Ring Chart
# ═══════════════════════════════════════════════════════════════════════════
def create_sentiment_donut(df: pd.DataFrame, sentiment_col: str = "sentiment") -> go.Figure:
    """Creates a premium ring chart showing sentiment distribution with shadow ring and glow."""
    if df.empty or sentiment_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT, height=420)
        return fig

    counts = df[sentiment_col].str.lower().value_counts().reset_index()
    counts.columns = ["sentiment", "count"]
    total = counts["count"].sum()

    color_seq = [SENTIMENT_COLORS.get(s, "#8B7CFF") for s in counts["sentiment"]]

    # Build pull list matching number of segments
    n_segments = len(counts)
    pull_values = [0.03] * n_segments

    # --- Shadow ring (invisible trace behind donut for depth) ---
    shadow_colors = ["rgba(15,23,42,0.45)"] * n_segments
    fig = go.Figure()

    fig.add_trace(
        go.Pie(
            labels=counts["sentiment"].str.capitalize(),
            values=counts["count"],
            hole=0.70,
            marker=dict(
                colors=shadow_colors,
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            textinfo="none",
            hoverinfo="skip",
            sort=False,
            showlegend=False,
            domain=dict(x=[0.02, 0.98], y=[0.02, 0.98]),
        )
    )

    # --- Main donut ring ---
    fig.add_trace(
        go.Pie(
            labels=counts["sentiment"].str.capitalize(),
            values=counts["count"],
            hole=0.72,
            marker=dict(
                colors=color_seq,
                line=dict(color="#151C2C", width=3),
            ),
            pull=pull_values,
            rotation=135,
            textinfo="percent",
            textfont=dict(size=16, color="#F8FAFC", family="Inter, sans-serif"),
            hovertemplate=(
                "<b style='font-size:15px;'>%{label}</b><br>"
                "<span style='color:#94A3B8;'>Count:</span> %{value:,}<br>"
                "<span style='color:#94A3B8;'>Share:</span> %{percent}<br>"
                "<extra></extra>"
            ),
            sort=False,
        )
    )

    fig.update_layout(
        **BASE_LAYOUT,
        height=420,
        annotations=[
            dict(
                text=(
                    f"<span style='font-size:36px; font-weight:800; color:#F8FAFC;"
                    f" font-family:Plus Jakarta Sans;'>{total:,}</span>"
                    f"<br><span style='font-size:13px; color:#64748B;"
                    f" text-transform:uppercase; letter-spacing:0.1em;"
                    f" font-weight:600;'>total reviews</span>"
                ),
                x=0.5,
                y=0.5,
                font=dict(family="Plus Jakarta Sans, sans-serif"),
                showarrow=False,
            )
        ],
        title=_title("Sentiment Distribution"),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 2. ASPECT BAR → Premium Horizontal Bars with Gradient Effect
# ═══════════════════════════════════════════════════════════════════════════
def create_aspect_bar(df: pd.DataFrame, aspects_col: str = "aspects") -> go.Figure:
    """Creates horizontal bars with gradient-like layering and smart value labels."""
    if df.empty or aspects_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT, height=420)
        return fig

    # Handle string lists or actual lists
    exploded = df[aspects_col].apply(
        lambda x: x if isinstance(x, list) else (str(x).split(", ") if str(x).strip() and str(x) != "None" else [])
    ).explode().dropna()

    exploded = exploded[exploded.isin(["Quality", "Shipping", "Price"])]
    if exploded.empty:
        counts = pd.DataFrame({"aspect": ["Quality", "Shipping", "Price"], "count": [0, 0, 0]})
    else:
        counts = exploded.value_counts().reset_index()
        counts.columns = ["aspect", "count"]

    # Fixed order
    order = ["Quality", "Shipping", "Price"]
    counts = counts.set_index("aspect").reindex(order).fillna(0).reset_index()

    colors = [ASPECT_COLORS.get(a, "#8B7CFF") for a in counts["aspect"]]
    max_val = counts["count"].max() if counts["count"].max() > 0 else 1

    fig = go.Figure()

    # --- Background bar (track) for each aspect ---
    fig.add_trace(
        go.Bar(
            x=[max_val * 1.15] * len(counts),
            y=counts["aspect"],
            orientation="h",
            marker=dict(
                color="rgba(30,41,59,0.35)",
                line=dict(width=0),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # --- Gradient layer: lighter bar behind main (glow effect) ---
    glow_colors = []
    for c in colors:
        # make a lighter, transparent version
        glow_colors.append(c.replace(")", ", 0.18)").replace("rgb", "rgba") if "rgb" in c else c)

    fig.add_trace(
        go.Bar(
            x=counts["count"] * 1.02,
            y=counts["aspect"],
            orientation="h",
            marker=dict(
                color=[f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.2)" for c in colors],
                line=dict(width=0),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # --- Main bar ---
    # Decide text position: inside (white) if bar is large enough, outside otherwise
    threshold = max_val * 0.25
    text_positions = ["inside" if v > threshold else "outside" for v in counts["count"]]

    fig.add_trace(
        go.Bar(
            x=counts["count"],
            y=counts["aspect"],
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="#151C2C", width=1),
            ),
            text=counts["count"].apply(lambda v: f"  {int(v):,}  "),
            textposition=text_positions,
            textfont=dict(size=16, color="#F8FAFC", family="Inter, sans-serif", weight=600),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "<span style='color:#94A3B8;'>Mentions:</span> %{x:,}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **BASE_LAYOUT,
        height=420,
        barmode="overlay",
        showlegend=False,
        title=_title("Aspect Frequency"),
        xaxis=_xaxis(
            showgrid=True,
            visible=False,
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False,
            showline=False,
            tickfont=dict(color="#F8FAFC", size=16, family="Inter, sans-serif"),
        ),
        bargap=0.35,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 3. GROUPED BAR → Stacked Rounded Bars with Labels
# ═══════════════════════════════════════════════════════════════════════════
def create_aspect_sentiment_grouped_bar(
    df: pd.DataFrame, sentiment_col: str = "sentiment", aspects_col: str = "aspects"
) -> go.Figure:
    """Stacked bar chart with data labels for sentiment breakdown per aspect."""
    if df.empty or aspects_col not in df.columns or sentiment_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT, height=420)
        return fig

    data_copy = df.copy()
    data_copy["_aspect_list"] = data_copy[aspects_col].apply(
        lambda x: x if isinstance(x, list) else (str(x).split(", ") if str(x).strip() and str(x) != "None" else [])
    )
    exploded = data_copy.explode("_aspect_list").dropna(subset=["_aspect_list"])
    exploded = exploded[exploded["_aspect_list"].isin(["Quality", "Shipping", "Price"])]

    if exploded.empty:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT, height=420)
        return fig

    exploded[sentiment_col] = exploded[sentiment_col].str.lower()
    grouped = exploded.groupby(["_aspect_list", sentiment_col]).size().unstack(fill_value=0).reset_index()

    for col in ["positive", "neutral", "negative"]:
        if col not in grouped.columns:
            grouped[col] = 0

    # Semi-transparent sentiment colors for stacked look
    SEMI_COLORS = {
        "positive": "rgba(34,197,94,0.85)",
        "neutral": "rgba(251,191,36,0.85)",
        "negative": "rgba(248,113,113,0.85)",
    }

    fig = go.Figure()
    for s_label, col_name in [("Positive", "positive"), ("Neutral", "neutral"), ("Negative", "negative")]:
        fig.add_trace(
            go.Bar(
                name=s_label,
                x=grouped["_aspect_list"],
                y=grouped[col_name],
                marker=dict(
                    color=SEMI_COLORS[col_name],
                    line=dict(color="#151C2C", width=1),
                ),
                text=grouped[col_name].apply(lambda v: f"{int(v):,}" if v > 0 else ""),
                textposition="inside",
                textfont=dict(size=14, color="#F8FAFC", family="Inter, sans-serif", weight=700),
                hovertemplate=(
                    f"<b>{s_label}</b><br>"
                    "<span style='color:#94A3B8;'>Aspect:</span> %{x}<br>"
                    "<span style='color:#94A3B8;'>Count:</span> %{y:,}"
                    "<extra></extra>"
                ),
            )
        )

    # Compute max total for reference line
    totals = grouped[["positive", "neutral", "negative"]].sum(axis=1)
    avg_total = totals.mean()

    fig.add_hline(
        y=avg_total,
        line_dash="dot",
        line_color="rgba(139,124,255,0.4)",
        line_width=1.5,
        annotation_text=f"Avg: {avg_total:.0f}",
        annotation_font=dict(size=13, color="#8B7CFF", family="Inter"),
        annotation_position="top right",
    )

    fig.update_layout(
        **BASE_LAYOUT,
        height=420,
        barmode="stack",
        title=_title("Sentiment Breakdown Across Aspects"),
        xaxis=_xaxis(
            tickfont=dict(color="#F8FAFC", size=16, family="Inter, sans-serif"),
            showgrid=False,
        ),
        yaxis=_yaxis(),
        bargap=0.30,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 4. TIME TREND → Area Chart with Glow Effect
# ═══════════════════════════════════════════════════════════════════════════
def create_time_trend_chart(df: pd.DataFrame, time_col: str = "Time", sentiment_col: str = "sentiment") -> go.Figure:
    """Area chart with gradient fills, glow shadow lines, and marker dots."""
    if df.empty or time_col not in df.columns or sentiment_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT, height=420)
        return fig

    trend_df = df.dropna(subset=[time_col, sentiment_col]).copy()
    trend_df["date"] = pd.to_datetime(trend_df[time_col], unit="s", errors="coerce")
    trend_df = trend_df.dropna(subset=["date"])

    if trend_df.empty:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT, height=420)
        return fig

    trend_df["month_year"] = trend_df["date"].dt.to_period("M").dt.to_timestamp()
    trend_df[sentiment_col] = trend_df[sentiment_col].str.lower()

    grouped = trend_df.groupby(["month_year", sentiment_col]).size().unstack(fill_value=0).reset_index()

    # Fill color mapping (gradient-like via rgba with low alpha)
    FILL_COLORS = {
        "positive": "rgba(34,197,94,0.08)",
        "neutral": "rgba(251,191,36,0.06)",
        "negative": "rgba(248,113,113,0.06)",
    }

    # Glow (shadow) color mapping
    GLOW_COLORS = {
        "positive": "rgba(34,197,94,0.15)",
        "neutral": "rgba(251,191,36,0.12)",
        "negative": "rgba(248,113,113,0.12)",
    }

    fig = go.Figure()

    for s_label, col_name in [("Positive", "positive"), ("Neutral", "neutral"), ("Negative", "negative")]:
        if col_name not in grouped.columns:
            continue

        y_vals = grouped[col_name]
        x_vals = grouped["month_year"]

        # --- Glow / shadow line (wider, lower opacity) ---
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines",
                line=dict(
                    color=GLOW_COLORS[col_name],
                    width=10,
                    shape="spline",
                    smoothing=1.1,
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )

        # --- Main line + filled area ---
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines+markers",
                name=s_label,
                line=dict(
                    color=SENTIMENT_COLORS[col_name],
                    width=3,
                    shape="spline",
                    smoothing=1.1,
                ),
                marker=dict(
                    size=7,
                    color=SENTIMENT_COLORS[col_name],
                    line=dict(color="#151C2C", width=2),
                    symbol="circle",
                ),
                fill="tozeroy",
                fillcolor=FILL_COLORS[col_name],
                hovertemplate=(
                    f"<b>{s_label}</b><br>"
                    "<span style='color:#94A3B8;'>Date:</span> %{x|%b %Y}<br>"
                    "<span style='color:#94A3B8;'>Count:</span> %{y:,}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        **BASE_LAYOUT,
        height=420,
        title=_title("Sentiment Volume Over Time"),
        xaxis=_xaxis(
            tickformat="%b '%y",
            dtick="M1",
        ),
        yaxis=_yaxis(),
        hovermode="x unified",
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 5. RATING × SENTIMENT → Stacked Bars with Labels
# ═══════════════════════════════════════════════════════════════════════════
def create_rating_sentiment_matrix(df: pd.DataFrame, score_col: str = "Score", sentiment_col: str = "sentiment") -> go.Figure:
    """Stacked bar chart of predicted sentiment across star ratings with labels."""
    if df.empty or score_col not in df.columns or sentiment_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT, height=420)
        return fig

    m_df = df.dropna(subset=[score_col, sentiment_col]).copy()
    m_df[sentiment_col] = m_df[sentiment_col].str.lower()
    grouped = m_df.groupby([score_col, sentiment_col]).size().unstack(fill_value=0).reset_index()

    SEMI_COLORS = {
        "positive": "rgba(34,197,94,0.85)",
        "neutral": "rgba(251,191,36,0.85)",
        "negative": "rgba(248,113,113,0.85)",
    }

    fig = go.Figure()
    for s_label, col_name in [("Positive", "positive"), ("Neutral", "neutral"), ("Negative", "negative")]:
        if col_name in grouped.columns:
            fig.add_trace(
                go.Bar(
                    name=s_label,
                    x=[f"{int(s)} ⭐" for s in grouped[score_col]],
                    y=grouped[col_name],
                    marker=dict(
                        color=SEMI_COLORS[col_name],
                        line=dict(color="#151C2C", width=1),
                    ),
                    text=grouped[col_name].apply(lambda v: f"{int(v):,}" if v > 0 else ""),
                    textposition="inside",
                    textfont=dict(size=14, color="#F8FAFC", family="Inter, sans-serif", weight=600),
                    hovertemplate=(
                        f"<b>{s_label}</b><br>"
                        "<span style='color:#94A3B8;'>Rating:</span> %{x}<br>"
                        "<span style='color:#94A3B8;'>Count:</span> %{y:,}"
                        "<extra></extra>"
                    ),
                )
            )

    fig.update_layout(
        **BASE_LAYOUT,
        height=420,
        barmode="stack",
        title=_title("Star Rating vs. Predicted Sentiment"),
        xaxis=_xaxis(
            tickfont=dict(color="#F8FAFC", size=16),
            showgrid=False,
        ),
        yaxis=_yaxis(),
        bargap=0.28,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 6. CONFUSION MATRIX → Premium Heatmap
# ═══════════════════════════════════════════════════════════════════════════
def create_confusion_matrix_heatmap(cm_df: pd.DataFrame) -> go.Figure:
    """Premium heatmap with vibrant colorscale, cell borders, and rich annotations."""
    labels = ["Negative", "Neutral", "Positive"]
    z_values = cm_df.values

    # Annotations with counts + row percentages
    annotations = []
    for i, row in enumerate(z_values):
        row_sum = sum(row)
        for j, val in enumerate(row):
            pct = (val / row_sum * 100) if row_sum > 0 else 0
            annotations.append(
                dict(
                    x=labels[j],
                    y=labels[i],
                    text=(
                        f"<span style='font-size:24px; font-weight:800;"
                        f" font-family:Plus Jakarta Sans;'>{val:,}</span>"
                        f"<br><span style='font-size:14px; opacity:0.80;"
                        f" font-weight:500;'>{pct:.1f}%</span>"
                    ),
                    font=dict(color="#F8FAFC", family="Plus Jakarta Sans"),
                    showarrow=False,
                )
            )

    # Vibrant custom colorscale: deep navy → electric purple → bright cyan
    premium_colorscale = [
        [0.00, "#0A0E1A"],
        [0.15, "#0F172A"],
        [0.30, "#1E1B4B"],
        [0.50, "#4F46E5"],
        [0.70, "#7C3AED"],
        [0.85, "#8B7CFF"],
        [1.00, "#22D3EE"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=labels,
            y=labels,
            colorscale=premium_colorscale,
            showscale=False,
            xgap=3,
            ygap=3,
            hovertemplate=(
                "<b>Actual:</b> %{y}<br>"
                "<b>Predicted:</b> %{x}<br>"
                "<span style='color:#94A3B8;'>Count:</span> %{z:,}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **BASE_LAYOUT,
        height=420,
        annotations=annotations,
        title=_title("Held-out Test Confusion Matrix"),
        xaxis=dict(
            title=dict(
                text="Predicted Label",
                font=dict(size=15, color="#64748B", family="Inter"),
                standoff=12,
            ),
            tickfont=dict(color="#F8FAFC", size=16),
            showgrid=False,
            showline=False,
        ),
        yaxis=dict(
            title=dict(
                text="Actual True Label",
                font=dict(size=15, color="#64748B", family="Inter"),
                standoff=12,
            ),
            autorange="reversed",
            tickfont=dict(color="#F8FAFC", size=16),
            showgrid=False,
            showline=False,
        ),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 7. CLASSIFICATION METRICS → Grouped Bar with Annotations + Reference Lines
# ═══════════════════════════════════════════════════════════════════════════
def create_classification_metrics_bar() -> go.Figure:
    """Grouped bar chart with value annotations, gradient coloring, and threshold lines."""
    classes = ["Negative", "Neutral", "Positive"]
    precision = [0.617, 0.266, 0.936]
    recall = [0.706, 0.401, 0.867]
    f1 = [0.659, 0.320, 0.900]

    # Gradient-like color mapping based on value (low=muted, high=vivid)
    def _value_color(base_rgb: tuple, val: float) -> str:
        """Return rgba string with opacity proportional to metric value."""
        alpha = 0.45 + val * 0.55  # range 0.45 → 1.0
        return f"rgba({base_rgb[0]},{base_rgb[1]},{base_rgb[2]},{alpha:.2f})"

    prec_base = (56, 189, 248)   # Sky blue
    rec_base = (129, 140, 248)   # Indigo
    f1_base = (139, 124, 255)    # Purple

    fig = go.Figure()

    # Precision
    fig.add_trace(
        go.Bar(
            name="Precision",
            x=classes,
            y=precision,
            marker=dict(
                color=[_value_color(prec_base, v) for v in precision],
                line=dict(color="#38BDF8", width=1),
            ),
            text=[f"{v:.3f}" for v in precision],
            textposition="outside",
            textfont=dict(size=14, color="#38BDF8", family="Inter, sans-serif", weight=600),
            hovertemplate=(
                "<b>Precision</b><br>"
                "<span style='color:#94A3B8;'>Class:</span> %{x}<br>"
                "<span style='color:#94A3B8;'>Score:</span> %{y:.3f}"
                "<extra></extra>"
            ),
        )
    )

    # Recall
    fig.add_trace(
        go.Bar(
            name="Recall",
            x=classes,
            y=recall,
            marker=dict(
                color=[_value_color(rec_base, v) for v in recall],
                line=dict(color="#818CF8", width=1),
            ),
            text=[f"{v:.3f}" for v in recall],
            textposition="outside",
            textfont=dict(size=14, color="#818CF8", family="Inter, sans-serif", weight=600),
            hovertemplate=(
                "<b>Recall</b><br>"
                "<span style='color:#94A3B8;'>Class:</span> %{x}<br>"
                "<span style='color:#94A3B8;'>Score:</span> %{y:.3f}"
                "<extra></extra>"
            ),
        )
    )

    # F1-Score
    fig.add_trace(
        go.Bar(
            name="F1-Score",
            x=classes,
            y=f1,
            marker=dict(
                color=[_value_color(f1_base, v) for v in f1],
                line=dict(color="#8B7CFF", width=1),
            ),
            text=[f"{v:.3f}" for v in f1],
            textposition="outside",
            textfont=dict(size=14, color="#8B7CFF", family="Inter, sans-serif", weight=600),
            hovertemplate=(
                "<b>F1-Score</b><br>"
                "<span style='color:#94A3B8;'>Class:</span> %{x}<br>"
                "<span style='color:#94A3B8;'>Score:</span> %{y:.3f}"
                "<extra></extra>"
            ),
        )
    )

    # Reference threshold lines
    fig.add_hline(
        y=0.5,
        line_dash="dot",
        line_color="rgba(248,113,113,0.3)",
        line_width=1,
        annotation_text="Min 0.50",
        annotation_font=dict(size=12, color="rgba(248,113,113,0.6)", family="Inter"),
        annotation_position="bottom right",
    )
    fig.add_hline(
        y=0.8,
        line_dash="dot",
        line_color="rgba(34,197,94,0.3)",
        line_width=1,
        annotation_text="Good 0.80",
        annotation_font=dict(size=12, color="rgba(34,197,94,0.6)", family="Inter"),
        annotation_position="top right",
    )

    fig.update_layout(
        **BASE_LAYOUT,
        height=420,
        barmode="group",
        title=_title("Evaluation Metrics by Class (Test Set)"),
        xaxis=_xaxis(
            tickfont=dict(color="#F8FAFC", size=16),
            showgrid=False,
        ),
        yaxis=_yaxis(
            range=[0, 1.12],
        ),
        bargap=0.22,
    )
    return fig
