from bs4 import BeautifulSoup
import urllib
import requests
from flask import Flask, jsonify, make_response,request
import time
from selenium import webdriver
import os


ROOT_URL = 'https://myanimelist.net'
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


def good_image(url):
    lst = url.split('/')
    del lst[3:5]
    url = '/'.join(lst)
    return url

def search_anime(anime_name):
    search_url = 'https://myanimelist.net/search/all?q=' + str(anime_name)
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content,'lxml')
    search_results = []
    anime_list = soup.findAll('article')[0].findAll('div',{'class':'list di-t w100'})
    for anime in anime_list:
        search_result = {'image_link' : good_image(anime.find('div',{'class':'picSurround di-tc thumb'}).find('img').get('data-src')),
                        'link' : anime.find('div',{'class':'picSurround di-tc thumb'}).find('a').get('href'),
                        'name' : anime.find('div',{'class':'information di-tc va-t pt4 pl8'}).find('a').text
                        }
        search_results.append(search_result)
    return search_results

def get_recent_anime():
    recent_animes = []
    url = ROOT_URL
    response = requests.get('https://myanimelist.net/')
    soup = BeautifulSoup(response.content,'lxml')
    anime_list = soup.findAll('div',{'class' : 'widget-slide-outer'})[1].findAll('li',{'class' : 'btn-anime episode'})
    for anime in anime_list:
        recent_anime = {'episode_num' : anime.find('div',{'class':'link episode js-widget-episode-video-link'}).find('div',{'class' : 'title di-b'}).find('a').text,
                        'image_link' : good_image(anime.find('div',{'class':'link episode js-widget-episode-video-link'}).find('img').get('data-src')),
                        'name' : anime.find('div',{'class':'link episode js-widget-episode-video-link'}).get('data-title')
                        }
        recent_animes.append(recent_anime)
    
    print(recent_animes)
    return recent_animes

def get_popular_anime():
    url = ROOT_URL + '/topanime.php?type=airing'
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    popular_animes =[]
    anime_list = soup.find('table',{'class' : 'top-ranking-table'}).findAll('tr',{'class':'ranking-list'})
    for anime in anime_list:
        popular_anime = {'name' : anime.find('td',{'class' : 'title al va-t word-break'}).find('div',{'class':'detail'}).find('div',{'class' :'di-ib clearfix'}).find('a').text,
                        'anime_link' : anime.find('td',{'class' : 'title al va-t word-break'}).find('a').get('href'),
                        'image_link' : good_image(anime.find('td',{'class' : 'title al va-t word-break'}).find('a').find('img').get('data-src'))}
        popular_animes.append(popular_anime)
    return popular_animes

def get_anime_desc(url):
    categories = []
    episode_names = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    description = soup.find('span',{'itemprop' : 'description'}).text
    # category_tags = soup.find('div',{'class' : 'anime_info_body_bg'}).find_all('p',{'class':'type'})[2].findAll('a')
    response = requests.get(url+'/episode')
    soup = BeautifulSoup(response.content)
    episodes = soup.find('span',{'class' : 'di-ib pl4 fw-n fs10'}).text.split('/')[0][1:]
    episode_names = ['Episode '+ str(episode_name) for episode_name in range(1,int(episodes)+1)]
    info =  {'desc' : str(description),'episode_names':episode_names}
    return info

def get_video_link(url):
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,chrome_options=chrome_options)
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    video_link = soup.find('li',{'class' : 'xstreamcdn'}).find('a').get('data-video')
    driver.get(video_link)
    time.sleep(3)
    button = driver.find_element_by_xpath('//*[@id="loading"]/div')
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(button, 1, 1)
    action.click()
    action.perform()
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source)
    video_link = soup.find('video',{'class' : 'jw-video jw-reset'}).get('src')
    driver.get(video_link)
    link = {'video_link' : driver.current_url }
    driver.quit()
    return link

app = Flask(__name__)

@app.route('/search')
def fetch_search_results():
    term = request.args.get('search')
    response = search_anime(term)
    if response:
        api_response = make_response(jsonify(response),200)
    api_response.headers['Content-Type'] = 'application/json'
    return api_response

@app.route('/video_link')
def fetch_video_link():
    url = request.args.get('url')
    response = get_video_link(url)
    if response:
        api_response = make_response(jsonify(response),200)
    api_response.headers['Content-Type'] = 'application/json'
    return api_response

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