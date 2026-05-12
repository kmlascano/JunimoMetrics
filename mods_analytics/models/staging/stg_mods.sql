select
    mod_id,
    game_id,
    creator_id,
    category,
    cast(created_at as date) as created_at,
    moderation_status,
    dependency_count
from read_csv_auto('../data/raw/mods.csv')