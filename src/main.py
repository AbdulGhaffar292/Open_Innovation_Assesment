import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from pymongo import MongoClient

# Define options for WebDriver
def create_driver(user_agent, proxy=None):
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument('--profile-directory=Default')
    opts.add_argument("start-maximized")
    opts.add_argument("disable-infobars")
    opts.add_argument("--lang=en")
    opts.add_argument("--enable-javascript")
    opts.add_argument("--enable-cookies")
    opts.add_argument(f"user-agent={user_agent}")
    opts.headless = False

    if proxy:
        opts.add_argument(f'--proxy-server={proxy}')

    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)

# List of User-Agents and proxies
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    # Add more User-Agents as needed
]

proxies = [
    "http://proxy1:port",
    "http://proxy2:port",
    # Add more proxies as needed
]

# Initialize WebDriver with a random User-Agent and optional proxy
user_agent = random.choice(user_agents)
proxy = random.choice(proxies) if proxies else None

# Comment this line if you are using proxies
driver = create_driver(user_agent)

# un Comment this line if you are using proxies
# driver = create_driver(user_agent, proxy)

# Define URL and initialize variables
url = "https://steamcommunity.com/market/search?q="
driver.get(url)
time.sleep(10)

product_links = []
product_data = []

def scrape_products_on_page():
    try:
        products = driver.find_elements(By.XPATH, '//div[@id="searchResultsRows"]/a')
        for product in products:
            product_links.append(product.get_attribute('href'))
    except NoSuchElementException:
        print("No products found on this page.")

def scrape_product_details(product_url):
    retries = 3
    for attempt in range(retries):
        try:
            driver.get(product_url)
            time.sleep(5)  # Wait for the product page to load

            # Initialize variables with default values
            Product_name = 'N/A'
            Bid_price = 'N/A'
            Buy_Offer = 'N/A'
            Ask_price = 'N/A'
            Sale_Offer = 'N/A'
            
            # Extract product name if available
            try:
                Product_name = driver.find_element(By.XPATH, '//h1[@class="hover_item_name"]').text
            except NoSuchElementException:
                print(f"No product name found for {product_url}")

            # Extract bid price if available
            try:
                Bid_price = driver.find_element(By.XPATH, '//div[@id="market_commodity_forsale_table"]/table/tbody/tr[position() = last()]/td[1]').text.replace('or more','').strip()
            except NoSuchElementException:
                print(f"No Bid price found for {product_url}")

            # Extract buy offer if available
            try:
                Buy_Offer = driver.find_element(By.XPATH, '//div[@id="market_commodity_forsale_table"]/table/tbody/tr[position() = last()]/td[2]').text
            except NoSuchElementException:
                print(f"No Buy Offer found for {product_url}")

            # Extract ask price if available
            try:
                Ask_price = driver.find_element(By.XPATH, '//div[@id="market_commodity_buyreqeusts_table"]/table/tbody/tr[position() = last()]/td[1]').text.replace('or less','').strip()
            except NoSuchElementException:
                print(f"No Ask price found for {product_url}")

            # Extract sale offer if available
            try:
                Sale_Offer = driver.find_element(By.XPATH, '//div[@id="market_commodity_buyreqeusts_table"]/table/tbody/tr[position() = last()]/td[2]').text
            except NoSuchElementException:
                print(f"No Sale Offer found for {product_url}")

            # Check if Product_name is valid and not missing
            if Product_name and Product_name != 'N/A':
                print(f"Scraped: {Product_name}, {Bid_price}, {Buy_Offer}, {Ask_price}, {Sale_Offer}, {product_url}")
                return {
                    'product name': Product_name,
                    'Bid price': Bid_price,
                    'Buy Offer': Buy_Offer,
                    'Ask price': Ask_price,
                    'Sale Offer': Sale_Offer,
                    'product url': product_url
                }
            else:
                print(f"Skipped: {product_url} (No product name found)")
                return None
        except (NoSuchElementException, WebDriverException) as e:
            print(f"Error scraping {product_url}: {e}")
            if attempt < retries - 1:
                wait_time = random.uniform(2, 5)  # Randomize wait time between retries
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed to scrape {product_url} after {retries} attempts.")
                return None

# Scrape product links and details
for page in range(1, 5):
    print(f"Scraping page {page}")
    scrape_products_on_page()

    # Throttle requests to avoid being blocked
    time.sleep(random.uniform(3, 7))  # Randomize delay between page requests

    try:
        next_button = driver.find_element(By.XPATH, '//div[@id="searchResults_controls"]/span[@id="searchResults_btn_next"]')
        next_button.click()
        time.sleep(2)  # Wait for the page to load
    except NoSuchElementException:
        print(f"No more pages found at page {page}")
        break

    # Rotate User-Agent and proxy for each page request
    user_agent = random.choice(user_agents)
    proxy = random.choice(proxies) if proxies else None
    driver.quit()
    
    # Comment this line if you are using proxies
    driver = create_driver(user_agent)

    # un Comment this line if you are using proxies
    # driver = create_driver(user_agent, proxy)

print(f"Total product links scraped: {len(product_links)}")

for link in product_links:
    product_details = scrape_product_details(link)
    if product_details:
        product_data.append(product_details)

# Save the scraped data to MongoDB
def save_to_mongodb(data):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['scraping_db']
    collection = db['steam_community']
    collection.insert_many(data)
    print(f"Data has been saved to MongoDB collection 'steam_community'.")

save_to_mongodb(product_data)

# Uncomment the following code to save data to CSV
# def save_to_csv(data):
#     csv_file = 'scraped_products.csv'
#     df = pd.DataFrame(data)
#     df.to_csv(csv_file, index=False)
#     print(f"Data has been saved to {csv_file}.")

# save_to_csv(product_data)

# Quit the WebDriver session
driver.quit()
