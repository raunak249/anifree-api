import urllib
import requests
from flask import Flask, jsonify, make_response, request
import re
import time

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
                        'time_remaining' : anime['nextAiringEpisode']['timeUntilAiring']
                        }
        search_results.append(search_result)
    return search_results

def get_popular_anime():
    response = requests.post(ROOT_URL, json={'query': search_query})
    anime_list = response.json()
    results = []
    for anime in anime_list['data']['Page']['media']:
        search_result = {'image_link' : anime['coverImage']['extraLarge'],
                        'description' : cleanhtml(anime['description']),
                        'name' : anime['title']['romaji']
                        }
        results.append(search_result)
    return results


# def get_video_link(url):
#     driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,chrome_options=chrome_options)
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content)
#     video_link = soup.find('li',{'class' : 'xstreamcdn'}).find('a').get('data-video')
#     driver.get(video_link)
#     time.sleep(3)
#     button = driver.find_element_by_xpath('//*[@id="loading"]/div')
#     action = webdriver.common.action_chains.ActionChains(driver)
#     action.move_to_element_with_offset(button, 1, 1)
#     action.click()
#     action.perform()
#     time.sleep(3)
#     soup = BeautifulSoup(driver.page_source)
#     video_link = soup.find('video',{'class' : 'jw-video jw-reset'}).get('src')
#     driver.get(video_link)
#     link = {'video_link' : driver.current_url }
#     driver.quit()
#     return link

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


@app.route('/')
def home():
    api_response = make_response({'time':str(time.strftime('%A %B, %d %Y %H:%M:%S'))},200)
    api_response.headers['Content-Type'] = 'application/json'
    return api_response

if __name__ == "__main__":
    app.run()
