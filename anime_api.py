from bs4 import BeautifulSoup
import urllib
import requests
from flask import Flask, jsonify, make_response,request
import time
from selenium import webdriver
import os


ROOT_URL = 'https://www.gogoanime.io'
CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sanbox")
chrome_options.binary_location = '/app/.apt/usr/bin/google-chrome'
#chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
'''
Anime :
    anime_name
    description
    main_image
    no_of_episodes
    Episodes[]

Episode :
    episode_name
    thumbnail
    duration
    video_link
'''



def search_anime(anime_name):
    search_url = 'https://animekisa.tv/search?q=' + str(anime_name)
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content)
    divs = soup.find_all('div',{'class' :'similarbox'})
    div = divs[0]
    links = div.find_all('a',{'class' : 'an'})
    for link in links:
        print(link.get('href'))

def get_recent_anime():
    '''
    To get 5 most recently released anime
    '''
    recent_animes = []
    url = ROOT_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    anime_list = soup.find('ul',{'class' : 'items'}).find_all('li')
    for anime in anime_list:
        recent_anime = {'episode_num' : anime.find('p',{'class':'episode'}).text,
                        'image_link' : anime.find('img').get('src'),
                        'link' : ROOT_URL + anime.find('a').get('href'),
                        'name' : anime.find('p',{'class' : 'name'}).text
                        }
        recent_animes.append(recent_anime)
    
    return recent_animes

def get_popular_anime():
    url = ROOT_URL + str('/popular.html')
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    anime_list = soup.find('ul',{'class':'items'}).find_all('li')[:10]
    popular_animes = []
    for anime in anime_list:
        popular_anime = {'name' : anime.find('p',{'class' : 'name'}).text,
                        'anime_link' : ROOT_URL + anime.find('p',{'class' : 'name'}).find('a').get('href'),
                        'image_link' : anime.find('img').get('src')}
        popular_animes.append(popular_anime)
    return popular_animes

def get_anime_desc(url):
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,chrome_options=chrome_options)
    categories = []
    episode_links = []
    episode_names = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    description = soup.find('div',{'class' : 'anime_info_body_bg'}).find_all('p',{'class':'type'})[1].text
    category_tags = soup.find('div',{'class' : 'anime_info_body_bg'}).find_all('p',{'class':'type'})[2].findAll('a')
    driver.get(url)
    time.sleep(3)
    episode_list = driver.find_element_by_id('episode_page')
    episode_list_items = episode_list.find_elements_by_tag_name('li') 
    for episode_list_item in reversed(episode_list_items):
        episode_list_item.click()
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source)
        episodes = soup.find('ul',{'id':'episode_related'}).findAll('li')
        for episode in episodes:
            episode_link = ROOT_URL + (episode.find('a').get('href')).strip()
            episode_links.append(episode_link)
            episode_name = episode.find('div',{'class' : 'name'}).text
            episode_names.append(episode_name)
    for category_tag in category_tags:
        categories.append((category_tag.text).split(' ')[-1])
    info =  {'desc' : description.strip(),'categories':categories,'episode_links':episode_links,'episode_names':episode_names}
    driver.quit()
    return info
#get_anime_desc("https://www17.gogoanime.io/category/boruto-naruto-next-generations")

app = Flask(__name__)

@app.route('/recent_anime')
def fetch_recent_anime():
    response = get_recent_anime()
    if response:
        api_response = make_response(jsonify(response),200)
    api_response.headers['Content-Type'] = 'application/json'
    return api_response

@app.route('/popular_anime')
def fetch_popular_anime():
    response = get_popular_anime()
    if response:
        api_response = make_response(jsonify(response),200)
    api_response.headers['Content-Type'] = 'application/json'
    return api_response

@app.route('/anime_info')
def fetch_anime_info():
    url = request.args.get('url')
    response = get_anime_desc(url)
    if response:
        api_response = make_response(jsonify(response),200)
    api_response.headers['Content-Type'] = 'application/json'
    return api_response

@app.route('/')
def home():
    api_response = make_response({'time':str(time.strftime('%A %B, %d %Y %H:%M:%S'))},200)
    api_response.headers['Content-Type'] = 'application/json'
    return api_response

if __name__ == "__main__":
    app.run()