
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from pathlib import Path
import os
import Soundtrack_Scraper_utils

def scrape_soundtrack_film(film_name, film_year=""):
    
    playlist = {}  # dict to hold each artist:song kv pair
    selectors = { # dict to hold the xpath strings 
        "cookies_agree_button": '//button[span[text()="AGREE"]]',
        "login_modal": '//div[contains(@class, "modal")]//h1[contains(text(), "Log in")]',
        "show_all_button": './/button[.//p[text()="Show all tracks"]]',
        "parent_container": '//div[contains(@class, "scroll-mt-20")]', # holds various track_containers
        "track_container": './/div[contains(@class, "flex flex-col")]', # song/artist container (within parent_container)
        "song": './/p[contains(@class, "font-bold") and contains(@class, "text-[1rem]")]',
        "artist": './/a[@data-discover="true" and contains(@href, "/artist/")]/small'
    }
    
    # Headless Firefox configuration
    options = Options()
    options.headless = False  # Enable headless mode / True = don't show browser   
    
    baseURL = "https://www.tunefind.com/movie/"
    film_name = film_name.split()
    film_name_clean = '-'.join(film_name)
    # some films omit the release year in the url (example: the hangover)
    if film_year != "":
        builtURL = baseURL + film_name_clean + '-' + film_year
    else:
        builtURL = baseURL + film_name_clean
    
    # set browser object & open url
    browser = webdriver.Firefox(options = options) # Use options when initializing the WebDriver
    browser.get(builtURL)
    Soundtrack_Scraper_utils.handle_cookies(browser, selectors)
    
    soundtrack_container = selectors["parent_container"]
    # Locate the parent div element
    parent_div = browser.find_element(By.XPATH, soundtrack_container)

    # the "show all tracks" button is located within the parent_div, hence why we pass the parent_div as an argument
    # this function call is inconsistent when we don't use the parent_div, ie we just search for the "show all tracks" button xpath
    Soundtrack_Scraper_utils.click_show_all(browser, selectors,parent_div) # Click "Show All" if present

    track_containers = parent_div.find_elements(By.XPATH, selectors["track_container"])
    for track in track_containers:
        try:
            # Extract song title
            song = track.find_element(By.XPATH, selectors["song"]).text.strip()

            # Extract all artist names within this track container
            artist_links = track.find_elements(By.XPATH, selectors["artist"])
            artists = ', '.join(artist.text.replace('\n', '').strip().rstrip(',') for artist in artist_links if artist.text.strip()) # handles multiple contributing artists (ie as one collection)

            playlist[song] = artists
        except Exception as e:
            print(f"Issue extracting track info: {e}")

    for k,v in playlist.items():
        print(f'{k}: {v}')
    print(f'playlist length: {len(playlist)}')

    # placeholder filename
    words = film_name_clean.split("-")
    output_filename = '_'.join(word.capitalize() for word in words)
    if film_year != "":
        output_filename += f"_{film_year}_Playlist.csv"
    else:
        output_filename += f"_Playlist.csv" 

    # using Path, create a dir to hold playlist csv files in the cwd
    # create dir if it doesn't exist; it won't crash if dir already exists
    output_dir = Path("Playlist CSV Files")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / output_filename
    # print(input(output_file))

    # use pandas module to create a dataframe of the playlist
    df_playlist = pd.DataFrame(list(playlist.items()), columns=["Song", "Artist"])
    df_playlist.to_csv(output_file, index=False)
    print()

    # Check if the file was created successfully
    if output_file.exists():
        print(f"Playlist saved successfully to: {output_file}")
    else:
        print(f"Error: Failed to save playlist to {output_file}") 

    # close browser
    browser.quit()

    return playlist # dict


##############################################

if __name__ == "__main__":
    film_name = input("Enter a film: ")
    film_year = input("Enter the year of release: ")
    scrape_soundtrack_film(film_name, film_year)