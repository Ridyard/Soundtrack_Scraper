import Soundtrack_Scraper_tv
import Soundtrack_Scraper_film
import Soundtrack_Builder

def build_playlist(tv_show, season_num):
    playlist_url = Soundtrack_Builder.run_soundtrack_builder(tv_show, season_num)
    return playlist_url

if __name__ == "__main__":
    tv_show = input('Please enter a TV Show to search... \n')
    season_num = input('Create playlist for which season? \n')

    try:
        playlist = Soundtrack_Scraper_tv.scrape_soundtrack_tv(tv_show, season_num) # returns a dict
        #output_file = Soundtrack_Scraper_tv.scrape_soundtrack_tv(tv_show, season_num) # returns a filepath
    except ValueError as e:
        print(e)
        exit()

    Soundtrack_Builder.run_soundtrack_builder(tv_show, season_num)

def build_playlist_film(film_name, film_year):
    playlist_url = Soundtrack_Builder.run_soundtrack_builder(film_name, film_year)
    return playlist_url

if __name__ == "__main__":
    film_name = input('Please enter a film to search... \n')
    film_year = input('Please enter the year of release... \n')

    try:
        playlist = Soundtrack_Scraper_film.scrape_soundtrack_film(film_name, film_year) # returns a dict
        #output_file = Soundtrack_Scraper_tv.scrape_soundtrack_tv(tv_show, season_num) # returns a filepath
    except ValueError as e:
        print(e)
        exit()

    Soundtrack_Builder.run_soundtrack_builder(tv_show, season_num)
