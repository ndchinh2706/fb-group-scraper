'''
Module that handles all the notification logic
using NTFY
'''

import requests

class Notifier:
    '''
    Holds all the logic to send notifications
    '''

    def __init__(self, ntfy_instance, token, keywords):
        self.instance_url = ntfy_instance
        self.token = token
        self.keywords = keywords

    def send_notification(self, title, message, images, priority = 3):
        '''
        Sends a notificatio through NTFY
        '''

        # Set message priority, title and tags
        headers = {
            'Title': title,
            'X-Priority': str(priority),
            'Tags': 'warning'
        }

        # Set auth headers if NTFY has token authentication
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        # If there are images, add them
        if images and len(images) > 0:
            headers['Attach'] = ','.join(images)

        res = requests.post(self.instance_url, headers=headers, data=message, timeout=120)

        res.raise_for_status()

    def send_article_notification(self, article):
        '''
        Send a notification about an article, by scanning the text
        for some keywords to decide the priority of the message
        '''

        # Check for the existance of keywordd
        # if there are any, only send the notification if the post
        # includes them (and use priority 5), otherwise always send with 3
        title = 'New post detected!'
        if self.keywords:
            parsed_keywords = str(self.keywords).split(";")

            for keyword in parsed_keywords:
                if keyword.lower().strip() in article['text'].lower().strip():
                    self.send_notification(title, article['text'], article['images'], 5)
                    return
        else:
            self.send_notification(title, article['text'], article['images'], 3)
