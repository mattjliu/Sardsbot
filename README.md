# Sardsbot

A reddit bot built using [Selenium](https://selenium-python.readthedocs.io/) and [PRAW](https://praw.readthedocs.io/en/latest/) for the subreddit of the film podcast [Sardonicast](https://sardonicast.fireside.fm/).

You can head on over to [u/sardsbot](https://www.reddit.com/user/sardsbot/) to see the bot's latest activity.

<p align="center">
 <img src="/screenshot.png" width="700"/>
</p>

## Setup and Installation

You will need:

- A [Letterboxd](https://letterboxd.com/) account for the bot. For this to work, be sure to follow *only* the accounts of [Adam](https://letterboxd.com/ymsunofficial/), [Ralph](https://letterboxd.com/ralfmakesmovies/) and [Alex](https://letterboxd.com/ihe/) on this account.
- A reddit account for the bot. [Create an application](https://www.reddit.com/prefs/apps) using said account to obtain a `CLIENT_ID` and `CLIENT_SECRET`.

1. Clone this repo and run `pip install requirements.txt`
2. Fill out your crendentials in `config.json`. The config file should look like this:
```
{
  "letterboxd_username": "letterboxd_bot",
  "letterboxd_password": "password",
  "reddit_client_id": "CLIENT_ID",
  "reddit_client_secret": "CLIENT_SECRET",
  "reddit_username": "reddit_bot",
  "reddit_password": "password",
  "user_agent": "bot by u/user",
  "subreddit": "Sardonicast"
}
```
3. Install [ChromeDriver](https://chromedriver.chromium.org/) and [Google Chrome](https://www.google.com/intl/en_ca/chrome/). If you run this locally and have Chrome installed, you should comment out the line `chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")` in `main.py`.
4. Include the ChromeDriver location in your PATH environement variable. If you do this, you should not pass in `executable_path=os.environ.get("CHROMEDRIVER_PATH")` when calling `driver = webdriver.Chrome(options=chrome_options)` in `main.py`. Otherwise, you can set your ChromeDriver location to the `CHROMEDRIVER_PATH` environment variable.
5. If you want to test the bot, you can set the `subreddit` field in `config.json` to a subreddit like [r/testingground4bots](https://www.reddit.com/r/testingground4bots/).
6. Run `python main.py`

## Deployement

I'm hosting the bot using [Heroku](https://www.heroku.com/). If you are deploying in another way, make sure you can install ChromeDriver and Google Chrome or add the location of ChromeDriver and the Google Chrome binaries in your environment variables.

To deploy using Heroku, you need to add the following buildpacks to your app in addition to the standard python buildpack:
- [Google Chrome Buildpack](https://github.com/heroku/heroku-buildpack-google-chrome)
- [ChromeDriver Buildpack](https://github.com/heroku/heroku-buildpack-chromedriver)

Simply copy and paste in the urls of the github repositories.

Set the following additional config vars in you app settings:
- `KEY: CROMEDRIVER_PATH`, `VALUE: /app/.chromedriver/bin/chromedriver`
- `KEY: GOOGLE_CHROME_BIN`, `VALUE: /app/.apt/usr/bin/google-chrome`

Create a `Procfile` and include the single process `worker: python main.py`.

Finally, deploy via `git push heroku master`.

## Letterboxd API

The bot works by using Selenium to login to a Letterboxd account that follows the 3 hosts of the podcast in order to scrape their ratings, watchlist information and reviews. It also scrapes the Letterboxd search results to make it easier for users (when a redditor comments `!ratings <film_title>`, the bot scrapes the Letterboxd search results for `<film_title>` for the best match).

The [Letterboxd API](http://api-docs.letterboxd.com/) is currently in closed beta, and it is unclear how easy it is to gain access. If I eventually obtain the API, I will make sure to rewrite the bot to use it instead. Until then, this is the best implementation I came up wit.
