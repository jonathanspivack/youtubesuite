#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common import action_chains, keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from collections import defaultdict
import pymongo



client = pymongo.MongoClient(connect=False)
db = client.youtube


def pull_transcript(youtube_watch_link,youtube_id):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    browser = webdriver.Chrome("/mnt/c/Users/Jonathan Spivack/Downloads/chromedriver_win32/chromedriver.exe", chrome_options=options)
    # browser = webdriver.Chrome("/mnt/c/Users/ivy1g/AppData/Local/Programs/Python/Python36-32/chromedriver.exe" , chrome_options=options)
    #browser = webdriver.Chrome("/usr/local/bin/chromedriver",chrome_options=options)
    browser.get('{}'.format(youtube_watch_link))


    try:
       element = WebDriverWait(browser, 20).until(
           EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='More actions']")))
       element.click()
    except:
       print ("Not aria-label=more actions.. trying aria-label=action menu")
       try:
           element = WebDriverWait(browser, 20).until(
               EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Action menu.']")))
           element.click()
       except Exception as e:
           print ("Nooooo whats wrong")
           print (e)
    try:
       elemz = browser.find_element_by_xpath("//yt-formatted-string[@class='style-scope ytd-menu-service-item-renderer']")
       elemz.click()

    except Exception as e:
       print ("I think there are no captions/transcript available.....")
       print (e)



    time.sleep(5)
    try:

        htmlSource = browser.page_source
        soup = BeautifulSoup(htmlSource)
        parents = soup.findAll("div",{"class":"cue-group style-scope ytd-transcript-body-renderer"})
        records = []
        captions_dict = defaultdict(list)

        for parent in parents:
            time_stamp = parent.text.strip()[0:5]
            caption = parent.text.strip()[5:]
            records.append((time_stamp.strip(), caption.strip()))

            words = caption.strip().split()

            for word in words:
                word=word.replace(".", "")
                word=word.replace("(", "")
                word=word.replace(")", "")
                word=word.replace(",", "")
                word=word.replace("!", "")
                word=word.encode('ascii', 'ignore').decode('ascii')
                captions_dict[word.lower()].append(time_stamp)



        df = pd.DataFrame(records, columns=['time_stamp', 'caption'])

        lastrowtime=df['time_stamp'].iloc[-1]
        print(lastrowtime)
        new_cache = {
            "url": youtube_id,
            "lasttimestamp": lastrowtime,
            "captionsd": dict(captions_dict)
        }
        db.cached.insert(new_cache, check_keys=False)
        browser.quit()
    except Exception as e:
        browser.quit()
        print('lololol')
        lastrowtime=""
        normaldict={".":"[00:00]"}
        new_cache = {
            "url": youtube_id,
            "lasttimestamp": lastrowtime,
            "captionsd": normaldict
        }

        db.cached.insert(new_cache, check_keys=False)


        return "No"



    print('appending to db')



if __name__ == "__main__":
    pull_transcript("https://www.youtube.com/watch?v=NAp-BIXzpGA")
