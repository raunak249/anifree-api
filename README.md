# anifree-api
An api made using Flask and Python built for the [AniFree app](https://github.com/raunak249/anifree)

# How is it built
It is built using Flask for python and deployed to Heroku as an app. It itself uses the [Anilist Api](https://github.com/AniList/ApiV2-GraphQL-Docs) to get information about anime.

# Directions to use

## Method
 `GET`
## URL
 `https://anifree-api.herokuapp.com/`
## Endpoints
  * `/recent_anime` : To get 10 most recent anime.
  * `/popular_anime` : To get 10 most trending anime.
  * `/search?search=SEARCH_TERM` : To search for a particular anime.
  * `/video_link?url=URL` : To get the video link of an episode using the [GoGoanime](gogoanime.io) url of a particular episode.
