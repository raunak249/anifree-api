from bs4 import BeautifulSoup
import urllib
import requests
from flask import Flask, jsonify, make_response,request
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os

ROOT_URL = 'https://animekisa.tv'
CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sanbox")
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
#"C:/Windows/chromedriver.exe"
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
    recent_anime = []
    div_classes = ['episode-box test','episode-box test ep-second','episode-box test ep-third','episode-box test ep-second ep-third']
    url = ROOT_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    anime_divs = []
    anime_divs.append(soup.find_all('div',{'class' : div_classes[0]})[0])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[1]})[0])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[2]})[0])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[1]})[1])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[0]})[1])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[3]})[0])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[0]})[2])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[1]})[2])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[2]})[1])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[1]})[3])
    for anime_div in anime_divs:
        recent_anime_info = {
            'link' : str(anime_div.find('a',{'class' : 'an'}).get('href')), 
            'name' : str(anime_div.find('div',{'class' : 'title-box-2'}).text),
            'episode_num' : str(anime_div.find('div',{'class' : 'centerv2'}).text.split('/')[0][:-2].strip()),
            'image_link' : str(anime_div.find('div',{'class' : 'image-box'}).find('img').get('src'))
        }
        recent_anime.append(recent_anime_info)
    return recent_anime

def get_popular_anime():
    url = ROOT_URL + str('/popular')
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    animes = soup.findAll('a',{'class':'an'})[:10]
    popular_animes = []
    for anime in animes:
        popular_anime = {
            'image_link' : str(anime.find('div',{'class':'similarpic'}).find('img').get('src')),
            'name' : str(anime.find('div',{'class':'similardd'}).text)[3:].strip(),
            'anime_link' : str(anime.get('href'))
        }
        popular_animes.append(popular_anime)
    return popular_animes

def get_anime_desc(url):
    categories = []
    episode_links = []
    episode_names = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    description = soup.find('div',{'class' : 'infodes2'}).text
    category_tags = soup.findAll('div',{'class' : 'infodes2'})[1].find('div',{'class':'textc'}).findAll('a',{'class':'infoan'})
    episode_tags = soup.find('div',{'class' : 'infoepbox'}).findAll('a',{'class':'infovan'})

    for episode_tag in episode_tags:
        episode_link = episode_tag.get('href')
        episode_links.append('/'+episode_link)
        episode_name = episode_tag.find('div',{'class':'infoept2'}).find('div',{'class':'centerv'}).text.strip()
        episode_names.append(episode_name)
    for category_tag in category_tags:
        categories.append(category_tag.text)
    info =  {'desc' : description.strip(),'categories':categories,'episode_links':episode_links,'episode_names':episode_names}
    return info

def get_video_link(url):
    browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,chrome_options=chrome_options)
    browser.get(url)
    elem = browser.find_element_by_xpath('//*[@id="main"]/div[7]/div')
    elem.click()
    browser.switch_to.window(browser.window_handles[1])
    iframe = browser.find_elements_by_tag_name('iframe')[0]
    browser.switch_to_frame(iframe)
    buttons = browser.find_elements_by_xpath("//*[contains(text(), 'Download Xstreamcdn')]")
    buttons[0].click()
    browser.switch_to.window(browser.window_handles[2])
    video_link = browser.current_url
    link_parts = video_link.split('/')
    first_part = '/'.join(link_parts[:-2])
    last_part = link_parts[-1]
    video_link = {'video_link' : first_part+'/v/'+last_part}
    browser.quit()
    return video_link


app = Flask(__name__)

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