import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from pymongo import MongoClient
import os

def set_undetected_chrome_browser_options() -> Options:

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--no-sandbox")  # Required for Docker
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration

    driver = uc.Chrome(options=chrome_options)
    return driver

def create_chrome_web_driver(user_agent, proxy=None):
    # Create ChromeOptions object
    chrome_options = uc.ChromeOptions()
    
    # Set desired options
    chrome_options.add_argument(f"user-agent={user_agent}")
    
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    
    # Use undetected_chromedriver to create a Chrome driver with the specified options
    driver = uc.Chrome(options=chrome_options)
    return driver

def scrape_products_page(driver, product_links):
    try:
        products = driver.find_elements(By.XPATH, '//div[@id="searchResultsRows"]/a')
        if not products:
            print("Products not found on this page.")
        for product in products:
            product_link = product.get_attribute('href')
            print(f"Found product link: {product_link}")
            product_links.append(product_link)
    except NoSuchElementException:
        print("Error: Products not found on this page.")

def scrape_product_details(driver, product_url):
    retries = 3
    for attempt in range(retries):
        try:
            driver.get(product_url)
            time.sleep(5)

            Product_name = 'N/A'
            Bid_price = 'N/A'
            Buy_Offer = 'N/A'
            Ask_price = 'N/A'
            Sale_Offer = 'N/A'
            
            try:
                Product_name = driver.find_element(By.XPATH, '//h1[@class="hover_item_name"]').text
            except NoSuchElementException:
                print(f"Product name not found for {product_url}")

            try:
                Bid_price = driver.find_element(By.XPATH, '//div[@id="market_commodity_forsale_table"]/table/tbody/tr[position() = last()]/td[1]').text.replace('or more','').strip()
            except NoSuchElementException:
                print(f"Bid price not found for {product_url}")

            try:
                Buy_Offer = driver.find_element(By.XPATH, '//div[@id="market_commodity_forsale_table"]/table/tbody/tr[position() = last()]/td[2]').text
            except NoSuchElementException:
                print(f"Buy Offer not found for {product_url}")

            try:
                Ask_price = driver.find_element(By.XPATH, '//div[@id="market_commodity_buyreqeusts_table"]/table/tbody/tr[position() = last()]/td[1]').text.replace('or less','').strip()
            except NoSuchElementException:
                print(f"Ask price not found for {product_url}")

            try:
                Sale_Offer = driver.find_element(By.XPATH, '//div[@id="market_commodity_buyreqeusts_table"]/table/tbody/tr[position() = last()]/td[2]').text
            except NoSuchElementException:
                print(f"Sale Offer not found for {product_url}")

            if Product_name and Product_name != 'N/A':
                print(f"Product Scraped Details: {Product_name}, {Bid_price}, {Buy_Offer}, {Ask_price}, {Sale_Offer}, {product_url}")
                return {
                    'product name': Product_name,
                    'Bid price': Bid_price,
                    'Buy Offer': Buy_Offer,
                    'Ask price': Ask_price,
                    'Sale Offer': Sale_Offer,
                    'product url': product_url
                }
            else:
                print(f"Skipped: {product_url} (Product name not found)")
                return None
        except (NoSuchElementException, WebDriverException) as e:
            print(f"Error scraping {product_url}: {e}")
            if attempt < retries - 1:
                wait_time = random.uniform(2, 5)
                print(f"Retrying to scrap in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Product Failed to scraped {product_url} after {retries} attempts.")
                return None

def save_to_csv(data, csv_file='Stream_Community_Data.csv'):
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False)
    print(f"Data has been saved to {csv_file}.")

def save_to_mongodb(data, db_name='steam_community', collection_name='products'):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_many(data)
    print(f"Data has been saved to MongoDB collection '{collection_name}'.")

if __name__ == "__main__":
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    ]

    proxies = [
        "http://proxy1:port",
        "http://proxy2:port",
    ]

    user_agent = random.choice(user_agents)
    proxy = random.choice(proxies) if proxies else None

    driver = create_chrome_web_driver(user_agent)
    url = "https://steamcommunity.com/market/search?q="
    driver.get(url)
    time.sleep(10)

    product_data = []
    product_links = []
    for page in range(1, 51):
        print(f"Scraping page {page}")
        scrape_products_page(driver, product_links)

        time.sleep(random.uniform(3, 7))

        try:
            next_button = driver.find_element(By.XPATH, '//div[@id="searchResults_controls"]/span[@id="searchResults_btn_next"]')
            next_button.click()
            time.sleep(2)
        except NoSuchElementException:
            print(f"No more pages found at page {page}")
            break

        user_agent = random.choice(user_agents)
        proxy = random.choice(proxies) if proxies else None
        driver.quit()
        
        driver = create_chrome_web_driver(user_agent)

    print(f"Total product links scraped: {len(product_links)}")

    for link in product_links:
        product_details = scrape_product_details(driver, link)
        if product_details:
            product_data.append(product_details)

    save_to_csv(product_data)
    save_to_mongodb(product_data)

    driver.quit()
