import csv
import json
import random
from datetime import datetime, timedelta

def schedule(club_id, league_code, save_num):
    opponents = []
    with open("data/assets/clubs.csv", mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['league_code'] == league_code and row['club_id'] != club_id:
                opponents.append(row['club_id'])

    schedule = []
    start_date = datetime.strptime("2024-09-17", "%Y-%m-%d")

    match_count = len(opponents) * 2
    match_dates = [start_date + timedelta(days=i * 7) for i in range(match_count)]

    for i, opponent in enumerate(opponents):
        schedule.append({
            "home": club_id,
            "away": opponent,
            "home_score": "",
            "away_score": "",
            "date": match_dates[i].strftime('%Y-%m-%d')
        })
        schedule.append({
            "home": opponent,
            "away": club_id,
            "home_score": "",
            "away_score": "",
            "date": match_dates[len(opponents) + i].strftime('%Y-%m-%d')
        })

    dates = [match["date"] for match in schedule]
    random.shuffle(schedule)
    for i, match in enumerate(schedule):
        match["date"] = dates[i]

    schedule.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))

    output_file = f"save{save_num}_schedule.json"
    with open(f"data/assets/{output_file}", 'w') as f_out:
        json.dump(schedule, f_out, indent=4)