#Terry 
import requests
import json
import os

def update_trackers(): #function that updates the trackers
    print("🛰️ Connecting to DuckDuckGo Tracker Radar...")
    # This is the official generated entity map from DDG's GitHub
    url = "https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/build-data/generated/entity_map.json"
    
    try:
        #grabs the url above, where the open source data of duckduckgo is 
        response = requests.get(url)
        #raise_for_status is it will return an error if the link is broken or the website is down, instead of processing empty data
        response.raise_for_status()
        #converts the data so Python can read 
        data = response.json()
        #puts that data in python dictionary 
        formatted_trackers = {}
        
        #loops through duckduckgo list
        for entity_name, details in data.items():
            #grabs the displayName and entity_name
            owner_display = details.get('displayName', entity_name)
            # loops through domains, each entity owns multiple properties (each companies owns many domains)
            for domain in details.get('properties', []):
                #makes the domain the key
                formatted_trackers[domain] = {
                    #assigns values to key, will transform the ddg data we receive in tracker.json. 10 is very common
                    "owner": owner_display,
                    #10 is very common, 7 is less common (looks for prevalence key, is tracker on more than 1% of web?)
                    "score": 10 if details.get('prevalence', 0) > 0.01 else 7
                }
        #opens the file tracker.json and dumps the new dictionary there)
        with open('trackers.json', 'w') as f:
            json.dump({"trackers": formatted_trackers}, f, indent=2)
        #status message confirming how many domains    
        print(f"✅ Success! Loaded {len(formatted_trackers)} tracker domains into trackers.json")
    #error handling 
    except Exception as e:
        print(f"❌ Failed to update: {e}")

if __name__ == "__main__":
    update_trackers()