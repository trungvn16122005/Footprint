#Terry 
import requests
import json
import os

def update_trackers():
    print("🛰️ Connecting to DuckDuckGo Tracker Radar...")
    # This is the official generated entity map from DDG's GitHub
    url = "https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/build-data/generated/entity_map.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        #flip the data to look up by domain
        formatted_trackers = {}
        
        for entity_name, details in data.items():
            owner_display = details.get('displayName', entity_name)
            # Each entity owns multiple properties (domains)
            for domain in details.get('properties', []):
                formatted_trackers[domain] = {
                    "owner": owner_display,
                    "score": 10 if details.get('prevalence', 0) > 0.01 else 7
                }
        
        with open('trackers.json', 'w') as f:
            json.dump({"trackers": formatted_trackers}, f, indent=2)
            
        print(f"✅ Success! Loaded {len(formatted_trackers)} tracker domains into trackers.json")

    except Exception as e:
        print(f"❌ Failed to update: {e}")

if __name__ == "__main__":
    update_trackers()