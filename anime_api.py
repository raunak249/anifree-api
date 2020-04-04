from bs4 import BeautifulSoup
import urllib
import requests
from flask import Flask, jsonify, make_response

ROOT_URL = 'https://animekisa.tv'
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
    recent_anime = []
    div_classes = ['episode-box test','episode-box test ep-second','episode-box test ep-third']
    url = ROOT_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    anime_divs = []
    anime_divs.append(soup.find_all('div',{'class' : div_classes[0]})[0])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[1]})[0])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[2]})[0])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[1]})[1])
    anime_divs.append(soup.find_all('div',{'class' : div_classes[0]})[1])
    for anime_div in anime_divs:
        recent_anime_info = {
            'link' : str(anime_div.find('a',{'class' : 'an'}).get('href')), 
            'name' : str(anime_div.find('div',{'class' : 'title-box-2'}).text),
            'episode_num' : str(anime_div.find('div',{'class' : 'centerv2'}).text[:9]),
            'image_link' : str(anime_div.find('div',{'class' : 'image-box'}).find('img').get('src'))
        }
        recent_anime.append(recent_anime_info)
    return recent_anime

app = Flask(__name__)

@app.route('/recent_anime')
def home():
    response = get_recent_anime()
    if response:
        api_response = make_response(jsonify(response),200)
    api_response.headers['Content-Type'] = 'application/json'
    return api_response

if __name__ == "__main__":
    app.run()