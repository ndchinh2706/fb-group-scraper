# My fork's to-do list
- [ ] Adding Facebook account login to monitor private Facebook groups.
- [ ] Multiple groups monitoring.
      
# Facebook Group Post Notifier

![fb-group-scraper](https://github.com/user-attachments/assets/ff7c10ef-54ea-4885-a101-b2ec158a1265)


## Introduction

The Facebook Group Post Notifier is a Python application designed to monitor specific Facebook groups for new posts, parse them, and send notifications through NTFY.
<br />
<br />
This tool is especially useful for staying updated with real-time information from Facebook groups without constantly checking the website or having to install the app.

## Project Inspiration

This project was inspired by a personal experience where I received a speeding ticket due to a mobile speed camera set up by the local police. After discussing with an officer, I learned that such setups are often announced in the city's police Facebook group. 
<br />
<br />
To avoid future tickets and stay informed, I created this script to automatically notify me of new posts that might indicate the presence of mobile speed cameras.

## Requirements

- Python 3.x
- Recent version of Firefox installed

## Setup
### Clone the Repository
Cloning the repository to your local machine.

```
git clone https://github.com/RaulRohjans/fb-group-scraper
cd fb-group-scraper
```

### Install Dependencies
Install the required Python libraries using pip.

```
pip install -r requirements.txt
```

## Configuration:
Modify the script arguments as needed.
- `--url`: URL of the Facebook group (default is set to a placeholder).
- `--ntfy-instance`: URL of your NTFY instance including the topic.
- `--ntfy-token`: Authentication token for the NTFY service.

## Usage
To run the script, use the following command:

```
python src/main.py --url "https://www.facebook.com/yourgroup" --ntfy-instance "your_ntfy_url" --ntfy-token "your_ntfy_token"
```

## How It Works
- *Initialization*: The script starts by parsing the provided arguments.
- *Scraping*: Utilizes Selenium to navigate and scrape the Facebook group page.
- *Parsing*: Extracts and processes the content from scraped HTML elements.
- *Database Checking*: Verifies new posts against previously saved ones in the SQLite database to detect new content.
- *Notification*: Sends notifications for new posts, especially those matching predefined keywords with higher priority.

## License
This project is licensed under the MIT License, which permits use, modification, distribution, and private use. This license also allows for sublicensing, providing flexibility for developers to integrate this project into larger works.
