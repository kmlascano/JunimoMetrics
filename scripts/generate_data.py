import pandas as pd
import random
from faker import Faker
from pathlib import Path
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)

OUT = Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)

# random values for data generation and analysis
n_users = 2000
n_games = 8
n_mods = 300
n_events = 10000

users = []
for i in range (1, n_users + 1):
    created_at = fake.date_between(start_date='-2y', end_date='-1d')
    users.append({
        "user_id": i,
        "created_at": created_at,
        "region": random.choice(["UK", "US", "EU", "CA", "AU"]),
        "is_premium": random.choice([True, False, False, False]),  # 25% premium
        "is_creator": random.choice([True, False, False]),  # 33% creators
        "lifecycle_status": random.choices(["new", "active", "inactive", "at_risk"])# could also assign weights for each value
    })
    
games = []
for i in range(1, n_games + 1):
    games.append({
        "game_id": i,
        "game_name": random.choice([
            "Skyrim", "Fallout 4", "Cyberpunk 2077", "Stardew Valley",
            "Baldur's Gate 3", "The Witcher 3", "RimWorld", "Mount & Blade"
        ]) + f" {i}",
        "genre": random.choice(["RPG", "Simulation", "Strategy", "Action"]),
        "activity_tier": random.choice(["low", "medium", "high"])
    })
    
    
mods = []
for i in range(1, n_mods + 1):
    game_id = random.randint(1, n_games)
    creator_id = random.randint(1, n_users)
    mods.append({
        "mod_id": i,
        "game_id": game_id,
        "creator_id": creator_id,
        "category": random.choice(["visual", "gameplay", "ui", "quests", "performance"]),
        "created_at": fake.date_between(start_date="-18m", end_date="-1d"),
        "moderation_status": random.choice(["approved", "approved", "approved", "pending", "rejected"]),
        "dependency_count": random.randint(0, 5)
    })
    

events = []
for i in range(1, n_events + 1):
    mod = random.choice(mods)
    started = fake.date_time_between(start_date="-90d", end_date="now")
    completed = random.random() > 0.12
    events.append({
        "event_id": i,
        "user_id": random.randint(1, n_users),
        "mod_id": mod["mod_id"],
        "game_id": mod["game_id"],
        "session_id": fake.uuid4(),
        "event_timestamp": started,
        "download_started": True,
        "download_completed": completed,
        "source_channel": random.choice(["search", "collection", "game_page", "recommendation"]),
        "error_code": None if completed else random.choice(["dependency_missing", "file_not_found", "network_error"])
    })
    

pd.DataFrame(users).to_csv(OUT / "users.csv", index=False)  
pd.DataFrame(games).to_csv(OUT / "games.csv", index=False)
pd.DataFrame(mods).to_csv(OUT / "mods.csv", index=False)
pd.DataFrame(events).to_csv(OUT / "events.csv", index=False)

print("Synthetic data generated and saved to 'data/raw' directory.") #optional