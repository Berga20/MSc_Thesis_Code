import praw
import pandas as pd
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import warnings


class RedditScraper:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(client_id=client_id,
                                  client_secret=client_secret,
                                  user_agent=user_agent)
        
    def scrape_subreddit(self, subreddit_name, keyword, limit=100, time_filter='year', sort='new'):
        subreddit = self.reddit.subreddit(subreddit_name)
        search_results = subreddit.search(keyword, limit=limit, time_filter=time_filter, sort=sort)
        dataset = []
        for submission in search_results:
            utc_datetime = datetime.utcfromtimestamp(submission.created_utc)
            formatted_date = utc_datetime.strftime('%d-%m-%Y %H:%M:%S')
            
            post_data = {
                'title': submission.title,
                'subreddit': subreddit_name,
                'search_keyword': keyword,
                'score': submission.score,
                'num_comments': submission.num_comments,
                'publication_date': formatted_date,
                'url': submission.url,
                'content': submission.selftext,
            }
            dataset.append(post_data)
            time.sleep(1) # Following Reddit API guidelines with a sleep time of 1 second
        
        df = pd.DataFrame(dataset)
        return df
    
class StocktwitsScraper:
    def __init__(self):
        pass

    def scrape_stock(self, tkr, stop_date):
        """
        Args:
            tkr (string): Ticker of the stock whose tweets want to be scraped
            stop_date (string): DATE MUST BE OF FORMAT "YYYY-MM-DD". Insert the date up to which scrape starting from the current day. 

        Returns:
            pd.DataFrame: _description_
        """
        warnings.simplefilter(action='ignore', category=FutureWarning)
        driver = webdriver.Chrome()
        url = f"https://stocktwits.com/symbol/{tkr}"
        driver.get(url)

        time.sleep(3)

        # Accepting Coockies button
        driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()

        time.sleep(2)

        # Closing Invasive Ads Button
        try:
            driver.find_element(By.XPATH, '//*[@id="Layout"]/div[4]/div/div[1]/button').click()
        except:
            pass

        time.sleep(3)

        df = pd.DataFrame(
                {
                'Ticker':[], 
                'User':[], 
                'Date':[], 
                'Message': [], 
        })

        scroll_count = 0
        last_date = datetime.today().strftime('%Y-%m-%d')

        while stop_date < last_date:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            posts = soup.find_all('div', class_ = 'StreamMessage_main__qWCNf')

            for item in posts:
                try:
                    user = item.find('span', {'aria-label': 'Username'}).text
                    message = item.find('div', class_ = 'RichTextMessage_body__4qUeP').text
                    post_date = datetime.strptime(item.find('time', {'aria-label': 'Time this message was posted'}).get('datetime'), '%Y-%m-%dT%H:%M:%SZ').date().strftime('%Y-%m-%d')
                    df = df.append({
                        'Ticker': tkr, 
                        'User': user, 
                        'Date': post_date,
                        'Message': message
                    }, ignore_index=True)
                    last_date = df['Date'].tail(1).values[0]
                except:
                    pass 

            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(3)
            scroll_count += 1
            print(f"Scroll {scroll_count} completed.")

        driver.quit()

        df = df.drop_duplicates(subset='Message')

        return df