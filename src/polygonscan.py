import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

#setup
date_current = datetime.now()
address = '0x0b83f617ad1b093e071248930366ca447aa81971'
url = f'https://polygonscan.com/txs?a={address}&p='
headers = {'User-Agent': 'Chrome/50.0.2661.102'}
result = requests.get(url, headers=headers)
df = None

def convert_time_to_date(date):
  # Function to convert the string to a date
  parts = date.split()

  if ('day' in date or 'days' in date) and ('hr' in date or 'hrs' in date):
    day = int(parts[0])
    hour = int(parts[2])
    delta_time = timedelta(days=day, hours=hour)
  elif ('day' in date or 'days' in date) and ('min' in date or 'mins' in date):
    day = int(parts[0])
    min = int(parts[2])
    delta_time = timedelta(days=day, minutes=min)
  elif ('hr' in date or 'hrs' in date) and ('min' in date or 'mins' in date):
    hour = int(parts[0])
    min = int(parts[2])
    delta_time = timedelta(hours=hour, minutes=min)
  else:
    min = int(parts[0])
    delta_time = timedelta(minutes=min)

  new_date = date_current - delta_time
    
  return new_date

if result.status_code == 200:
  content = result.content
  soup = BeautifulSoup(content,'html.parser')
  pages = soup.find(class_='page-link text-nowrap')
  pages = pages.find_all('strong')
  pages = int(pages[1].get_text())
  count = 1

  while count <= pages:

    headers = {'User-Agent': 'Chrome/50.0.2661.102'}
    result = requests.get(f'{url}{count}', headers=headers) 
    content = result.content
    soup = BeautifulSoup(content,'html.parser')
    table = str(soup.find(class_='table-responsive mb-2 mb-md-0'))
    table_temp = pd.read_html(table)[0]
    df = pd.concat([df, table_temp], ignore_index=True)
    count += 1

  del df['Unnamed: 0']
  df.rename(columns={'Unnamed: 4': 'Age','Unnamed: 6': 'Action','Unnamed: 9': 'Fee'}, inplace=True)
  df['Date'] = df['Age'].apply(convert_time_to_date)

df.to_csv(f'data/polygonscan-{address}.csv', index=False)


