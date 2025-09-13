
# Script to build a Spotify Playlist from a given csv - see Soundtrack Scraper script
# example usage:
# create_spotify_playlist_from_csv(tv_show="Entourage", season_num="1")

# A Ridyard // 08.2025 // initial build
#                      // retreive Spotipy credentials via .env file
#                      // split script functionality into functions
#                      // add conditional block for native script testing
# 

#####################################################################################
###
### NOTE: If you’ve changed credentials or scopes recently, wipe the token cache:
### in terminal:
###         rm .cache
### make sure client_id & client_secret are correct & re-run
###
#####################################################################################

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from collections import OrderedDict
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv


def run_soundtrack_builder(tv_show, season_num, csv_dir="Playlist CSV Files", log_missing=True):
    """
    Build a Spotify playlist from a CSV and return the playlist URL.
    Works both when imported (web-app) and when run standalone (__main__).
    """
    sp = get_spotify_client()
    playlist_url = create_spotify_playlist_from_csv(sp, tv_show, season_num, csv_dir, log_missing)
    return playlist_url
    # create_spotify_playlist_from_csv(sp, tv_show, season_num, csv_dir, log_missing)



def get_spotify_client():
    # Get Spotify Credentials (avoids hard coding sensitive info)
    # this will look for the ".env" file in the project directory
    load_dotenv() # load env variables from .env
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    # Initialize Spotify client (credentials can be loaded from env/config later)
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="playlist-modify-public"
        ),
        requests_timeout=30
    )



def create_spotify_playlist_from_csv(sp, tv_show, season_num, csv_dir="Playlist CSV Files", log_missing=True):
    """
    Creates a Spotify playlist from a CSV of Song/Artist pairs.
    Deduplicates tracks, preserves order, and logs missing entries.
    """
    
    tv_show = '_'.join(word.capitalize() for word in tv_show.split())
    csv_path = f"{csv_dir}/{tv_show}_Season_{season_num}_Playlist.csv"
    
    # check that the playlist exists
    if not Path(csv_path).exists():
        print(f"❌ CSV not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    track_uris = []
    missing_tracks = []

    for _, row in df.iterrows():
        query = f"{row['Song']} {row['Artist']}"
        results = sp.search(q=query, type="track", limit=1)
        tracks = results.get('tracks', {}).get('items', [])
        if tracks:
            track_uris.append(tracks[0]['uri'])
        else:
            print(f"❌ Not found: {query}")
            missing_tracks.append(query)

    # Deduplicate while preserving order
    track_uris = list(OrderedDict.fromkeys(track_uris))

    # Log missing tracks
    if log_missing and missing_tracks:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        log_path = f"{csv_dir}/{tv_show}_Season_{season_num}_missing_tracks_log_{timestamp}.txt"
        with open(log_path, "w", encoding="utf-8") as f:
            for track in missing_tracks:
                f.write(track + "\n")
        print(f"📝 Missing tracks logged to: {log_path}")

    # Create playlist and add tracks
    tv_show_clean = tv_show.replace('_', ' ')

    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=f"{tv_show_clean} Season {season_num}", public=True)

    for i in range(0, len(track_uris), 100):
        sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris[i:i+100])

    playlist_url = playlist['external_urls']['spotify']
    print(f"✅ Playlist created: {playlist['external_urls']['spotify']}")
    print(playlist_url)

    return playlist_url


# tester code block
# when testing soundtrack_builder.py (ie calling functions from within this script, rather than importing from soundtrack_main.py)
# this code only runs when executed directly; it won't trigger when this file is imported elsewhere
# this call requires there to be a "tv_show_Season_1_Playlist.txt" file in the "Playlist CSV Files" sub-directory
if __name__ == "__main__":
    # tv_show = '_'.join(word.capitalize() for word in input("Enter a TV show to test script: ").split())
    tv_show = input("enter a tv show to test script: ")
    season_num = input("enter season num: ")
    sp = get_spotify_client()
    create_spotify_playlist_from_csv(sp, tv_show, season_num)


