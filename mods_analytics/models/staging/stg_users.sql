select
    user_id,
    cast(created_at as date) as created_at,
    region,
    is_premium,
    is_creator,
    case
        when lower(trim(lifecycle_status)) in ('new', 'active', 'inactive', 'at_risk')
            then lower(trim(lifecycle_status))
        else 'inactive'
    end as lifecycle_status
from read_csv_auto('../data/raw/users.csv')