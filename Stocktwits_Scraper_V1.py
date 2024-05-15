import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import warnings

#--------------------------------------------------------------
warnings.simplefilter(action='ignore', category=FutureWarning)

driver = webdriver.Chrome()
tkr = 'MSFT'

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
stop_date = '2024-01-01'

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


