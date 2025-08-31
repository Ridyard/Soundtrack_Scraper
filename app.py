
# script to launch the soundtrack scraper web-app

from flask import Flask, render_template, request, redirect, url_for
from Soundtrack_Scraper_tv import scrape_soundtrack_tv
from Soundtrack_Builder import run_soundtrack_builder

app = Flask(__name__)
playlist_cache = {}  # temporary in-memory store

@app.route("/", methods=["GET", "POST"])
def index():
    success = request.args.get("success")
    track_count = request.args.get("tracks", default=0, type=int)
    if request.method == "POST":
        tv_show = request.form["tv_show"]
        season_num = int(request.form["season_num"])
        playlist = scrape_soundtrack_tv(tv_show, season_num)
        playlist_cache["data"] = playlist
        playlist_cache["tv_show"] = tv_show
        playlist_cache["season_num"] = season_num
        return render_template("preview.html", playlist=playlist, tv_show=tv_show, season_num=season_num)
    # return render_template("index.html", success=success)
    return render_template("index.html", success=success, track_count=track_count)




@app.route("/confirm", methods=["POST"])
def confirm():
    tv_show = playlist_cache.get("tv_show")
    season_num = playlist_cache.get("season_num")
    run_soundtrack_builder(tv_show, season_num)
    # return redirect(url_for("index", success="true"))
    return redirect(url_for("index", success="true", tracks=len(playlist_cache["data"])))


if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True)
