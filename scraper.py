# pylint: disable=broad-exception-caught disable=broad-exception-raised
'''
Provides all the utils to scrape the data
'''

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

class Scraper:
    '''
    Scraper class that holds all the logic to interact with
    the webpage an extract the data
    '''

    def __init__(self):
        # Initialize chrome driver
        service = Service(GeckoDriverManager().install())
        options = webdriver.FirefoxOptions()
        # options.add_argument('--headless')  # Run headless

        self.driver = webdriver.Firefox(service=service, options=options)

    def find_element(self, by, value, optional=False):
        '''
        Utility method to find an element; handles absence based on 'optional' flag.
        '''
        try:
            return self.driver.find_element(by, value)
        except Exception:
            if not optional:
                raise
            return None

    def click_if_present(self, by, value):
        '''Attempts to click an element if it's present.'''
        element = self.find_element(by, value, optional=True)
        if element:
            element.click()

    def bypass_dialogs(self):
        '''Bypass any pop-up dialogs such as cookies and login prompts.'''
        self.click_if_present(By.CSS_SELECTOR, 'div[aria-label="Decline optional cookies"]')
        self.click_if_present(By.CSS_SELECTOR, 'div[aria-label="Close"] i')

    def fetch_articles(self):
        '''
        Fetch the main content
        The HTML is a mess so we can use the loading element
        and find what we want through its parents
        '''

        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'div[role="main"]')))
        main_container = self.driver.find_element(By.CSS_SELECTOR, 'div[role="main"]')

        if not main_container:
            raise Exception("Could not find the main page content.")

        loading_divs = main_container.find_elements(By.CSS_SELECTOR,
            'div[aria-label="Loading..."]')

        parent = None
        for loading in loading_divs:
            parent = loading.find_element(By.XPATH, '..')

            # Check if we have the right parent
            parent_attribute = parent.get_attribute('role')
            if parent_attribute and parent_attribute == 'article':
                break

        if not parent:
            raise Exception("Could not find the loading element.")

        raw_articles = (parent.find_element(By.XPATH, '../../..')
            .find_elements(By.XPATH, './*'))

        # We check if its less than two since the loading dom trash
        # will be included in the childs
        if len(raw_articles) < 2:
            raise Exception("Could not find any article in the page")

        # Filter the empty articles and invalid elements
        clean_articles = []
        for article in raw_articles:
            child_elems = article.find_elements(By.XPATH, './*')

            # Filter empty articles
            if len(child_elems) < 1:
                continue

            # Filter articles that werent loaded yet
            has_loading = False
            for child in child_elems:
                if len(child.find_elements(By.CSS_SELECTOR, 'div[aria-label="Loading..."]')):
                    has_loading = True
                    break

            if has_loading:
                continue

            # Should be a valid article, so add it
            clean_articles.append(article)

        return clean_articles

    def scroll_page(self, pixels = 1000):
        '''
        Scrolls the page until a specific height in pixels
        '''

        self.driver.execute_script(f"window.scrollBy(0, {pixels});")  # Scroll down by x pixels

    def remove_login_annoynace(self):
        '''
        Removed the annoying authentication prompt that is sticky
        on the bottom of the page.
        This can cause problems when trying to click elements that
        this thing is obscuring
        '''
        self.driver.execute_script('''
            Array.from(document.querySelectorAll('div[data-nosnippet]')).forEach(el => el.remove());
            ''')

    def fetch_html(self, url):
        '''
        Fetch the html with the posts content from the DOM
        '''
        self.driver.get(url)

        # Bypass cookies and login dialogs
        self.bypass_dialogs()

        # Remove auth prompt
        self.remove_login_annoynace()

        # Scroll the page to load the articles
        self.scroll_page()

        # Wait for posts to load
        time.sleep(5)

        # Fetch a clean article list
        return self.fetch_articles()

class ArticleParser:
    '''
    Handles parsing of HTML elements to extract article data.
    '''

    def parse_article_html(self, articles):
        '''
        Parse and structure HTML elements from a list of article elements.
        '''

        if not articles:
            raise ValueError("No articles provided for parsing.")

        parsed_articles = []
        for article in articles:
            parsed_article = self.extract_article_details(article)

            if parsed_article:
                parsed_articles.append(parsed_article)

        return parsed_articles

    def extract_article_details(self, article):
        '''Extracts details from a single article element.'''

        parsed_article = {}
        try:
            # Attempt to expand hidden text if necessary
            self.expand_hidden_text(article)

            # Extract text content
            parsed_article['text'] = self.extract_text(article)

            # Extract images
            parsed_article['images'] = self.extract_images(article)

        except Exception as e:
            print(f"Error parsing article: {e}")
            return None  # Skip this article if any part fails to parse correctly

        return parsed_article if parsed_article['text'] or parsed_article['images'] else None

    def expand_hidden_text(self, article):
        '''
        Clicks 'See more' if they exist within an article.
        '''
        see_more_buttons = article.find_elements(By.XPATH,
            './/div[@role="button" and contains(text(), "See more")]')

        for button in see_more_buttons:
            button.click()

    def extract_text(self, article):
        '''
        Extracts text from the article.
        '''

        message_element = article.find_element(By.CSS_SELECTOR,
            'div[data-ad-comet-preview="message"]')

        return message_element.text if message_element else ""

    def extract_images(self, article):
        '''
        Extracts all image URLs from the article.
        '''

        image_urls = []
        image_element_containers = article.find_elements(By.CSS_SELECTOR, 'a')
        for container in image_element_containers:
            try:
                image = container.find_element(By.CSS_SELECTOR, 'img')

                if image:
                    src = image.get_attribute("src")
                    if src:
                        image_urls.append(src)
            except Exception:
                continue # No image in this container

        return image_urls
