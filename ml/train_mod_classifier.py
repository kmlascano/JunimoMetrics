
from pathlib import Path
import duckdb
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


DB_PATH = "nexus_mods.duckdb"
ARTIFACT_DIR = Path("ml/artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def load_training_data() -> pd.DataFrame:
    con = duckdb.connect(DB_PATH)

    df = con.execute("""
        select
            mod_id,
            coalesce(mod_name, '') as mod_name,
            coalesce(description, '') as description,
            coalesce(tags, '') as tags,
            coalesce(category, '') as category,
            dependency_count,
            moderation_status
        from read_csv_auto('data/raw/mods.csv')
        where category is not null
    """).df()

    df["text"] = (
        df["mod_name"].fillna("") + " " +
        df["description"].fillna("") + " " +
        df["tags"].fillna("") + " " +
        df["moderation_status"].fillna("")
    )

    return df


def train_classifier(df: pd.DataFrame):
    X = df["text"]
    y = df["category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=2
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ))
    ])

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(classification_report(y_test, preds))

    return model


if __name__ == "__main__":
    training_df = load_training_data()
    model = train_classifier(training_df)

    joblib.dump(model, ARTIFACT_DIR / "mod_classifier.joblib")
    print("Saved model to ml/artifacts/mod_classifier.joblib")