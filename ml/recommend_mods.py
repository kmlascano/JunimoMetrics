import duckdb
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


DB_PATH = "nexus_mods.duckdb"


def load_user_mod_matrix():
    con = duckdb.connect(DB_PATH)

    events = con.execute("""
        select
            user_id,
            mod_id,
            count(*) as interactions
        from read_csv_auto('data/raw/events.csv')
        where download_completed = true
        group by 1, 2
    """).df()

    matrix = events.pivot_table(
        index="mod_id",
        columns="user_id",
        values="interactions",
        fill_value=0
    )

    return matrix


def build_item_recommendations(matrix, top_n=10):
    similarity = cosine_similarity(matrix)
    similarity_df = pd.DataFrame(
        similarity,
        index=matrix.index,
        columns=matrix.index
    )

    rows = []

    for mod_id in similarity_df.index:
        similar_mods = (
            similarity_df[mod_id]
            .drop(index=mod_id)
            .sort_values(ascending=False)
            .head(top_n)
        )

        for recommended_mod_id, score in similar_mods.items():
            rows.append({
                "mod_id": mod_id,
                "recommended_mod_id": recommended_mod_id,
                "similarity_score": score
            })

    return pd.DataFrame(rows)


def write_recommendations(recommendations):
    con = duckdb.connect(DB_PATH)

    con.execute("drop table if exists ml_mod_recommendations")
    con.register("recommendations_df", recommendations)

    con.execute("""
        create table ml_mod_recommendations as
        select * from recommendations_df
    """)

    print("Wrote recommendations to ml_mod_recommendations")


if __name__ == "__main__":
    matrix = load_user_mod_matrix()
    recommendations = build_item_recommendations(matrix)
    write_recommendations(recommendations)