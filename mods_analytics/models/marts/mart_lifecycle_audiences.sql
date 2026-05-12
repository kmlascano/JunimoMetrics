select
    u.user_id,
    u.region,
    u.is_premium,
    u.is_creator,
    u.lifecycle_status,
    count(d.event_id) as download_events_90d,
    sum(case when d.download_completed then 1 else 0 end) as completed_downloads_90d,
    case
        when u.is_creator and u.lifecycle_status = 'inactive' then 'inactive_creator'
        when u.is_premium and u.lifecycle_status = 'at_risk' then 'at_risk_premium_user'
        when count(d.event_id) >= 10 and not u.is_premium then 'high_intent_free_user'
        when u.lifecycle_status = 'new' then 'new_user_activation'
        else 'general_engagement'
    end as lifecycle_audience
from {{ ref('stg_users') }} u
left join {{ ref('stg_download_events') }} d
    on u.user_id = d.user_id
group by 1, 2, 3, 4, 5