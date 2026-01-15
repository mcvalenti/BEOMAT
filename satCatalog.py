import requests


def request_CelesTrack(group_name):

    # REQUEST for a complete group JSON
    """
    Docstring for request_CelesTrack
    json keys for every satellite - 
    ['OBJECT_NAME', 'OBJECT_ID', 'EPOCH', 'MEAN_MOTION', 'ECCENTRICITY',
       'INCLINATION', 'RA_OF_ASC_NODE', 'ARG_OF_PERICENTER', 'MEAN_ANOMALY',
       'EPHEMERIS_TYPE', 'CLASSIFICATION_TYPE', 'NORAD_CAT_ID',
       'ELEMENT_SET_NO', 'REV_AT_EPOCH', 'BSTAR', 'MEAN_MOTION_DOT',
       'MEAN_MOTION_DDOT']
    
    :param group_name: Description
    """
    url = f"https://celestrak.org/NORAD/elements/gp.php?GROUP={group_name}&FORMAT=JSON"

    response = requests.get(url)

    if response.status_code == 200:
        constellation = response.json()
    
    return constellation

def request_by_name(name_text="NUSAT"):
    url = "https://celestrak.org/NORAD/elements/gp.php"
    params = {
        "NAME": name_text,
        "FORMAT": "JSON"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200 and response.text.strip().startswith('['):
        return response.json()
    else:
        print("Not found")
        return []
    

def request_celestrak_data(search_value="STARLINK", search_type="GROUP"):
    """
    Fetches satellite data from CelesTrak.
    
    Args:
        search_value (str): The value to search for (e.g., 'STARLINK', 'NUSAT').
        search_type (str): 'GROUP' for official categories or 'NAME' for free-text search.
        
    Returns:
        list: A list of dictionaries containing Name, TLE lines, and NORAD ID.

    Example:
         1. Search by GROUP (Official CelesTrak categories)
         starlink_list = request_celestrak_data("STARLINK", "GROUP")

        2. Search by NAME (Free-text search for specific names)
        nusat_list = request_celestrak_data("NUSAT", "NAME")
    """
    
    base_url = "https://celestrak.org/NORAD/elements/gp.php"
    
    # We set the parameters dynamically based on search_type
    # FORMAT=TLE is required to get the raw TLE lines
    params = {
        search_type.upper(): search_value,
        "FORMAT": "TLE"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        # Split the text into lines and remove empty ones
        lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
        
        constellation_data = []
        
        # TLE format is 3 lines per satellite: 0:Name, 1:Line1, 2:Line2
        for i in range(0, len(lines), 3):
            if i + 2 < len(lines):
                satellite_record = {
                    "OBJECT_NAME": lines[i],
                    "TLE_LINE1": lines[i+1],
                    "TLE_LINE2": lines[i+2],
                    "NORAD_CAT_ID": lines[i+1][2:7].strip()
                }
                constellation_data.append(satellite_record)
        
        return constellation_data

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return []

    # --- HOW TO USE IT ---

