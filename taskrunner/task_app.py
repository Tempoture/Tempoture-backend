import requests

def store():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        local = f"http://localhost:5000/store_tracks"
        resp = requests.get(local)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("ERR:" + str(err))
