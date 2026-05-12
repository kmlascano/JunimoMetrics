
from pathlib import Path
import duckdb
import joblib
import pandas as pd


DB_PATH = "nexus_mods.duckdb"
MODEL_PATH = Path("ml/artifacts/mod_classifier.joblib")


def load_mods() -> pd.DataFrame:
    con = duckdb.connect(DB_PATH)

    return con.execute("""
        select
            mod_id,
            coalesce(mod_name, '') as mod_name,
            coalesce(description, '') as description,
            coalesce(tags, '') as tags,
            coalesce(category, '') as existing_category,
            coalesce(moderation_status, '') as moderation_status,
            dependency_count
        from read_csv_auto('data/raw/mods.csv')
    """).df()

def score_mods(df: pd.DataFrame) -> pd.DataFrame:
    model = joblib.load(MODEL_PATH)

    df["text"] = (
        df["mod_name"].fillna("") + " " +
        df["description"].fillna("") + " " +
        df["tags"].fillna("") + " " +
        df["moderation_status"].fillna("")
    )

    df["predicted_category"] = model.predict(df["text"])

    if hasattr(model.named_steps["clf"], "predict_proba"):
        probabilities = model.predict_proba(df["text"])
        df["classification_confidence"] = probabilities.max(axis=1)
    else:
        df["classification_confidence"] = None

    return df[[
        "mod_id",
        "existing_category",
        "predicted_category",
        "classification_confidence",
        "dependency_count"
    ]]


def write_predictions(predictions: pd.DataFrame):
    con = duckdb.connect(DB_PATH)

    con.execute("drop table if exists ml_mod_classification")
    con.register("predictions_df", predictions)

    con.execute("""
        create table ml_mod_classification as
        select * from predictions_df
    """)

    print("Wrote predictions to ml_mod_classification")


if __name__ == "__main__":
    mods = load_mods()
    predictions = score_mods(mods)
    write_predictions(predictions)