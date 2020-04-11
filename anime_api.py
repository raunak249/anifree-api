import urllib
import requests
from flask import Flask, jsonify, make_response, request
import re
import time
from selenium import webdriver
import os
from bs4 import BeautifulSoup


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


def ConvertSectoDay(n): 
  
    day = n // (24 * 3600) 
  
    n = n % (24 * 3600) 
    hour = n // 3600
  
    n %= 3600
    minutes = n // 60
  
    n %= 60
    seconds = n 
    return day

ROOT_URL = 'https://graphql.anilist.co'
search_query = '''query($search : String) { # Define which variables will be used in the query (id)
                    Page(page:1,perPage:100){
                        media(type:ANIME,search:$search){
                            title{
                                romaji
                            },
                            status,
                            description,
                            season,
                            episodes,
                            duration,
                            averageScore,
                            coverImage{
                                extraLarge
                            }
                        }
                     }
                }'''
popular_query  = '''
query { # Define which variables will be used in the query (id)
  Page(page:1,perPage:10){
    media(type:ANIME,sort :POPULARITY_DESC){
      title{
        romaji,
      },
      status,
      description,
      episodes,
      duration,
      averageScore,
      coverImage{
        extraLarge
      }
    }
  }
}'''

recent_query = '''
query { # Define which variables will be used in the query (id)
  Page(page:1,perPage:10){
    media(type:ANIME,status :RELEASING,sort:TRENDING_DESC){
      title{
        romaji
      },
      nextAiringEpisode {
        timeUntilAiring
        episode
      },
      status,
      description(asHtml:false),
      duration,
      averageScore,
      coverImage{
        extraLarge
      }
    }
  }
}
'''
def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def search_anime(anime_name):
    search_variable = {
        'search': anime_name
    }
    response = requests.post(ROOT_URL, json={'query': search_query, 'variables': search_variable})
    anime_list = response.json()
    search_results = []
    for anime in anime_list['data']['Page']['media']:
        search_result = {'image_link' : anime['coverImage']['extraLarge'],
                        'description' : cleanhtml(anime['description']),
                        'name' : anime['title']['romaji']
                        }
        search_results.append(search_result)
    return search_results


def get_recent_anime():
    response = requests.post(ROOT_URL, json={'query': recent_query})
    anime_list = response.json()
    search_results = []
    for anime in anime_list['data']['Page']['media']:
        search_result = {'image_link' : anime['coverImage']['extraLarge'],
                        'description' : cleanhtml(anime['description']),
                        'episode_num' : anime['nextAiringEpisode']['episode'] - 1,
                        'name' : anime['title']['romaji'],
                        'time_remaining' : ConvertSectoDay(anime['nextAiringEpisode']['timeUntilAiring'])
                        }
        search_results.append(search_result)
    return search_results

def get_popular_anime():
    response = requests.post(ROOT_URL, json={'query': popular_query})
    anime_list = response.json()
    results = []
    for anime in anime_list['data']['Page']['media']:
        search_result = {'image_link' : anime['coverImage']['extraLarge'],
                        'description' : cleanhtml(anime['description']),
                        'name' : anime['title']['romaji'],
                        'score' : anime['averageScore']
                        }
        results.append(search_result)
    return results


def get_video_link(url):
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,chrome_options=chrome_options)
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    video_link = soup.find('div',{'class' : 'anime_muti_link'}).find('a').get('data-video')
    driver.get('http:'+video_link)
    button = driver.find_element_by_xpath('//*[@id="myVideo"]/div[2]/div[4]')
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element(button)
    action.click()
    action.perform()
    action.click()
    action.perform()
    time.sleep(1)
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

@app.route('/video_link')
def fetch_video_link():
    url = request.args.get('url')
    try:
      response = get_video_link(url)
      if response:
          api_response = make_response(jsonify(response),200)
    except:
      api_response = make_response({'video_link':'null'},200)
    api_response.headers['Content-Type'] = 'application/json'
    return api_response


@app.route('/')
def home():
    api_response = make_response({'time':str(time.strftime('%A %B, %d %Y %H:%M:%S'))},200)
    api_response.headers['Content-Type'] = 'application/json'
    return api_response

if __name__ == "__main__":
    app.run()
