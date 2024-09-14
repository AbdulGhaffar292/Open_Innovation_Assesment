# Open Innovation Assessment

This repository contains two projects:

1. **Selenium Project**: A web scraping project using Selenium with Python.
2. **Scrapy-Selenium Project**: A web scraping project using the Scrapy framework with Selenium.

## Features

### Selenium Project

- Stores data in CSV files.
- Stores data in MongoDB.

### Scrapy-Selenium Project

- Stores data in MongoDB.
- Optionally saves data in JSON files.

## Installation

### Selenium Project

1. Ensure you have Python installed.
2. Navigate to the `selenium/` directory.
3. Install the required libraries by running:

   ```bash
   pip install -r requirements.txt
    ```
### Scrapy-Selenium Project

1. Ensure you have Python installed.
2. Install Scrapy using pip:
    ```bash
    pip install scrapy 
    ```
3. Install Selenium if it's not already installed:
    ```bash
    pip install selenium
    ```
## How to Run
### Selenium Project
1. Navigate to the selenium/ directory.
2. Run the script:
    ```bash
    python main.py
    ```
### Scrapy-Selenium Project
1. Navigate to the scrapy-selenium/ directory.
2. To run the spider and save data in MongoDB (default behavior), use:
    ```bash
    scrapy crawl steam_market
    ```
3. To run the spider and save data in a JSON file, use:
    ```bash
    scrapy crawl steam_market -o output.json
    ```
 