"""
ReviewSense - UI Chart Components
Plotly-based charts matching the Linear/Vercel dark SaaS design system
Configured for Projector Presentation Readability (15-18px information text)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
from ui_theme import SENTIMENT_COLORS, ASPECT_COLORS

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94A3B8", size=15),
    margin=dict(l=24, r=24, t=44, b=24),
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


def create_sentiment_donut(df: pd.DataFrame, sentiment_col: str = "sentiment") -> go.Figure:
    """Creates a sleek, modern donut chart showing sentiment distribution."""
    if df.empty or sentiment_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT)
        return fig

    counts = df[sentiment_col].str.lower().value_counts().reset_index()
    counts.columns = ["sentiment", "count"]
    total = counts["count"].sum()

    color_seq = [SENTIMENT_COLORS.get(s, "#8B7CFF") for s in counts["sentiment"]]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=counts["sentiment"].str.capitalize(),
                values=counts["count"],
                hole=0.68,
                marker=dict(
                    colors=color_seq,
                    line=dict(color="#151C2C", width=3)
                ),
                textinfo="percent",
                hoverinfo="label+value+percent",
                textfont=dict(size=16, color="#F8FAFC", family="Inter, sans-serif"),
                sort=False,
            )
        ]
    )

    fig.update_layout(
        **BASE_LAYOUT,
        annotations=[
            dict(
                text=f"<span style='font-size:28px; font-weight:700; color:#F8FAFC;'>{total:,}</span><br><span style='font-size:14px; color:#94A3B8; text-transform:uppercase; letter-spacing:0.06em;'>Reviews</span>",
                x=0.5,
                y=0.5,
                font=dict(family="Plus Jakarta Sans, sans-serif"),
                showarrow=False,
            )
        ],
        title=dict(
            text="Sentiment Distribution",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans"),
            x=0.02,
            y=0.98,
        ),
    )
    return fig


def create_aspect_bar(df: pd.DataFrame, aspects_col: str = "aspects") -> go.Figure:
    """Creates a horizontal bar chart displaying frequency of aspect mentions."""
    if df.empty or aspects_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT)
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

    # Order
    order = ["Quality", "Shipping", "Price"]
    counts = counts.set_index("aspect").reindex(order).fillna(0).reset_index()

    colors = [ASPECT_COLORS.get(a, "#8B7CFF") for a in counts["aspect"]]

    fig = go.Figure(
        data=[
            go.Bar(
                x=counts["count"],
                y=counts["aspect"],
                orientation="h",
                marker=dict(color=colors, line=dict(width=0)),
                text=counts["count"].apply(lambda v: f"{int(v):,}"),
                textposition="outside",
                textfont=dict(size=15, color="#F8FAFC", family="Inter, sans-serif"),
            )
        ]
    )

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text="Aspect Frequency",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans"),
            x=0.02,
            y=0.98,
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1E293B",
            zeroline=False,
            tickfont=dict(color="#94A3B8", size=15),
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color="#F8FAFC", size=16, family="Inter, sans-serif"),
        ),
    )
    return fig


def create_aspect_sentiment_grouped_bar(
    df: pd.DataFrame, sentiment_col: str = "sentiment", aspects_col: str = "aspects"
) -> go.Figure:
    """Grouped bar chart showing sentiment breakdown per aspect."""
    if df.empty or aspects_col not in df.columns or sentiment_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT)
        return fig

    data_copy = df.copy()
    data_copy["_aspect_list"] = data_copy[aspects_col].apply(
        lambda x: x if isinstance(x, list) else (str(x).split(", ") if str(x).strip() and str(x) != "None" else [])
    )
    exploded = data_copy.explode("_aspect_list").dropna(subset=["_aspect_list"])
    exploded = exploded[exploded["_aspect_list"].isin(["Quality", "Shipping", "Price"])]

    if exploded.empty:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT)
        return fig

    exploded[sentiment_col] = exploded[sentiment_col].str.lower()
    grouped = exploded.groupby(["_aspect_list", sentiment_col]).size().unstack(fill_value=0).reset_index()

    for col in ["positive", "neutral", "negative"]:
        if col not in grouped.columns:
            grouped[col] = 0

    fig = go.Figure()
    for s_label, col_name in [("Positive", "positive"), ("Neutral", "neutral"), ("Negative", "negative")]:
        fig.add_trace(
            go.Bar(
                name=s_label,
                x=grouped["_aspect_list"],
                y=grouped[col_name],
                marker=dict(color=SENTIMENT_COLORS[col_name], line=dict(width=0)),
                text=grouped[col_name].apply(lambda v: f"{int(v):,}" if v > 0 else ""),
                textposition="auto",
                textfont=dict(size=14, color="#0B0F19", family="Inter, sans-serif"),
            )
        )

    fig.update_layout(
        **BASE_LAYOUT,
        barmode="group",
        title=dict(
            text="Sentiment Breakdown Across Aspects",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans"),
            x=0.02,
            y=0.98,
        ),
        xaxis=dict(
            tickfont=dict(color="#F8FAFC", size=16, family="Inter, sans-serif"),
            gridcolor="#1E293B",
        ),
        yaxis=dict(
            gridcolor="#1E293B",
            zeroline=False,
            tickfont=dict(color="#94A3B8", size=15),
        ),
    )
    return fig


def create_time_trend_chart(df: pd.DataFrame, time_col: str = "Time", sentiment_col: str = "sentiment") -> go.Figure:
    """Monthly sentiment trend over time."""
    if df.empty or time_col not in df.columns or sentiment_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT)
        return fig

    trend_df = df.dropna(subset=[time_col, sentiment_col]).copy()
    trend_df["date"] = pd.to_datetime(trend_df[time_col], unit="s", errors="coerce")
    trend_df = trend_df.dropna(subset=["date"])

    if trend_df.empty:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT)
        return fig

    trend_df["month_year"] = trend_df["date"].dt.to_period("M").dt.to_timestamp()
    trend_df[sentiment_col] = trend_df[sentiment_col].str.lower()

    grouped = trend_df.groupby(["month_year", sentiment_col]).size().unstack(fill_value=0).reset_index()

    fig = go.Figure()
    for s_label, col_name in [("Positive", "positive"), ("Neutral", "neutral"), ("Negative", "negative")]:
        if col_name in grouped.columns:
            fig.add_trace(
                go.Scatter(
                    x=grouped["month_year"],
                    y=grouped[col_name],
                    mode="lines",
                    name=s_label,
                    line=dict(color=SENTIMENT_COLORS[col_name], width=3.0, shape="spline"),
                    fill="tozeroy" if col_name == "positive" else None,
                    fillcolor="rgba(34, 197, 94, 0.05)" if col_name == "positive" else None,
                )
            )

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text="Sentiment Volume Over Time",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans"),
            x=0.02,
            y=0.98,
        ),
        xaxis=dict(
            gridcolor="#1E293B",
            tickfont=dict(color="#94A3B8", size=15),
        ),
        yaxis=dict(
            gridcolor="#1E293B",
            zeroline=False,
            tickfont=dict(color="#94A3B8", size=15),
        ),
    )
    return fig


def create_rating_sentiment_matrix(df: pd.DataFrame, score_col: str = "Score", sentiment_col: str = "sentiment") -> go.Figure:
    """Shows distribution of predicted sentiment across star ratings (1 to 5)."""
    if df.empty or score_col not in df.columns or sentiment_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(**BASE_LAYOUT)
        return fig

    m_df = df.dropna(subset=[score_col, sentiment_col]).copy()
    m_df[sentiment_col] = m_df[sentiment_col].str.lower()
    grouped = m_df.groupby([score_col, sentiment_col]).size().unstack(fill_value=0).reset_index()

    fig = go.Figure()
    for s_label, col_name in [("Positive", "positive"), ("Neutral", "neutral"), ("Negative", "negative")]:
        if col_name in grouped.columns:
            fig.add_trace(
                go.Bar(
                    name=s_label,
                    x=[f"{int(s)} ⭐" for s in grouped[score_col]],
                    y=grouped[col_name],
                    marker=dict(color=SENTIMENT_COLORS[col_name]),
                )
            )

    fig.update_layout(
        **BASE_LAYOUT,
        barmode="stack",
        title=dict(
            text="Star Rating vs. Predicted Sentiment",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans"),
            x=0.02,
            y=0.98,
        ),
        xaxis=dict(
            tickfont=dict(color="#F8FAFC", size=16),
            gridcolor="#1E293B",
        ),
        yaxis=dict(
            gridcolor="#1E293B",
            zeroline=False,
            tickfont=dict(color="#94A3B8", size=15),
        ),
    )
    return fig


def create_confusion_matrix_heatmap(cm_df: pd.DataFrame) -> go.Figure:
    """Interactive heatmap for confusion matrix with exact values and percentages."""
    labels = ["Negative", "Neutral", "Positive"]
    z_values = cm_df.values

    # Annotations with counts and row percentages
    annotations = []
    for i, row in enumerate(z_values):
        row_sum = sum(row)
        for j, val in enumerate(row):
            pct = (val / row_sum * 100) if row_sum > 0 else 0
            annotations.append(
                dict(
                    x=labels[j],
                    y=labels[i],
                    text=f"<span style='font-size:22px; font-weight:700;'>{val:,}</span><br><span style='font-size:15px; opacity:0.85;'>{pct:.1f}%</span>",
                    font=dict(color="#F8FAFC", family="Plus Jakarta Sans"),
                    showarrow=False,
                )
            )

    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=labels,
            y=labels,
            colorscale=[
                [0.0, "#0F172A"],
                [0.2, "#1E293B"],
                [0.6, "#4F46E5"],
                [1.0, "#8B7CFF"],
            ],
            showscale=False,
        )
    )

    fig.update_layout(
        **BASE_LAYOUT,
        annotations=annotations,
        title=dict(
            text="Held-out Test Confusion Matrix",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans"),
            x=0.02,
            y=0.98,
        ),
        xaxis=dict(
            title=dict(text="Predicted Label", font=dict(size=15, color="#94A3B8")),
            tickfont=dict(color="#F8FAFC", size=16),
        ),
        yaxis=dict(
            title=dict(text="Actual True Label", font=dict(size=15, color="#94A3B8")),
            autorange="reversed",
            tickfont=dict(color="#F8FAFC", size=16),
        ),
    )
    return fig


def create_classification_metrics_bar() -> go.Figure:
    """Grouped bar chart for precision, recall, and F1 per class from test results."""
    classes = ["Negative", "Neutral", "Positive"]
    precision = [0.617, 0.266, 0.936]
    recall = [0.706, 0.401, 0.867]
    f1 = [0.659, 0.320, 0.900]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Precision", x=classes, y=precision, marker=dict(color="#38BDF8")))
    fig.add_trace(go.Bar(name="Recall", x=classes, y=recall, marker=dict(color="#818CF8")))
    fig.add_trace(go.Bar(name="F1-Score", x=classes, y=f1, marker=dict(color="#8B7CFF")))

    fig.update_layout(
        **BASE_LAYOUT,
        barmode="group",
        title=dict(
            text="Evaluation Metrics by Class (Test Set)",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans"),
            x=0.02,
            y=0.98,
        ),
        xaxis=dict(
            tickfont=dict(color="#F8FAFC", size=16),
            gridcolor="#1E293B",
        ),
        yaxis=dict(
            range=[0, 1.05],
            gridcolor="#1E293B",
            zeroline=False,
            tickfont=dict(color="#94A3B8", size=15),
        ),
    )
    return fig
