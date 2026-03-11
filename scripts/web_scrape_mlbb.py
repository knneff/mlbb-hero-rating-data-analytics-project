import requests
import json
import os

def fetch_mlbb_data():
    auth_token = os.environ.get('MLBB_AUTH_TOKEN')
    url = 'https://api.gms.moontontech.com/api/gms/source/2669606/2756567'
    
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'x-actid': '2669607',
        'x-appid': '2669606',
        'x-lang': 'en',
        'Authorization': auth_token 
    }

    body = {
        "pageSize": 131, 
        "pageIndex": 1,
        "filters": [
            { "field": "bigrank", "operator": "eq", "value": "101" },
            { "field": "match_type", "operator": "eq", "value": 0 }
        ],
        "sorts": [
            { "data": { "field": "main_hero_win_rate", "order": "desc" }, "type": "sequence" }
        ],
        "fields": [
            "main_hero",
            "main_hero_appearance_rate",
            "main_hero_win_rate",
            "main_heroid"
        ]
    }

    try:
        print("Connecting to Moonton GMS API...")
        response = requests.post(url, headers=headers, json=body, timeout=20)
        
        print(f"Response Status: {response.status_code}")
        
        response.raise_for_status()
        raw_data = response.json()

        hero_list = raw_data.get('data', {}).get('list', [])
        
        if not hero_list:
            print("WARNING: API returned success but 'data.list' is empty.")
            print("Full API Response for debugging:")
            print(json.dumps(raw_data, indent=2))
            
            print("Retrying with broader filters (removing bigrank)...")
            body["filters"] = [{ "field": "match_type", "operator": "eq", "value": 0 }]
            response = requests.post(url, headers=headers, json=body, timeout=20)
            hero_list = response.json().get('data', {}).get('list', [])

        processed_heroes = []
        for hero in hero_list:
            hero_id = hero.get('main_heroid')
            if hero_id:
                processed_heroes.append({
                    "name": hero.get('main_hero'),
                    "winRate": hero.get('main_hero_win_rate'),
                    "useRate": hero.get('main_hero_appearance_rate'),
                    "heroId": hero_id,
                    "avatar": f"https://akmweb.youngjoygame.com/mlbb/hero/icon/{hero_id}.png"
                })

        os.makedirs('public', exist_ok=True)
        
        with open('public/data.json', 'w') as f:
            json.dump(processed_heroes, f, indent=2)
            
        print(f"Success! Processed {len(processed_heroes)} heroes.")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        # Ensure we don't break the build
        if not os.path.exists('public/data.json'):
            with open('public/data.json', 'w') as f:
                json.dump([], f)

if __name__ == "__main__":
    fetch_mlbb_data()