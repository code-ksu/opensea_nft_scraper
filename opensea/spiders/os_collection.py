import scrapy
import urllib
import json
import math
from ..items import NFT


class OsCollectionSpider(scrapy.Spider):
    name = 'os-collection'
    allowed_domains = ['opensea.io']
    start_urls = ['https://opensea.io/collection/art-blocks']
    page_limit = 50

    def start_requests(self):
        return self.parse_os_assets()

    def parse_os_assets(self, response = None, offset = 0, collection = 'art-blocks'):
        hasNext = True
        if (response != None):
            json_content = response.json()
            assets = json_content['assets']
            hasNext = len(assets) == self.page_limit
            for asset in assets:
                yield self.parse_os_asset(response, asset)

        if (hasNext):
            url = "https://api.opensea.io/api/v1/assets?"
            data = {
                "order_direction": "desc",
                "offset": offset,
                "limit": str(self.page_limit), # max
                "collection": "art-blocks"
            }

            url += urllib.parse.urlencode(data)
            new_offset = offset + self.page_limit

            yield scrapy.Request(
                url,
                callback=self.parse_os_assets,
                cb_kwargs=dict(offset=new_offset),
                headers=dict(Accept='application/json')
            )


    def parse_os_asset(self, response, os_item):
        # calculate the USD price
        latest_price = self.calc_price_sale(os_item['last_sale'])
        sell_order_usd = self.calc_price_order(os_item['sell_orders'])

        nft = NFT(
            os_id = os_item['id'],
            token_id = os_item['token_id'],
            name = os_item['name'],
            description = os_item['description'],
            image_url = os_item['image_url'],
            image_original_url = os_item['image_original_url'],
            animation_original_url = os_item['animation_original_url'],
            external_link = os_item['external_link'],
            permalink = os_item['permalink'],
            collection_slug = os_item['collection']['slug'],
            creator = os_item['creator']['user']['username'],
            latest_sale_usd = latest_price,
            sell_order_usd = sell_order_usd,
        )
        # TODO: follow website
        # TODO: parse follower
        
        return nft

    def calc_price(self, amount, payment_token):
        usd = float(payment_token['usd_price'])
        decimals = float(payment_token['decimals'])
        price = float(amount) / math.pow(10, decimals) * usd
        return price

    def calc_price_sale(self, sale):
        if sale == None:
            return None
        amount = sale['total_price']
        payment_token = sale['payment_token']
        return self.calc_price(amount, payment_token)

    def calc_price_order(self, sale):
        if sale == None or sale[0] == None:
            return None
        amount = sale[0]['current_price']
        payment_token = sale[0]['payment_token_contract']
        return self.calc_price(amount, payment_token)
        

    def unexpected_response(self, response):
        page = response.url.split("/")[-2]
        filename = f'data/error-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved error page {response.url} to {filename}')