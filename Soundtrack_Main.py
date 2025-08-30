import Soundtrack_Scraper_tv
import Soundtrack_Builder

tv_show = input('Please enter a TV Show to search... \n')
season_num = input('Scrape the soundtrack for which season? \n')

try:
    playlist = Soundtrack_Scraper_tv.scrape_soundtrack_tv(tv_show, season_num) # returns a dict
except ValueError as e:
    print(e)
    exit()

tv_show = '_'.join(word.capitalize() for word in tv_show.split()) # cleanse tv_show to match the csv returned from soundtrack_scraper

Soundtrack_Builder.run_soundtrack_builder(tv_show, season_num)


