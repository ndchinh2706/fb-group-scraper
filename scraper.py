# pylint: disable=broad-exception-caught disable=broad-exception-raised
'''
Provides all the utils to scrape the data
'''

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
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

    def bypass_cookie_dialog(self):
        '''
        Check if there is a popup to accept the cookies
        if so, we press the decline optional cookies
        '''

        dialogs = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="dialog"]')

        found = False
        for dialog in dialogs: # There may be more than one dialog

            try:
                button = dialog.find_element(By.CSS_SELECTOR,
                    'div[aria-label="Decline optional cookies"]')

                if button:
                    found = True
                    button.click()
                    break
            except Exception:
                pass # Button isn't in this dialog

        if not found and len(dialogs) > 0:
            raise Exception("Could not find a \"Decline Cookies\" button in the cookies popup.")

    def bypass_login_dialog(self):
        '''
        Check if there is a popup to login
        if so, we press the X icon at the top right corner
        '''

        dialogs = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="dialog"]')

        found = False
        for dialog in dialogs: # There may be more than one dialog

            try:
                button = dialog.find_element(By.CSS_SELECTOR,
                    'div[aria-label="Close"] i')

                if button:
                    found = True
                    button.click()
                    break
            except Exception:
                pass # Button isn't in this dialog

        if not found and len(dialogs) > 0:
            raise Exception("Could not find a close button in the login popup.")

    def fetch_articles(self):
        '''
        Fetch the main content
        The HTML is a mess so we can use the loading element
        and find what we want through its parents
        '''

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

    def scroll_page(self, pixels):
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

        auth_prompt = self.driver.find_element(By.CSS_SELECTOR, 'div[data-nosnippet=""]')

        self.driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, auth_prompt)

    def fetch_html(self, url):
        '''
        Fetch the html with the posts content from the DOM
        '''
        self.driver.get(url)

        # Bypass cookies dialog if it is displayed
        self.bypass_cookie_dialog()

        # Close page login dialog
        self.bypass_login_dialog()

        # Remove auth prompt
        self.remove_login_annoynace()

        # Scroll the page to load the articles
        self.scroll_page(1000)

        # Wait for posts to load
        time.sleep(5)

        # Fetch a clean article list
        return self.fetch_articles()

    def parse_article_html(self, articles):
        '''
        Parse and structure article HTML elements
        '''

        if not articles:
            raise Exception("The provided articles are invalid")

        parsed_articles = []
        for article in articles:
            try:
                parsed_article = {}

                # Make sure all the text is loaded by pressing see more
                try:
                    see_more_button = article.find_element(By.XPATH,
                        '//div[@role="button" and contains(text(), "See more")]')

                    if see_more_button:
                        see_more_button.click()
                except Exception as e:
                    print(e)
                    #pass # There is no see more in this post

                ##### Fetch message
                article_message = article.find_element(By.CSS_SELECTOR,
                    'div[data-ad-comet-preview="message"]')                

                parsed_article['text'] = article_message.text


                #### Get all the images
                try:
                    # Get image container by following the sibling nearest to the
                    # message article message parent
                    image_container = (article_message.find_element(By.XPATH, '..')
                        .find_element(By.XPATH, 'following-sibling::div'))
                    article_image_containers = image_container.find_elements(By.CSS_SELECTOR, 'a')

                    parsed_article['images'] = []
                    for container in article_image_containers:
                        try:
                            image = container.find_element(By.CSS_SELECTOR, 'img')

                            if image:
                                image_url = image.get_attribute("src")
                                if image_url:
                                    parsed_article['images'].append(image_url)
                        except Exception:
                            continue # No image in this container

                except Exception:
                    pass # There are no images

                # Add article to list
                parsed_articles.append(parsed_article)
            except Exception:
                continue # Invalid article

        return parsed_articles
