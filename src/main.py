# pylint: disable=broad-exception-caught disable=broad-exception-raised
'''
Module where main logic is executed, everything since gathering the data
to storing it to notifying the final user
'''

import argparse
from database import db
from notifier import Notifier
from scraper import Scraper, ArticleParser


class Logic:
    '''
    Main class that starts the program execution
    '''

    def __init__(self, url, ntfy_instance, ntfy_token, keywords):
        self.url = url
        self.ntfy_instance = ntfy_instance
        self.ntfy_token = ntfy_token
        self.keywords = keywords

    def send_log(self, message):
        '''
        Sends a log to the console
        Current its just a printf but could be replaced
        with a better alterantive in the future
        '''
        print(message)

    def start(self):
        '''
        Starts the web scraping process, by fetching posts, parsing, storing and notifying
        '''

        self.send_log('Starting, please wait...')

        scraper_instance = Scraper()

        self.send_log('Fetching data from facebook')

        # Get article HTML data
        articles_html = scraper_instance.fetch_html(self.url)

        self.send_log('Feeding the data to the models')

        # Parse HTML into a structured object
        parser = ArticleParser()
        articles = parser.parse_article_html(articles_html)

        self.send_log('Checking if wev\'ve seen this posts before')

        # Check if any of the articles is in the database
        # this will tell us if it has been "seen" or its new
        unsaved_articles = db.get_unsaved_articles(articles)

        self.send_log('Sending notifications about the new posts')

        # Send article notifications
        notifier = Notifier(self.ntfy_instance, self.ntfy_token, self.keywords)
        for article in unsaved_articles:
            notifier.send_article_notification(article)

        self.send_log('Replacing old persistent data')

        # Replace db articles with the new unsaved ones
        db.replace_existing_articles(unsaved_articles)

        print('Execution complete!')


def main():
    '''
    Starts the program execution
    '''

    # Create the parser instance
    parser = argparse.ArgumentParser(description='Process some integers.')

    # Add arguments
    parser.add_argument('--url', type=str, required=False,
                        default='https://www.facebook.com/profile.php?id=100077086791019',
                        help='The URL of the Facebook group to scrape')
    parser.add_argument('--ntfy-instance', type=str, required=True,
                        help='The NTFY instance URL to send notifications, with the topic included')
    parser.add_argument('--ntfy-token', type=str, required=True,
                        help='The authentication token for the NTFY service')
    parser.add_argument('--keywords', type=str, required=False, default="",
                        help='Only posts with at least one of the keywords will be sent ' +
                        'for notification. Enter the keywords separated by semicolons ";" .')

    # Parse arguments
    args = parser.parse_args()

    # Initialize and start main application logic with the provided arguments
    logic = Logic(args.url, args.ntfy_instance, args.ntfy_token, args.keywords)
    logic.start()

if __name__ == '__main__':
    main()
