import requests
import json
import os

def fetch_mlbb_data():
    url = 'https://api.gms.moontontech.com/api/gms/source/2669606/2756567'
    
    # Using environment variable for security
    auth_token = os.environ.get('MLBB_AUTH_TOKEN')
    
    # Fallback to hardcoded token only if environment variable is missing
    # (Useful for local testing, but environment variable is preferred)
    if not auth_token:
        auth_token = 'UoXPlAENpsE7NAfeDxk4SvbyDTc='

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'x-actid': '2669607',
        'x-appid': '2669606',
        'x-lang': 'en',
        'Authorization': auth_token 
    }

    body = {
        "pageSize": 200, 
        "pageIndex": 1,
        "filters": [], 
        "sorts": [
            { "data": { "field": "main_hero_win_rate", "order": "desc" }, "type": "sequence" }
        ],
        "fields": ["main_hero", "main_hero_appearance_rate", "main_hero_win_rate", "main_heroid"]
    }

    try:
        print("Connecting to Moonton GMS API...")
        response = requests.post(url, headers=headers, json=body, timeout=20)
        
        if response.status_code != 200:
            print(f"Failed to connect. Status: {response.status_code}")
            return

        raw_json = response.json()
        # Data is located in 'data' -> 'records' based on successful terminal run
        records = raw_json.get('data', {}).get('records', [])
        
        if not records:
            print("WARNING: API returned success but 'data.records' is empty.")
            return

        print(f"Total raw records found: {len(records)}")

        processed_heroes = []
        for item in records:
            # Each record has a nested 'data' object containing hero stats
            hero_data = item.get('data', {})
            
            hero_id = hero_data.get('main_heroid')
            # Name is nested: hero_data -> main_hero -> data -> name
            hero_info = hero_data.get('main_hero', {}).get('data', {})
            name = hero_info.get('name')
            
            wr_raw = hero_data.get('main_hero_win_rate', 0)
            ar_raw = hero_data.get('main_hero_appearance_rate', 0)
            
            if hero_id and name:
                processed_heroes.append({
                    "name": name,
                    "winRate": float(wr_raw),
                    "useRate": float(ar_raw),
                    "heroId": hero_id,
                    "avatar": f"https://akmweb.youngjoygame.com/mlbb/hero/icon/{hero_id}.png"
                })

        # Ensure the public directory exists for the GitHub Action / Vercel
        os.makedirs('public', exist_ok=True)
        with open('public/data.json', 'w') as f:
            json.dump(processed_heroes, f, indent=2)
            
        print(f"Success! Processed {len(processed_heroes)} heroes into public/data.json")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    fetch_mlbb_data()