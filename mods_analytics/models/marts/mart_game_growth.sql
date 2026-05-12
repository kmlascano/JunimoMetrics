select
    g.game_id,
    g.game_name,
    g.genre,
    g.activity_tier,
    count(distinct d.user_id) as active_downloaders,
    count(distinct d.mod_id) as downloaded_mods,
    count(*) as download_starts,
    sum(case when d.download_completed then 1 else 0 end) as completed_downloads,
    round(
        sum(case when d.download_completed then 1 else 0 end)::double / count(*),
        4
    ) as completion_rate
from {{ ref('stg_download_events') }} d
left join {{ ref('stg_games') }} g
    on d.game_id = g.game_id
group by 1, 2, 3, 4