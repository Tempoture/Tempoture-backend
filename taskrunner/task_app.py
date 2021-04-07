import requests

def store():
    try:
        local = f"https://backendtempoture.herokuapp.com/store_tracks"
        resp = requests.get(local)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("ERR:" + str(err))
