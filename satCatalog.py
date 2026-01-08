import requests


def request_CelesTrack(group_name):

    # REQUEST for a complete group en formato JSON
    url = f"https://celestrak.org/NORAD/elements/gp.php?GROUP={group_name}&FORMAT=JSON"

    response = requests.get(url)

    if response.status_code == 200:
        constelacion = response.json()
    
    return constelacion

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

