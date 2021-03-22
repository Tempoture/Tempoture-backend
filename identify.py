import requests
import xml.etree.ElementTree as ET 
import os
from dotenv import load_dotenv


fmUrl = "http://ws.audioscrobbler.com/2.0/?" #lastfm url
mbUrl = "https://musicbrainz.org/ws/2/" #musicbrainz url (currently unused)

load_dotenv()
key = os.environ.get('LASTFMKEY')


def getTags(track, artist, numTags=1):
    querystring = {"api_key":key,"method":"track.getInfo","artist":artist,"track":track}
    headers = {}
    response = requests.request("GET", fmUrl, headers=headers, params=querystring)
    #print(response.text)
    root = ET.fromstring(response.text)
    tags = []
    i = 0
    for item in root.findall('./track/toptags/tag/name'):
        if not item.text in tags: 
            tags.append(item.text)
            i = i + 1
            if i >= numTags:
                break

    #If we have enough from the track, return now
    if (len(tags) == numTags):
        return tags

    #Otherwise check the album tags
    if root.find('./track/album/title') != None:
        album = root.find('./track/album/title').text
        querystring = {"api_key":key,"method":"album.getInfo","artist":artist,"album":album}
        response = requests.request("GET", fmUrl, headers=headers, params=querystring)
        root = ET.fromstring(response.text)
        for item in root.findall('./album/toptags/tag/name'): 
            if not item.text in tags:
                tags.append(item.text)
                i = i + 1
                if i >= numTags:
                    break
    
    #If we have enough from the album, return now
    if (len(tags) == numTags):
        return tags

    #Otherwise check the artist tags
    querystring = {"api_key":key,"method":"artist.getTopTags","artist":artist}
    response = requests.request("GET", fmUrl, headers=headers, params=querystring)
    root = ET.fromstring(response.text)
    #print(response.text)
    for item in root.findall('./toptags/tag/name'):
        if not item.text in tags: 
            tags.append(item.text)
            i = i + 1
            if i >= numTags:
                break

    #Return
    return tags


print(getTags("色の無い水槽","tricot", 5)) 