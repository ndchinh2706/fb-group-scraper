# pylint: disable=broad-exception-caught disable=broad-exception-raised
'''
Module where main logic is executed, everything since gathering the data
to storing it to notifying the final user
'''

from database import db
from notifier import Notifier
from scraper import Scraper, ArticleParser


class Main:
    '''
    Main class that starts the program execution
    '''

    def __init__(self, url, ntfy_instance, ntfy_token):
        self.url = url
        self.ntfy_instance = ntfy_instance
        self.ntfy_token = ntfy_token

    def start(self):
        '''
        Starts the web scraping process, by fetching posts, parsing, storing and notifying
        '''
        scraper_instance = Scraper()

        # Get article HTML data
        articles_html = scraper_instance.fetch_html(self.url)

        # Parse HTML into a structured object
        parser = ArticleParser()
        articles = parser.parse_article_html(articles_html)

        # Check if any of the articles is in the database
        # this will tell us if it has been "seen" or its new
        unsaved_articles = db.get_unsaved_articles(articles)

        # Send article notifications
        notifier = Notifier(self.ntfy_instance, self.ntfy_token)
        for article in unsaved_articles:
            notifier.send_article_notification(article)

        # Replace db articles with the new unsaved ones
        db.replace_existing_articles(unsaved_articles)

        print('Execution complete!')

if __name__ == '__main__':
    URL = 'https://www.facebook.com/profile.php?id=100077086791019'
    NTFY_INSTANCE = 'https://ntfy.rohjans.com/psp-setubal'
    NTFY_TOKEN = 'tk_gxktwesoj2lynjo8hjz5bfa1jga5k'
    # URL = ''

    main = Main(URL, NTFY_INSTANCE, NTFY_TOKEN)
    main.start()
