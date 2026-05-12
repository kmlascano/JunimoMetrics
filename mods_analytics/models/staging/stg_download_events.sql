select
    event_id,
    user_id,
    mod_id,
    game_id,
    session_id,
    cast(event_timestamp as timestamp) as event_timestamp,
    download_started,
    download_completed,
    source_channel,
    error_code
from read_csv_auto('../data/raw/events.csv')