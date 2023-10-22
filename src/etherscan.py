from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import requests
import configparser

class Config:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        print(self.config.read(config_file))

    def get_address(self):
        return self.config['ADDRESS']['ERC20']
        
config_file = 'config.ini'
config = Config(config_file)
address = config.get_address()
df = None
count = 1

def get_content(address,count):
    headers = {'User-Agent': 'Chrome/50.0.2661.102'}
    url = f'https://etherscan.io/txs?a={address}&p={count}'
    result = requests.get(url, headers=headers) 
    status = result.status_code
    content = result.content
    soup = BeautifulSoup(content,'html.parser')

    return soup, status

def convert_time_to_date(date):
    # Function to convert the string to a date
    parts = date.split()
    date_current = datetime.now()
    date = date.lower().replace('s', '')
    
    if 'day' in date and 'hr' in date:
        day = int(parts[0])
        hour = int(parts[2])
        delta_time = timedelta(days=day, hours=hour)
    elif 'day' in date and 'min' in date:
        day = int(parts[0])
        min = int(parts[2])
        delta_time = timedelta(days=day, minutes=min)
    elif 'hr' in date and 'min' in date:
        hour = int(parts[0])
        min = int(parts[2])
        delta_time = timedelta(hours=hour, minutes=min)
    else:
        min = int(parts[0])
        delta_time = timedelta(minutes=min)

    new_date = date_current - delta_time

    return new_date
soup, status = get_content(address,count)

if status == 200:
    pages = soup.find('span',class_='page-link text-nowrap')
    try:
        pages = int(pages.get_text().split()[-1])
    except:
        pages = 1 

    while count <= pages:
        soup, status = get_content(address,count)
        table = str(soup.find(class_='table-responsive'))
        table_temp = pd.read_html(table)[0]
        df = pd.concat([df, table_temp], ignore_index=True)
        count += 1

    del df['Unnamed: 0']
    df.rename(columns={'Unnamed: 4': 'Age','Unnamed: 6': 'Action','Unnamed: 9': 'Fee'}, inplace=True)
    df['Date'] = df['Age'].apply(convert_time_to_date)

df.to_csv(f'data/etherscan-{address}.csv', index=False)