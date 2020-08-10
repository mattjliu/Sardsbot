import unittest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from main import *
import json

with open('config.json', 'r') as f:
  config = json.load(f)


class TestLogin(unittest.TestCase):

  def setUp(self):
    self.driver = webdriver.Chrome()
    self.driver.implicitly_wait(5)

  def test_login_success(self):
    self.assertTrue(letterboxd_login(self.driver, config['letterboxd_username'], config['letterboxd_password']))

  def test_login_fail(self):
    with self.assertRaises(TimeoutException):
      result = letterboxd_login(self.driver, 'username', 'password')

  def tearDown(self):
    self.driver.quit()


class TestSearch(unittest.TestCase):

  def setUp(self):
    self.driver = webdriver.Chrome()
    self.driver.implicitly_wait(5)

  def test_search_success(self):
    self.assertEqual(get_search_results(self.driver, 'scarface 1983'), 'https://letterboxd.com/film/scarface-1983/')
    self.assertEqual(get_search_results(self.driver, 'scarface 1932'), 'https://letterboxd.com/film/scarface/')
    self.assertEqual(get_search_results(self.driver, 'eraserhead'), 'https://letterboxd.com/film/eraserhead/')
    self.assertEqual(get_search_results(self.driver, 'phantom menace'), 'https://letterboxd.com/film/star-wars-episode-i-the-phantom-menace/')
    self.assertEqual(get_search_results(self.driver, 'birdman'), 'https://letterboxd.com/film/birdman-or-the-unexpected-virtue-of-ignorance/')
    self.assertEqual(get_search_results(self.driver, 'dead alive'), 'https://letterboxd.com/film/braindead-1992/')
    self.assertEqual(get_search_results(self.driver, "rosemary's baby"), 'https://letterboxd.com/film/rosemarys-baby/')
    self.assertEqual(get_search_results(self.driver, "ocean's eleven"), 'https://letterboxd.com/film/oceans-eleven-2001/')

  def test_search_fail(self):
    with self.assertRaises(NoSuchElementException):
      get_search_results(self.driver, 'scarface 1984')
    with self.assertRaises(NoSuchElementException):
      get_search_results(self.driver, 'adsfasdfjhalsdf')

  def tearDown(self):
    self.driver.quit()


# These test cases may change with ratings / watchlist changes
class TestGetRatings(unittest.TestCase):
  def setUp(self):
    self.driver = webdriver.Chrome()
    self.driver.implicitly_wait(5)
    letterboxd_login(self.driver, config['letterboxd_username'], config['letterboxd_password'])

  def test_rated(self):
    film_title, film_year, activity_dict, ratings_dict, reviews_dict = get_ratings(self.driver, 'https://letterboxd.com/film/being-john-malkovich/')
    self.assertEqual(film_title, 'Being John Malkovich')
    self.assertEqual(film_year, '1999')
    self.assertEqual(activity_dict, {'Adam': 'Rated by YMSUnofficial', 'Ralph': 'Rated by Ralph', 'Alex': 'Rated by IHE'})
    self.assertEqual(ratings_dict, {'Adam': '★★★★★', 'Ralph': '★★★★½', 'Alex': '★★★★'})
    self.assertEqual(reviews_dict, {'Adam': None, 'Ralph': None, 'Alex': None})

  def test_reviewed(self):
    film_title, film_year, activity_dict, ratings_dict, reviews_dict = get_ratings(self.driver, 'https://letterboxd.com/film/the-lighthouse-2019/')
    self.assertEqual(film_title, 'The Lighthouse')
    self.assertEqual(film_year, '2019')
    self.assertEqual(activity_dict, {'Adam': 'Reviewed by YMSUnofficial', 'Ralph': 'Reviewed by Ralph', 'Alex': 'Reviewed by IHE'})
    self.assertEqual(ratings_dict, {'Adam': '★★★★★', 'Ralph': '★★★★★', 'Alex': '★★★★★'})
    self.assertEqual(reviews_dict,
                     {
                         'Adam': 'https://youtu.be/FZqd3CJ2FrY',
                         'Ralph': 'https://letterboxd.com/ralfmakesmovies/film/the-lighthouse-2019/',
                         'Alex': 'https://letterboxd.com/ihe/film/the-lighthouse-2019/'
                     })

  def test_adam_youtube(self):
    film_title, film_year, activity_dict, ratings_dict, reviews_dict = get_ratings(self.driver, 'https://letterboxd.com/film/the-killing-of-a-sacred-deer/')
    self.assertEqual(film_title, 'The Killing of a Sacred Deer')
    self.assertEqual(film_year, '2017')
    self.assertEqual(activity_dict, {'Adam': 'Reviewed by YMSUnofficial', 'Ralph': 'Rated by Ralph', 'Alex': 'Rated by IHE'})
    self.assertEqual(ratings_dict, {'Adam': '★★★★½', 'Ralph': '★★★★½', 'Alex': '★★★½'})
    self.assertEqual(reviews_dict, {'Adam': 'https://m.youtube.com/watch?v=bF5eaG1e3t8', 'Ralph': None, 'Alex': None})

  def test_no_adam_youtube(self):
    film_title, film_year, activity_dict, ratings_dict, reviews_dict = get_ratings(self.driver, 'https://letterboxd.com/film/the-holy-mountain/')
    self.assertEqual(film_title, 'The Holy Mountain')
    self.assertEqual(film_year, '1973')
    self.assertEqual(activity_dict, {'Adam': 'Reviewed by YMSUnofficial', 'Ralph': 'Rated by Ralph', 'Alex': 'Rated by IHE'})
    self.assertEqual(ratings_dict, {'Adam': '★★★★★', 'Ralph': '★★★★½', 'Alex': '★★★★★'})
    self.assertEqual(reviews_dict, {'Adam': 'https://letterboxd.com/ymsunofficial/film/the-holy-mountain/1/', 'Ralph': None, 'Alex': None})

  def test_no_activity(self):
    film_title, film_year, activity_dict, ratings_dict, reviews_dict = get_ratings(self.driver, 'https://letterboxd.com/film/last-year-at-marienbad/')
    self.assertEqual(film_title, 'Last Year at Marienbad')
    self.assertEqual(film_year, '1961')
    self.assertEqual(activity_dict, {'Adam': None, 'Ralph': None, 'Alex': None})
    self.assertEqual(ratings_dict, {'Adam': None, 'Ralph': None, 'Alex': None})
    self.assertEqual(reviews_dict, {'Adam': None, 'Ralph': None, 'Alex': None})

  def test_watched_not_rated(self):
    film_title, film_year, activity_dict, ratings_dict, reviews_dict = get_ratings(self.driver, 'https://letterboxd.com/film/cube/')
    self.assertEqual(film_title, 'Cube')
    self.assertEqual(film_year, '1997')
    self.assertEqual(activity_dict, {'Alex': 'Rated by IHE', 'Adam': 'Watched by YMSUnofficial', 'Ralph': 'Watched by Ralph'})
    self.assertEqual(ratings_dict, {'Adam': None, 'Ralph': None, 'Alex': '★★★'})
    self.assertEqual(reviews_dict, {'Adam': None, 'Ralph': None, 'Alex': None})

  def test_on_watchlist(self):
    film_title, film_year, activity_dict, ratings_dict, reviews_dict = get_ratings(self.driver, 'https://letterboxd.com/film/the-last-temptation-of-christ/')
    self.assertEqual(film_title, 'The Last Temptation of Christ')
    self.assertEqual(film_year, '1988')
    self.assertEqual(activity_dict, {'Adam': 'YMSUnofficial wants to watch', 'Alex': 'IHE wants to watch', 'Ralph': 'Ralph wants to watch'})
    self.assertEqual(ratings_dict, {'Adam': None, 'Ralph': None, 'Alex': None})
    self.assertEqual(reviews_dict, {'Adam': None, 'Ralph': None, 'Alex': None})

  def tearDown(self):
    self.driver.quit()

class TestBotCommand(unittest.TestCase):

  def test_simple_commands(self):
    search_string = find_search_string('!ratings', '!ratings search_string')
    self.assertEqual(search_string, 'search string')
    search_string = find_search_string('ratings!', 'ratings! search_string')
    self.assertEqual(search_string, 'search string')

  def test_non_simple_commands(self):
    search_string = find_search_string('!ratings',
                                       '''
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
      Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      \n!ratings search_string
      ''')
    self.assertEqual(search_string, 'search string')
    search_string = find_search_string('!ratings',
                                       '''!ratings search_string
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
      Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      ''')
    self.assertEqual(search_string, 'search string')
    search_string = find_search_string('!ratings',
                                       '''
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
      Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      \n!ratings search_string
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
      Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      ''')
    self.assertEqual(search_string, 'search string')

    search_string = find_search_string('ratings!',
                                       '''
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
      Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      \nratings! search_string
      ''')
    self.assertEqual(search_string, 'search string')
    search_string = find_search_string('ratings!',
                                       '''ratings! search_string
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
      Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      ''')
    self.assertEqual(search_string, 'search string')
    search_string = find_search_string('ratings!',
                                       '''
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
      Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      \nratings! search_string
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
      Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      ''')
    self.assertEqual(search_string, 'search string')

  def test_no_film_title(self):
    with self.assertRaises(AttributeError):
      search_string = find_search_string('!ratings', '!ratings')
    with self.assertRaises(AttributeError):
      search_string = find_search_string('ratings!', 'ratings!')
    with self.assertRaises(AttributeError):
      search_string = find_search_string('!ratings',
                                         '''
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
      Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      \n!ratings
      ''')
    with self.assertRaises(AttributeError):
      search_string = find_search_string('ratings!',
                                         '''
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
      Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      \nratings!
      ''')

  def test_multiple_commands(self):
    search_string = find_search_string('!ratings',
                                       '!ratings search_string0\n!ratings search_string1\n!ratings search_string2\n!ratings search_string3')
    self.assertEqual(search_string, 'search string0')

  def test_false_positive_match(self):
    with self.assertRaises(AttributeError):
      search_string = find_search_string('ratings!',
                                         '''
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum ratings! search_string
        ''')


if __name__ == '__main__':
  unittest.main()
