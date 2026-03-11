import requests
import json
import os

def fetch_mlbb_data():
    url = 'https://api.gms.moontontech.com/api/gms/source/2669606/2756567'
    
    # Using environment variable for security
    auth_token = os.environ.get('MLBB_AUTH_TOKEN')
    
    # Fallback for local testing if env var is missing
    if not auth_token:
        auth_token = 'UoXPlAENpsE7NAfeDxk4SvbyDTc='

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'x-actid': '2669607',
        'x-appid': '2669606',
        'x-lang': 'en',
        'Authorization': auth_token 
    }

    # Updated body with the specific filters and fields from your working script
    body = {
        "pageSize": 131,
        "pageIndex": 1,
        "filters": [
            { "field": "bigrank", "operator": "eq", "value": "101" },
            { "field": "match_type", "operator": "eq", "value": 0 }
        ],
        "sorts": [
            { "data": { "field": "main_hero_win_rate", "order": "desc" }, "type": "sequence" },
            { "data": { "field": "main_heroid", "order": "desc" }, "type": "sequence" }
        ],
        "fields": [
            "main_hero",
            "main_hero_appearance_rate",
            "main_hero_ban_rate",
            "main_hero_channel",
            "main_hero_win_rate",
            "main_heroid",
            "data.sub_hero.hero",
            "data.sub_hero.hero_channel",
            "data.sub_hero.increase_win_rate",
            "data.sub_hero.heroid"
        ]
    }

    try:
        print("Connecting to Moonton GMS API (Mythic+ Filters)...")
        response = requests.post(url, headers=headers, json=body, timeout=20)
        
        if response.status_code != 200:
            print(f"Failed to connect. Status: {response.status_code}")
            return

        raw_json = response.json()
        records = raw_json.get('data', {}).get('records', [])
        
        if not records:
            print("WARNING: API returned success but 'data.records' is empty. Check filters.")
            return

        print(f"Total raw records found: {len(records)}")

        processed_heroes = []
        for item in records:
            hero_data = item.get('data', {})
            
            # Accessing main_hero data based on your successful script structure
            main_hero_obj = hero_data.get('main_hero', {}).get('data', {})
            hero_id = hero_data.get('main_heroid')
            name = main_hero_obj.get('name')
            head_url = main_hero_obj.get('head')
            
            # Get raw percentage values
            wr_raw = hero_data.get('main_hero_win_rate', 0)
            ar_raw = hero_data.get('main_hero_appearance_rate', 0)
            br_raw = hero_data.get('main_hero_ban_rate', 0)
            
            if hero_id and name:
                processed_heroes.append({
                    "name": name,
                    "winRate": float(wr_raw),
                    "useRate": float(ar_raw),
                    "banRate": float(br_raw),
                    "heroId": hero_id,
                    "avatar": head_url if head_url else f"https://akmweb.youngjoygame.com/mlbb/hero/icon/{hero_id}.png"
                })

        # Ensure directory exists
        os.makedirs('public', exist_ok=True)
        with open('public/data.json', 'w') as f:
            json.dump(processed_heroes, f, indent=2)
            
        print(f"Success! Processed {len(processed_heroes)} heroes into public/data.json")
        if processed_heroes:
            top = processed_heroes[0]
            print(f"Top Hero (Mythic+): {top['name']} - WR: {round(top['winRate']*100, 2)}%")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    fetch_mlbb_data()