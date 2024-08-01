# pylint: disable=broad-exception-caught disable=broad-exception-raised
'''
Module where main logic is executed, everything since gathering the data
to storing it to notifying the final user
'''

from scraper import Scraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager



def start(url):
    '''
    Starts the web scraping process, by fetching posts, parsing, storing and notifying
    '''
    scraper_instance = Scraper()

    # Get article HTML data
    articles_html = scraper_instance.fetch_html(url)

    # Parse HTML into a structured object
    articles = scraper_instance.parse_article_html(articles_html)

    print(articles)


if __name__ == '__main__':
    URL = 'https://www.facebook.com/profile.php?id=100077086791019'
    # URL = ''

    start(URL)
