!pip install sqlalchemy beautifulSoup4 selenium requests

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from sqlalchemy import create_engine

url = "https://www.aliexpress.com/?src=google&albch=fbrnd&acnt=450-156-4625&isdl=y&aff_short_key=UneMJZVf&albcp=2042458462&albag=71343543599&slnk=&trgt=kwd-14802285088&plac=&crea=619144571406&netw=g&device=c&mtctp=e&memo1=&albbt=Google_7_fbrnd&aff_platform=google&albagn=888888&isSmbActive=false&isSmbAutoCall=false&needSmbHouyi=false&gad_source=1&gclid=Cj0KCQjwtsy1BhD7ARIsAHOi4xbIEXwhBSjq_BOkmoQRXrTfeAqVgXAbrT9UDcXuU4ns9rUJx7dWD1QaAueTEALw_wcB"
r = requests.get(url)

print(r)

# configure Selenium ChromeDriver Options
options = Options()
Options.headless = True
service = Service(executable_path='chromedriver-win64\chromedriver.exe')

# initialize the webdriver
driver = webdriver.Chrome(service=service, options=options)

#Define the URL
url = "https://www.aliexpress.com/?src=google&albch=fbrnd&acnt=450-156-4625&isdl=y&aff_short_key=UneMJZVf&albcp=2042458462&albag=71343543599&slnk=&trgt=kwd-14802285088&plac=&crea=619144571406&netw=g&device=c&mtctp=e&memo1=&albbt=Google_7_fbrnd&aff_platform=google&albagn=888888&isSmbActive=false&isSmbAutoCall=false&needSmbHouyi=false&gad_source=1&gclid=Cj0KCQjwtsy1BhD7ARIsAHOi4xbIEXwhBSjq_BOkmoQRXrTfeAqVgXAbrT9UDcXuU4ns9rUJx7dWD1QaAueTEALw_wcB"

#Use selenium to open the page

#Wait for the dynamic content to load
time.sleep(10)

#Get the page source and close the browser
page_source = driver.page_source
driver.quit()

# configure Selenium ChromeDriver Options
options = Options()
Options.headless = True
service = Service(executable_path='chromedriver-win64\chromedriver.exe')

# initialize the webdriver
driver = webdriver.Chrome(service=service, options=options)

# Initialize WebDriver (Assuming you have set up WebDriver correctly)
driver = webdriver.Chrome()

# Lists to store extracted data
product_names = []
prices = []
store_names = []
store_links = []
shipping_prices = []
extra_discounts = []
item_sold = []
original_prices = []
shipping_free_statuses = []

# Assuming you know the total number of pages
total_pages = 5  # Set total pages as required
for page_number in range(1, total_pages + 1):
    url = f"https://www.aliexpress.com/w/wholesale-duvet-cover-.html?page={page_number}&g=y&SearchText=duvet+cover+"

    driver.get(url)
    time.sleep(30)

    # Parse the loaded page_source
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Adjust the class selectors based on the current website structure
    duvet_king_size = soup.find_all('div', class_='list--gallery--C2f2tvm search-item-card-wrapper-gallery')

    for duvet in duvet_king_size:
        # product_name
        product_name = duvet.find('h3', class_='multi--titleText--nXeOvyr').text

        # prices
        price = duvet.find('div', class_='multi--price-sale--U-S0jtj').text
        # or in a situation where you want to remove the curency icon use 
        #prices = duvet.find('div', class_='multi--price-sale--U-S0jtj').text.replace('$', '').replace(',', '')

        # store_name
        store_name = duvet.find('a', class_='cards--storeLink--XkKUQFS').text

        # store_link
        try:
            store_link = duvet.find('a', class_='cards--storeLink--XkKUQFS')['href']
        except (TypeError, KeyError):
            store_link = ''

        # shipping_price
        try:
            shipping_price = duvet.find('span', class_= 'tag--text--1BSEXVh tag--textStyle--3dc7wLU multi--serviceStyle--1Z6RxQ4').text
        except AttributeError:
            shipping_price = ''

        # extra_discount
        try:
            extra_discount = duvet.find('span', class_='tag--text--1BSEXVh tag--textStyle--3dc7wLU multi--superStyle--1jUmObG').text
        except AttributeError:
            extra_discount = ''

        # item_sold
        try:
            item_sold_text = duvet.find('span', class_='multi--trade--Ktbl2jB').text
            items_sold_value = item_sold_text.split()[0] if item_sold_text else ''
        except AttributeError:
            items_sold_value = ''

        # Append data to list
        product_names.append(product_name)
        prices.append(price)
        store_names.append(store_name)
        store_links.append(store_link)
        shipping_prices.append(shipping_price)
        extra_discounts.append(extra_discount)
        item_sold.append(items_sold_value)

        # extracting additional information
        former_price = duvet.find_all('div', class_='multi--price-original--1zEQqOK')
        original_prices.append(former_price[0].text if former_price else '')

        free_shipping = duvet.find_all('span', class_='tag--text--1BSEXVh tag--textStyle--3dc7wLU multi--serviceStyle--1Z6RxQ4')
        ship_free = free_shipping[0].text.strip() if free_shipping else ''
        shipping_free_statuses.append(ship_free)

# Once all the pages' information is extracted, quit the driver
driver.quit()

# Create DataFrame
data = {
    'product_name': product_names,
    'price': prices,
    'store_name': store_names,
    'store_link': store_links,
    'shipping_price': shipping_prices,
    'extra_discount': extra_discounts,
    'item_sold': item_sold,
    'original_price': original_prices,
    'shipping_free_status': shipping_free_statuses
}

df = pd.DataFrame(data)
# display dataframe
display(df.head())

# save the raw data
df.to_csv('Aliexpressduvetcover.csv', index=False)

# Products table
product_columns = ['product_name', 'price', 'store_name', 'store_link']
#products = df[product_columns].copy()
# How to drop duplicates
products = df[product_columns].copy().drop_duplicates().reset_index(drop=True)

# create product id
products.index.name = 'product_id'
products = products.reset_index()

# Discount table
discount_columns = ['product_name', 'price', 'original_price', 'extra_discount']
discounts = df[discount_columns].copy()

# discount id
discounts.index.name = 'discount_id'
discounts = discounts.reset_index()

# removing currency symbols and commas then convert to float
discounts['original_price'] = discounts['original_price'].str.replace('￡', '').str.extract('(/d+)%').astype(float)

# extract discount percent value and coin percent value as integer
discounts['extra_discount'] = discounts['extra_discount'].str.extract('(/d+)%').astype(float) 

# filling up missing values
discounts.fillna({
    'original_price': 0.0,
    'extra_discount': 0.0,
}, inplace=True)

discounts

#Sales Table
sales_column = ['product_name','price', 'item_sold',]
sales = df[sales_column].copy()

# sales id
sales.index.name = 'sales_id'
sales = sales.reset_index()

sales

#Shipping Table
shipping_column = ['product_name','shipping_price', 'shipping_free_status']
shipping = df[shipping_column].copy()

# sales id
shipping.index.name = 'shipping_id'
shipping = shipping.reset_index()

# for replacing string with float
# filling up missing values
shipping.fillna({
    'shipping_price': 0.0,
    'shipping_free_status': 0.0,
}, inplace=True)

shipping

# saving to csv file
products.to_csv('products.csv', index=False)
discounts.to_csv('discounts.csv', index=False)
sales.to_csv('sales.csv', index=False)
shipping.to_csv('shipping.csv', index=False)

from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

db_params = {
    'username': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_DATABASE')
}

# Define db url connection using db parameters
db_url = f"postgresql://{db_params['username']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"

# Create database engine
engine = create_engine(db_url)

# Connect to the PostgreSQL server
with engine.connect() as connection:
    # Create tables and load data
    products.to_sql('products', connection, index=False, if_exists='replace')
    discounts.to_sql('discounts', connection, index=False, if_exists='replace')
    sales.to_sql('sales', connection, index=False, if_exists='replace')
    shipping.to_sql('shipping', connection, index=False, if_exists='replace')

print('Database, table, and data loaded successfully')