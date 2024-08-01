'''
Module that handles all the notification logic
using NTFY
'''

import requests

class Notifier:
    '''
    Holds all the logic to send notifications
    '''

    def __init__(self, ntfy_instance, token = None):
        self.instance_url = ntfy_instance
        self.token = token

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

        keywords = ['QUEM O AVISA', 'locais', 'controlo', 'velocidade', 'radar']

        # Check if any keyword is in the article text
        notification_priority = 3
        if [keyword for keyword in keywords if keyword.lower() in article['text'].lower()]:
            notification_priority = 4

        title = 'New post from PSP Setubal!'
        self.send_notification(title, article['text'], article['images'], notification_priority)
