from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import praw
from praw.exceptions import RedditAPIException
import re
import os

with open('config.json', 'r') as f:
  config = json.load(f)

host_names = {
    "YMSUnofficial": "Adam",
    "Ralph": "Ralph",
    "IHE": "Alex"
}
account_names = {
    'ymsunofficial': 'Adam',
    'ralfmakesmovies': 'Ralph',
    'ihe': 'Alex'
}

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")


def letterboxd_login(driver, username, password):
  driver.get('https://letterboxd.com/sign-in')
  driver.find_element_by_id('signin-username').send_keys(username)
  driver.find_element_by_id('signin-password').send_keys(password)
  time.sleep(3)
  driver.find_element_by_css_selector(".button[value='Sign in']").click()
  element = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CLASS_NAME, "nav-account")),
      message='Login Unsuccsessful'
  )
  return True


def get_ratings(driver, link):
  driver.get(link)
  activity_dict = {}
  ratings_dict = {}
  reviews_dict = {}

  for account in account_names:
    try:
      activity = driver.find_element_by_css_selector(f'section.activity-from-friends a[href*="/{account}/"]')
      activity_dict[account_names[account]] = activity.get_attribute('data-original-title')
    except NoSuchElementException:
      activity_dict[account_names[account]] = None

    try:
      rating = driver.find_element_by_css_selector(f'section.activity-from-friends a[href*="/{account}/"] span.rating').text
      ratings_dict[account_names[account]] = rating
    except NoSuchElementException:
      ratings_dict[account_names[account]] = None

    try:
      review = driver.find_element_by_css_selector(f'section#popular-reviews-with-friends .film-detail-content a[href*="/{account}/"]')
      review_link = review.get_attribute('href')
      if account_names[account] == 'Adam':
        driver.get(review_link)
        try:
          adam_review = driver.find_element_by_css_selector(f'div.review a[href*="/youtu.be/"]').get_attribute('href')
          reviews_dict[account_names[account]] = adam_review
        except NoSuchElementException:
          try:
            adam_review = driver.find_element_by_css_selector(f'div.review a[href*="/m.youtube.com/"]').get_attribute('href')
            reviews_dict[account_names[account]] = adam_review
          except NoSuchElementException:
            reviews_dict[account_names[account]] = review_link
        finally:
          driver.get(link)
      else:
        reviews_dict[account_names[account]] = review_link
    except NoSuchElementException:
      reviews_dict[account_names[account]] = None

  film_title = driver.find_element_by_css_selector('section#featured-film-header h1.headline-1').text
  film_year = driver.find_element_by_css_selector('section#featured-film-header a[href*="/films/year/"]').text

  return film_title, film_year, activity_dict, ratings_dict, reviews_dict


def get_search_results(driver, search_string):
  formatted_search_string = '+'.join(search_string.split())
  driver.get('https://letterboxd.com/search/films/{}/'.format(formatted_search_string))
  best_link = driver.find_element_by_css_selector('ul.results span.film-title-wrapper a[href*="/film/"]')
  return best_link.get_attribute('href')


def create_response(activity_dict, ratings_dict, reviews_dict, film_title, film_year, link):
  if all([a is None for a in activity_dict.values()]):
    response = f'None of the guys have seen [{film_title} ({film_year})]({link}) or have it on their watchlists!\n\n'
  else:
    response = f'Ratings for [{film_title} ({film_year})]({link}):\n\n'
    for host in activity_dict:
      if activity_dict[host] is None:
        response += '**{}**: {}\n\n'.format(host, 'Not yet watched, not on watchlist')
      else:
        phrase = activity_dict[host].lower().split()
        if 'wants' in phrase:
          response += '**{}**: {}\n\n'.format(host, 'On watchlist')
        elif 'watched' in phrase:
          response += '**{}**: {}\n\n'.format(host, 'Watched but not rated')
        elif 'rated' in phrase:
          response += '**{}**: {}/10\n\n'.format(host,
                                                 ratings_dict[host].count('★') * 2 + ratings_dict[host].count('½'))
        elif 'reviewed' in phrase:
          if ratings_dict[host] is not None:
            response += '**{}**: {}/10 ([Review]({}))\n\n'.format(host,
                                                                  ratings_dict[host].count('★') * 2 + ratings_dict[host].count('½'),
                                                                  reviews_dict[host])
          else:
            response += '**{}**: [Review]({}) (no rating)\n\n'.format(host, reviews_dict[host])

  return response


def find_search_string(keyword, comment_body):
  pattern = re.compile(f'(?<=({keyword} )).+', re.IGNORECASE)
  search_string = re.search(pattern, comment_body).group(0)
  return search_string


if __name__ == '__main__':

  reddit = praw.Reddit(
      user_agent=config['user_agent'],
      client_id=config['reddit_client_id'],
      client_secret=config['reddit_client_secret'],
      username=config['reddit_username'],
      password=config['reddit_password']
  )

  subreddit = reddit.subreddit(config['subreddit'])
  keywords = ['!ratings', 'ratings!']

  for comment in subreddit.stream.comments(skip_existing=True):
    for keyword in keywords:
      if keyword in comment.body.lower():
        search_string = find_search_string(keyword, comment.body)

        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        driver.implicitly_wait(5)
        try:
          letterboxd_login(driver, config['letterboxd_username'], config['letterboxd_password'])
        except TimeoutException as e:
          continue

        try:
          best_link = get_search_results(driver, search_string)
          film_title, film_year, activity_dict, ratings_dict, reviews_dict = get_ratings(driver, best_link)
          bot_response = create_response(activity_dict, ratings_dict, reviews_dict, film_title, film_year, best_link)
          if comment.author is not None:
            try:
              comment.reply(bot_response)
            except RedditAPIException:
              time.sleep(30)

        except NoSuchElementException as e:
          bot_response = f"I couldn't find any results for \"{search_string}\".\n\nPlease make sure your spelling (or the year) is correct!"
          if comment.author is not None:
            try:
              comment.reply(bot_response)
            except RedditAPIException:
              time.sleep(30)
        finally:
          driver.quit()
