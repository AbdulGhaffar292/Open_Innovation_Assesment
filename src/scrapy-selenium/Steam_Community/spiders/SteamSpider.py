import scrapy
import time
from scrapy_selenium import SeleniumRequest

class SteamSpider(scrapy.Spider):
    name = "steam_spider"
    start_url = 'https://steamcommunity.com/market/search?q='
    
 
    
    def start_requests(self):
       
       link = "https://steamcommunity.com/market/search?q="
       yield SeleniumRequest( url=link, callback=self.parse)
  

    def parse(self,response):

        products = response.xpath('//div[@id="searchResultsRows"]/a/@href').getall()
        for prod in products:
            yield SeleniumRequest( url=prod, callback=self.parse_Products)

        for page_num in range(2, 52):
            time.sleep(10)  # Start from page 2, end at page 51
            next_page = f'https://steamcommunity.com/market/search?q=#p{page_num}_popular_desc'
            print("****************************")
            print(next_page)
            print("*next_page****")
            print("****************************")
            yield SeleniumRequest(url=next_page, callback=self.parse)

    def parse_Products(self,response):
        item = {}
        
        item['Product_Name'] = self.parse_Product_Name(response)
        item['Bid_price'] = self.parse_Bid_price(response)
        item['Buy_Offer'] = self.parse_Buy_Offer(response)
        item['Ask_price'] = self.parse_Ask_price(response)
        item['Sale_Offer'] = self.parse_Sale_Offer(response)
        item['product_url']  = response.url
        yield item



    def parse_Product_Name(self, response):
        name = response.xpath('//h1[@class="hover_item_name"]/text()').get()
        return name
    
    def parse_Bid_price(self, response):
        try:
            Bid_price = response.xpath('//div[@id="market_commodity_forsale_table"]/table/tbody/tr[position() = last()]/td[1]/text()').get()
            Bid_price = Bid_price.replace('or more','').strip()
            return Bid_price
        except:
            Bid_price = ""
            return Bid_price
        

    def parse_Buy_Offer(self, response):
        Buy_Offer = response.xpath('//div[@id="market_commodity_forsale_table"]/table/tbody/tr[position() = last()]/td[2]/text()').get()
        return Buy_Offer

    def parse_Ask_price(self, response):
        try:
            Ask_price = response.xpath('//div[@id="market_commodity_buyreqeusts_table"]/table/tbody/tr[position() = last()]/td[1]/text()').getall()
            Ask_price = Ask_price.replace('or less','').strip()
            return Ask_price
        except:
            Ask_price = ""
            return Ask_price
    
    def parse_Sale_Offer(self, response):
        Sale_Offer = response.xpath('//div[@id="market_commodity_buyreqeusts_table"]/table/tbody/tr[position() = last()]/td[2]/text()').getall()
        return Sale_Offer

     
    
   