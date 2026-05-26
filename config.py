import json
import os

def load_beomat_configuration():
    # Load default satellites
    with open('satellites_default.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    all_satellites = config.get('satellites', [])
    
    # Load User satellites, if any
    user_file = 'user_setup.json'
    if os.path.exists(user_file):
        with open(user_file, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
        
        # Combine all information
        existing_ids = {sat['norad_id'] for sat in all_satellites}
        for user_sat in user_config.get('satellites', []):
            if user_sat['norad_id'] not in existing_ids:
                all_satellites.append(user_sat)
                
    return all_satellites