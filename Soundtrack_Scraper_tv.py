

# py script to scrape the soundtrack from a given tv show
# Tracks are pulled from each episode, ordered by season
# A Ridyard // 09.2024 // initial build
#           // 08.2025 // updated xpaths; all previous xpaths were deprecated
#                      // updated method for scraping song/artists
#                      // updated the method for handling multiple contributing artists on a single song
#                      // added conditional block for native script testing
#                      // updated episode_elements section; handles stale DOM / episode element references


# TODO
# check if opening credits song is in playlist - and if not - add it
# Add film functionality - 


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from pathlib import Path

def handleCookies(browser, selectors):
    # Called when navigating to new browser instance or web page; clear the "cookies" pop-up
    # Wait for the cookies "AGREE" button to be present and clickable
    agree_button_xpath = selectors["cookies_agree_button"]
    try:
        agree_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, agree_button_xpath)))
        agree_button.click()  # Click the "AGREE" button
    except:
        print("No cookies popup found.")


def findGivenElements(browser, xpath_in):
    # accepts an xpath argument & returns a list of corresponding elements 
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath_in)))
    return browser.find_elements(By.XPATH, xpath_in)


def showAllClick(browser, selectors, parent_div_in):
    # each episode-page will show an abridged list of tracks; if there is a "show all" button, this function will click & expand the track listing
    try:
        showAllButt_xpath = selectors["show_all_button"]
        showAllButtons = parent_div_in.find_elements(By.XPATH, showAllButt_xpath)
        if showAllButtons:
            showAllButt = showAllButtons[0]
            browser.execute_script("arguments[0].scrollIntoView(true);", showAllButt)
            browser.execute_script("arguments[0].click();", showAllButt)
        # debugging line
        # else:
        #     print("No 'Show All' button present — skipping expansion.")
    except Exception as e:
        print(f"Issue with clicking 'Show All': {str(e)}")


# occasionally the website will throw a "please log in" page; this function handles such events
def isLoginModalPresent(browser, selectors):
    try:
        modal_xpath = selectors["login_modal"]
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, modal_xpath)))
        return True
    except:
        return False


# the main scraping function; this function will call other functions in this script
def scrape_soundtrack_tv(tv_show, season_num):

    season_num = int(season_num)
    playlist = {}  # dict to hold each artist:song kv pair
    selectors = { # dict to hold the xpath strings 
        "cookies_agree_button": '//button[span[text()="AGREE"]]',
        "season_links": '//a[contains(@href, "/show/") and contains(@href, "/season-")]',
        "episode_cards": '//a[contains(@class, "card-border") and @data-discover="true"]',
        "login_modal": '//div[contains(@class, "modal")]//h1[contains(text(), "Log in")]',
        "episode_div": '//div[contains(@class, "scroll-mt-20")]',
        "show_all_button": './/button[.//p[text()="Show all tracks"]]',
        "track_container": './/div[contains(@class, "flex flex-col")]',
        "song": './/p[contains(@class, "font-bold") and contains(@class, "text-[1rem]")]',
        "artist": './/a[@data-discover="true" and contains(@href, "/artist/")]/small'
    }


    # Headless Firefox configuration
    options = Options()
    options.headless = True  # Enable headless mode / True = don't show browser

    # build the url from which we will scrape the soundtrack list
    baseURL = 'https://www.tunefind.com/show/'
    #tv_show = input('Please enter a TV Show to search...').split()
    tv_show = tv_show.split()
    tvShowClean = '-'.join(tv_show)  # replace whitespaces with '-' in url
    builtUrl = baseURL + tvShowClean

    # set browser object & open url
    browser = webdriver.Firefox(options = options) # Use options when initializing the WebDriver
    browser.get(builtUrl)
    handleCookies(browser, selectors)

    ###################################################

    # xpath of the show's seasons
    season_element_xpath = selectors["season_links"]
    season_elements = findGivenElements(browser, season_element_xpath)
    # for season in season_elements:
    #     print(season.text.strip())
    # print(input("here"))

    # amended the way we collect season_num (passed in as an function argument)
    # # choose the season to pull track listing from
    # if len(season_elements) > 1:
    #     currChoice = int(input(f'Scrape the soundtrack for which season?\n1-{str(len(season_elements))} \n'))
    # else:
    #     print(f'scraping soundtrack for {" ".join(tv_show)} season 1')
    #     currChoice = 1

    if season_num <1 or  season_num > len(season_elements):
        browser.quit()
        raise ValueError(f"Season {season_num} is out of range. Available: 1-{len(season_elements)}")

    else:
        currChoice = season_num


    # Click into the corresponding season link
    browser.execute_script("arguments[0].click();", season_elements[currChoice-1])


    ###################################################

    # xpath of "episode" elements within each season
    episode_element_xpath = selectors["episode_cards"]
    episode_elements = findGivenElements(browser, episode_element_xpath)

    #print(f"🔍 Found {len(episode_elements)} episodes.")
    # for j in range(len(episode_elements)):

    #     # Re-fetch the elements after each navigation to avoid stale element exception
    #     episode_elements = findGivenElements(browser, episode_element_xpath)
    #     episode = episode_elements[j]


    ##############################
    num_episodes = len(findGivenElements(browser, episode_element_xpath))
    for j in range(num_episodes):
        episode_elements = findGivenElements(browser, episode_element_xpath)
        if j >= len(episode_elements):
            print(f"❌ Episode index {j} out of range after re-fetch.")
            break

        episode = episode_elements[j]

    ###################################

        # Capture episode metadata BEFORE clicking
        try:
            episode_title = episode.find_element(By.XPATH, './/h4').text.strip()
            episode_date = episode.find_element(By.XPATH, './/p[not(contains(text(), "Tracks")) and not(contains(text(), "Questions"))]').text.strip()
        except Exception as e:
            episode_title = f"Episode {j+1}"
            episode_date = "Unknown"
            print(f"[{j+1}] Issue extracting episode info: {e}")


        ###########################################################################    


        print(f"Navigating to episode: {episode_title} ({episode_date})")
        
        # Try to click the episode link
        try:
            browser.execute_script("arguments[0].click();", episode)  # click into each episode

            # Wait briefly for page to load
            WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Check for login modal
            if isLoginModalPresent(browser, selectors):
                print("Login modal detected — skipping episode.") # TODO check this; we don't want to skip 
                browser.back()
                continue
            
            # pull song / artist elements from within a specific div element
            # avoids pulling additional / not required tracks that are duplicated around the page
            div_xpath = selectors["episode_div"]
            try:
                WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, div_xpath)))
            except TimeoutException:
                print(f"{episode_title}: Episode div not found — skipping.")
                browser.back()
                continue



            # Locate the parent div element
            parent_div = browser.find_element(By.XPATH, div_xpath)

            # the "show all tracks" button is located within the parent_div, hence why we pass the parent_div as an argument
            # this function call is inconsistent when we don't use the parent_div, ie we just search for the "show all tracks" button xpath
            showAllClick(browser, selectors, parent_div)  # Click "Show All" if present

            # once inside the episode page, scrape the tracks
            # Now find a specific song(p) & artist elements within the parent div
            # scrape song & artist
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

            # After scraping, navigate back to the season episode list
            browser.back()

        except Exception as e:
            print(f"{episode_title}: Could not navigate or scrape — error: {str(e)}")



    # placeholder for the csv filename, in a standardissed format
    words = tvShowClean.split('-')
    output_filename = '_'.join(word.capitalize() for word in words) # eg will output as "Game_Of_Thrones"

    # using Path, create a dir to hold playlist csv files in the cwd
    # create dir if it doesn't exist; it won't crash if dir already exists
    output_dir = Path("Playlist CSV Files")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f'{output_filename}_Season_{currChoice}_Playlist.csv'

    # use pandas module to create a dataframe of the playlist
    df_playlist = pd.DataFrame(list(playlist.items()), columns=["Song", "Artist"])
    df_playlist.to_csv(output_file, index=False)
    print()


    # Check if the file was created successfully
    if output_file.exists():
        print(f"Playlist saved successfully to: {output_file}")
    else:
        print(f"Error: Failed to save playlist to {output_file}")


    # Close the browser once scraping is complete
    browser.quit()

    print()
    for k,v in playlist.items():
        print(k + " : " + v)
    print(f"playlist length: {len(playlist)}")
    print()

    # return playlist
    return playlist # dict
    #return output_file # filepath

# tester function call - test any amendments to Soundtrack_Scraper_tv.py
# this will only run if this script is executed natively (ie not when imported into soundtrack_main.py)
if __name__ == "__main__":
    tv_show = input("Enter a tv show: ")
    season_num = input("Enter a season number: ")
    scrape_soundtrack_tv(tv_show, season_num)

    









