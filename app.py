
# script to launch the soundtrack scraper web-app

from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests, os
from dotenv import load_dotenv
from Soundtrack_Scraper_tv import scrape_soundtrack_tv
from Soundtrack_Builder import run_soundtrack_builder
from Soundtrack_Main import build_playlist

app = Flask(__name__)
playlist_cache = {}  # temporary in-memory store

load_dotenv()  # Loads from .env file

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# used when the user selects "tv show"
@app.route("/", methods=["GET", "POST"])
def tv_builder(): #previously index()
    success = request.args.get("success")
    track_count = request.args.get("tracks", default=0, type=int)
    playlist_url = request.args.get("playlist_url")

    if request.method == "POST":
        tv_show = request.form["tv_show"]
        season_num = int(request.form["season_num"])
        playlist = scrape_soundtrack_tv(tv_show, season_num)
        playlist_cache["data"] = playlist
        playlist_cache["tv_show"] = tv_show
        playlist_cache["season_num"] = season_num
        #print('scraped playlist: ',playlist)
        return render_template("preview.html", playlist=playlist, tv_show=tv_show, season_num=season_num)
    return render_template("index.html", success=success, track_count=track_count, playlist_url=playlist_url)


@app.route("/current-episode")
def current_episode():
    try:
        with open("current_episode.txt", "r", encoding="utf-8") as f:
            title = f.read().strip()
        return {"episode": title}
    except FileNotFoundError:
        return {"episode": "Loading..."}
    

@app.route("/confirm", methods=["POST"])
def confirm():
    tv_show = playlist_cache.get("tv_show")
    season_num = playlist_cache.get("season_num")
    playlist_url = build_playlist(tv_show, season_num)
    # run_soundtrack_builder(tv_show, season_num)
    return redirect(url_for("tv_builder", success="true", tracks=len(playlist_cache["data"]), playlist_url=playlist_url))



# @app.route("/search")
# def autocomplete_search():
#     query = request.args.get("q")
#     media_type = request.args.get("type", "tv")

#     endpoint = "tv" if media_type == "tv" else "movie"
#     url = f"https://api.themoviedb.org/3/search/{endpoint}"

#     params = {
#         "api_key": TMDB_API_KEY,
#         "query": query,
#         "language": "en-US",
#         "include_adult": False
#     }

#     response = requests.get(url, params=params)
#     return jsonify(response.json())
@app.route("/search")
def autocomplete_search():
    query = request.args.get("q")
    media_type = request.args.get("type", "tv")

    endpoint = "tv" if media_type == "tv" else "movie"
    url = f"https://api.themoviedb.org/3/search/{endpoint}"

    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "en-US",
        "include_adult": False
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()  # raises HTTPError for 4xx/5xx
        data = response.json()
    except requests.RequestException as e:
        app.logger.error(f"TMDB API request failed: {e}")
        return jsonify([])  # return empty list on error
    except ValueError as e:
        app.logger.error(f"TMDB JSON decode failed: {e}")
        return jsonify([])

    results = data.get("results", [])[:3]  # limit to 3 results

    for r in results:
        # Add year field for display
        if media_type == "tv":
            r["year"] = r.get("first_air_date", "")[:4] if r.get("first_air_date") else ""
        else:
            r["year"] = r.get("release_date", "")[:4] if r.get("release_date") else ""

        # Only add poster_url if TMDB returned one
        if r.get("poster_path"):
            r["poster_url"] = f"https://image.tmdb.org/t/p/w500{r['poster_path']}"
        
    return jsonify({"results": results})


@app.route("/film", methods=["GET", "POST"])
def film_search():
    if request.method == "POST":
        media_type = request.form.get("media_type")
        query = request.form.get("tv_show")
        season_num = request.form.get("season_num")  # May be None for films

        endpoint = "tv" if media_type == "tv" else "movie"
        url = f"https://api.themoviedb.org/3/search/{endpoint}"

        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
            "language": "en-US",
            "include_adult": False
        }

        response = requests.get(url, params=params)
        raw_results = response.json().get("results", [])

        playlist = []
        for item in raw_results:
            title = item.get("title") or item.get("name")
            year = item.get("release_date", "")[:4] if media_type == "movie" else ""
            playlist.append({"title": title, "year": year})

        return render_template(
            "film_preview.html",
            playlist=playlist,
            tv_show=query, 
            season_num=None)

    return render_template("index.html")




#####################################################

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True)