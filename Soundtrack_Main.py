import Soundtrack_Scraper_tv
import Soundtrack_Builder

tv_show = input('Please enter a TV Show to search... \n')
season_num = input('Create playlist for which season? \n')

try:
    playlist = Soundtrack_Scraper_tv.scrape_soundtrack_tv(tv_show, season_num) # returns a dict
    #output_file = Soundtrack_Scraper_tv.scrape_soundtrack_tv(tv_show, season_num) # returns a filepath
except ValueError as e:
    print(e)
    exit()

Soundtrack_Builder.run_soundtrack_builder(tv_show, season_num)


