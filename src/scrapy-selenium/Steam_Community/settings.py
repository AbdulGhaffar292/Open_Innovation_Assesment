# Scrapy settings for steam_spider project
BOT_NAME = 'steam_spider'

SPIDER_MODULES = ['steam_spider.spiders']
NEWSPIDER_MODULE = 'steam_spider.spiders'

BOT_NAME = "Steam_Community"

SPIDER_MODULES = ["Steam_Community.spiders"]
NEWSPIDER_MODULE = "Steam_Community.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# MongoDB settings
MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = 'steam_market'

# Enable item pipelines
ITEM_PIPELINES = {
    'steam_spider.pipelines.SteamSpiderPipeline': 300,
}

# Configure user-agent and download delay
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True
