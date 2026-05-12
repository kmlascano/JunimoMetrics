select
    m.mod_id,
    m.game_id,
    m.creator_id,
    m.category as original_category,
    ml.predicted_category,
    ml.classification_confidence,
    m.dependency_count,
    m.moderation_status,
    case
        when ml.classification_confidence >= 0.80 then 'high_confidence'
        when ml.classification_confidence >= 0.50 then 'medium_confidence'
        else 'needs_review'
    end as classification_quality_band,
    case
        when m.category = ml.predicted_category then true
        else false
    end as category_matches_prediction
from {{ ref('stg_mods') }} m
left join ml_mod_classification ml
    on m.mod_id = ml.mod_id