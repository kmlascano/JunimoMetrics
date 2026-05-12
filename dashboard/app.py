import duckdb
import streamlit as st
import plotly.express as px


con = duckdb.connect("../nexus_mods.duckdb")

st.set_page_config(page_title="Junimo Metrics", layout="wide")

st.title("Junimo Metrics Dashboard for Mods Analytics")
st.caption(
    "Synthetic modding analytics platform with dbt models, tested marts, "
    "lifecycle audiences, ML-powered mod classification, discovery scoring, "
    "and recommendations."
)


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

    col1.metric("Games", game_growth["game_id"].nunique())
    col2.metric("Download Starts", int(game_growth["download_starts"].sum()))

    completion_rate = (
        game_growth["completed_downloads"].sum()
        / game_growth["download_starts"].sum()
    )

    col3.metric("Completion Rate", f"{completion_rate:.1%}")

    st.subheader("Game Growth")
    st.dataframe(game_growth, use_container_width=True)

    fig = px.bar(
        game_growth,
        x="game_name",
        y="download_starts",
        color="completion_rate",
        title="Download Starts by Game"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Lifecycle Audiences")
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


st.subheader("ML Mod Classification")

try:
    ml_classification = load_ml_classification()

    ml_col1, ml_col2, ml_col3 = st.columns(3)

    ml_col1.metric(
        "Classified Mods",
        f"{ml_classification['mod_id'].nunique():,}"
    )

    ml_col2.metric(
        "Avg Confidence",
        f"{ml_classification['classification_confidence'].mean():.1%}"
    )

    low_confidence_count = (
        ml_classification["classification_confidence"] < 0.5
    ).sum()

    ml_col3.metric(
        "Needs Review",
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

    st.write("Low-confidence classifications for review")

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



st.subheader("Discovery Quality")

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


st.subheader("Discovery Quality Score")

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


st.subheader("Mod Recommendations")

try:
    recommendations = con.execute("""
        select *
        from ml_mod_recommendations
        order by similarity_score desc
        limit 100
    """).df()

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

st.subheader("Metric Catalogue")

try:
    metrics = load_metric_catalogue()
    st.dataframe(metrics, use_container_width=True)

except Exception as e:
    st.warning(
        "Metric catalogue is not available yet. "
        "Run your dbt models first."
    )