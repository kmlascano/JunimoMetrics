import duckdb
import streamlit as st
import plotly.express as px


con = duckdb.connect("../nexus_mods.duckdb")

st.set_page_config(
    page_title="Junimo Metrics",
    page_icon="🌱",
    layout="wide"
)




st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

/* Hide Streamlit top toolbar / Deploy button */
[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}

/* Hide Streamlit header */
[data-testid="stHeader"] {
    visibility: hidden;
    height: 0%;
}

/* Hide default Streamlit menu */
#MainMenu {
    visibility: hidden;
}

/* Hide footer */
footer {
    visibility: hidden;
}

/* Main app background */
.stApp {
    background: linear-gradient(180deg, #fff7dc 0%, #f7e7b8 45%, #d8f0c2 100%);
    font-family: 'Nunito', sans-serif;
}

/* Main content width and spacing */
.block-container {
    padding-top: 1rem;
    padding-bottom: 4rem;
}

/* Main title */
h1 {
    color: #5c4033;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-shadow: 2px 2px 0px #f6d98b;
}

/* Section headers */
h2, h3 {
    color: #6b4226;
    font-weight: 800;
}

/* Normal text */
p, div, span {
    font-family: 'Nunito', sans-serif;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #fff8df;
    border: 3px solid #d69b52;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 4px 4px 0px #a86f3d;
}

/* Metric label */
[data-testid="stMetricLabel"] {
    color: #6b4226;
    font-weight: 800;
}

/* Metric value */
[data-testid="stMetricValue"] {
    color: #3f6f3f;
    font-weight: 800;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    background: #fff8df;
    border: 3px solid #d69b52;
    border-radius: 16px;
    padding: 8px;
    box-shadow: 4px 4px 0px #a86f3d;
}

/* Plot containers */
[data-testid="stPlotlyChart"] {
    background: #fff8df;
    border: 3px solid #d69b52;
    border-radius: 16px;
    padding: 12px;
    box-shadow: 4px 4px 0px #a86f3d;
    margin-bottom: 2rem;
}

/* Warning boxes */
[data-testid="stAlert"] {
    border-radius: 14px;
    border: 2px solid #d69b52;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #e7c985;
}

/* Tables text */
table {
    color: #3e3028;
}

/* Cute buttons if filters are added later */
.stButton > button {
    background-color: #8fbc5a;
    color: white;
    border: 3px solid #5c7f35;
    border-radius: 14px;
    font-weight: 800;
    box-shadow: 3px 3px 0px #4f6f2c;
}

.stButton > button:hover {
    background-color: #78a84b;
    color: white;
    border-color: #4f6f2c;
}

/* Custom cute divider */
.cozy-divider {
    border-top: 4px dashed #d69b52;
    margin: 2.3rem 0;
}

/* Small section label */
.cozy-label {
    color: #7a5c44;
    font-weight: 700;
    font-size: 0.95rem;
}

/* Hero card */
.hero-card {
    background: #fff8df;
    border: 4px solid #d69b52;
    border-radius: 24px;
    padding: 24px 28px;
    box-shadow: 6px 6px 0px #a86f3d;
    margin-bottom: 28px;
}

/* Little intro cards */
.info-card {
    background: #fff8df;
    border: 3px solid #d69b52;
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 4px 4px 0px #a86f3d;
    color: #6b4226;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


def cozy_divider():
    st.markdown('<div class="cozy-divider"></div>', unsafe_allow_html=True)




st.markdown("""
<div class="hero-card">
    <h1 style="margin-bottom: 0.3rem;">🌱 Junimo Metrics</h1>
    <p style="
        font-size: 1.1rem;
        color: #6b4226;
        margin-bottom: 0;
    ">
        A cozy analytics dashboard for mods, discovery,
        classification, and recommendations.
    </p>
</div>
""", unsafe_allow_html=True)



@st.cache_data
def load_game_growth():
    return con.execute("""
        select *
        from mart_game_growth
        order by download_starts desc
    """).df()


@st.cache_data
def load_lifecycle_audiences():
    return con.execute("""
        select
            lifecycle_audience,
            count(*) as users
        from mart_lifecycle_audiences
        group by 1
        order by users desc
    """).df()


@st.cache_data
def load_metric_catalogue():
    return con.execute("""
        select *
        from metric_catalogue
    """).df()


@st.cache_data
def load_ml_classification():
    return con.execute("""
        select *
        from ml_mod_classification
    """).df()




try:
    game_growth = load_game_growth()
    audiences = load_lifecycle_audiences()

    col1, col2, col3 = st.columns(3)

    col1.metric("🎮 Games", game_growth["game_id"].nunique())
    col2.metric("📦 Download Starts", int(game_growth["download_starts"].sum()))

    completion_rate = (
        game_growth["completed_downloads"].sum()
        / game_growth["download_starts"].sum()
    )

    col3.metric("✅ Completion Rate", f"{completion_rate:.1%}")

    cozy_divider()

    st.markdown("## 🌾 Game Growth")
    st.dataframe(game_growth, use_container_width=True)

    fig = px.bar(
        game_growth,
        x="game_name",
        y="download_starts",
        color="completion_rate",
        title="Download Starts by Game"
    )
    st.plotly_chart(fig, use_container_width=True)

    cozy_divider()

    st.markdown("## 🧺 Lifecycle Audiences")
    st.dataframe(audiences, use_container_width=True)

    fig2 = px.bar(
        audiences,
        x="lifecycle_audience",
        y="users",
        title="Lifecycle Audience Sizes"
    )
    st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.warning(
        "Core analytics tables are not available yet. "
        "Run your dbt models first."
    )
    st.exception(e)


cozy_divider()


st.markdown("## 🧠 Mod Classification")

try:
    ml_classification = load_ml_classification()

    st.markdown("""
    <div class="info-card">
        This section uses a trained text classification model to assign mods into
        structured categories using names, descriptions, tags, and metadata.
    </div>
    """, unsafe_allow_html=True)

    ml_col1, ml_col2, ml_col3 = st.columns(3)

    ml_col1.metric(
        "🌱 Classified Mods",
        f"{ml_classification['mod_id'].nunique():,}"
    )

    ml_col2.metric(
        "✨ Avg Confidence",
        f"{ml_classification['classification_confidence'].mean():.1%}"
    )

    low_confidence_count = (
        ml_classification["classification_confidence"] < 0.5
    ).sum()

    ml_col3.metric(
        "🧺 Needs Review",
        f"{low_confidence_count:,}"
    )

    category_counts = (
        ml_classification
        .groupby("predicted_category", as_index=False)
        .agg(mods=("mod_id", "count"))
        .sort_values("mods", ascending=False)
    )

    fig3 = px.bar(
        category_counts,
        x="predicted_category",
        y="mods",
        title="Predicted Mod Categories"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### 🧺 Low-confidence classifications for review")

    review_queue = (
        ml_classification
        .sort_values("classification_confidence", ascending=True)
        .head(25)
    )

    st.dataframe(review_queue, use_container_width=True)

except Exception as e:
    st.warning(
        "ML classification table not found yet. "
        "Run `python ml/train_mod_classifier.py` and `python ml/score_mods.py` first."
    )


cozy_divider()


st.markdown("## 🔍 Discovery Quality")

try:
    discovery = con.execute("""
        select
            predicted_category,
            avg(classification_confidence) as avg_confidence,
            avg(dependency_count) as avg_dependencies,
            count(*) as mods
        from ml_mod_classification
        group by 1
        order by mods desc
    """).df()

    st.dataframe(discovery, use_container_width=True)

    fig5 = px.scatter(
        discovery,
        x="avg_dependencies",
        y="avg_confidence",
        size="mods",
        color="predicted_category",
        title="Discovery Quality by Predicted Category"
    )

    st.plotly_chart(fig5, use_container_width=True)

except Exception as e:
    st.warning(
        "Discovery quality is not available yet. "
        "Run `python ml/score_mods.py` first."
    )


cozy_divider()


st.markdown("## ⭐ Discovery Quality Score")

try:
    discovery_scores = con.execute("""
        select
            mod_id,
            predicted_category,
            classification_confidence,
            dependency_count,
            case
                when classification_confidence >= 0.8 then 3
                when classification_confidence >= 0.5 then 2
                else 1
            end
            + dependency_count * 0.2 as discovery_score
        from ml_mod_classification
        order by discovery_score desc
    """).df()

    st.dataframe(discovery_scores, use_container_width=True)

    fig_discovery = px.scatter(
        discovery_scores,
        x="classification_confidence",
        y="discovery_score",
        color="predicted_category",
        size="dependency_count",
        title="Discovery Score by Classification Confidence"
    )

    st.plotly_chart(fig_discovery, use_container_width=True)

except Exception as e:
    st.warning(
        "Discovery scores are not available yet. "
        "Run `python ml/score_mods.py` first."
    )


cozy_divider()


st.markdown("## 🍄 Mod Recommendations")

try:
    recommendations = con.execute("""
        select *
        from ml_mod_recommendations
        order by similarity_score desc
        limit 100
    """).df()

    st.markdown("""
    <div class="info-card">
        These recommendations are based on completed download behaviour.
        Mods with similar user interaction patterns are grouped together.
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(recommendations, use_container_width=True)

    fig4 = px.histogram(
        recommendations,
        x="similarity_score",
        title="Recommendation Similarity Score Distribution"
    )

    st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.warning(
        "Recommendation table not found yet. "
        "Run `python ml/recommend_mods.py` first."
    )


cozy_divider()

st.markdown("## 📚 Metric Catalogue")

try:
    metrics = load_metric_catalogue()
    st.dataframe(metrics, use_container_width=True)

except Exception as e:
    st.warning(
        "Metric catalogue is not available yet. "
        "Run your dbt models first."
    )