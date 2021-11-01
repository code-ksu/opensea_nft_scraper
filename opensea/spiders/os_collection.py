import scrapy
import urllib
import math
import requests
import re
from os import getcwd
from pathlib import Path
from ..items import NFT


class OsCollectionSpider(scrapy.Spider):
    name = 'os-collection'
    allowed_domains = ['opensea.io']
    start_urls = ['https://opensea.io/collection/art-blocks']
    page_limit = 5
    file_ext_regex = re.compile(r'^.+\.\w{2-8}$')

    def start_requests(self):
        return self.get_assets()

    def get_assets(self, response = None, offset = 0, collection = 'art-blocks-factory'):
        hasNext = True
        if (response != None):
            json_content = response.json()
            assets = json_content['assets']
            hasNext = len(assets) == self.page_limit
            for asset in assets:
                yield self.get_asset_details(asset)

        if (hasNext):
            url = "https://api.opensea.io/api/v1/assets?"
            data = {
                "order_direction": "desc",
                "offset": offset,
                "limit": str(self.page_limit), # max
                # "collection": collection
            }

            url += urllib.parse.urlencode(data)
            new_offset = offset + self.page_limit

            yield scrapy.Request(
                url,
                callback=self.get_assets,
                cb_kwargs=dict(offset=new_offset),
                headers=dict(Accept='application/json'),
                priority=0 # next page = low prio
            )

    def get_asset_details(self, collection_item):
        address = collection_item["asset_contract"]["address"]
        token_id = collection_item["token_id"]
        url = f'https://api.opensea.io/api/v1/asset/{address}/{token_id}'

        return scrapy.Request(
            url,
            callback=self.parse_asset,
            cb_kwargs=dict(collection_item=collection_item),
            headers=dict(Accept='application/json'),
            priority=1 # asset details = high prio!
        )


    def parse_asset(self, response, collection_item): # do we need collection_item ?
        item = response.json()
        print(item)

        if collection_item['id'] != item['id']:
            print("MISMATCHING ID!")

        # calculate the USD price
        latest_price = self.calc_price_sale(item['last_sale'])
        sell_order_usd = self.calc_price_order(item['sell_orders'])
        buy_order_usd = self.calc_price_order(item['orders'])

        # skip when no price was offered AND no sale ever happend
        if latest_price == None and buy_order_usd == None:
            self.log(f'skipping cuz no price')
            #return None

        print(f'latest price: {str(sell_order_usd)} | seller: {sell_order_usd} | offer: {buy_order_usd} ')

        creator = item['creator']['address']
        if item['creator']['user']:
            creator = item['creator']['user']['username']

        nft = NFT(
            # meta
            os_id = item['id'],
            token_id = item['token_id'],
            name = item['name'],
            description = item['description'],
            external_link = item['external_link'],
            permalink = item['permalink'],
            collection_slug = item['collection']['slug'],
            creator = creator,
            is_animation = item['animation_original_url'] != None,
            #content
            image_preview_url = item['image_preview_url'],
            image_url = item['image_url'],
            image_original_url = item['image_original_url'],
            animation_original_url = item['animation_original_url'],
            # price
            latest_sale_usd = latest_price,
            sell_order_usd = sell_order_usd,
            buy_order_usd = buy_order_usd,
        )

        #dl
        try:
            self.save_file(nft['os_id'], nft['image_original_url'], 'img')
        except:
            self.save_file(nft['os_id'], nft['image_url'], 'img')
        self.save_file(nft['os_id'], nft['image_preview_url'], 'preview')

        # TODO: follow website: artblock / medium

        # TODO: parse follower
        telegram = item['collection']['telegram_url']
        twitter = item['collection']['instagram_username']
        instagram = item['collection']['instagram_username']
        wiki = item['collection']['wiki_url']

        #request = self.get_social(None, nft, telegram, twitter, instagram, wiki)

        #if (request == None):
        return nft
        # else:
        #     yield request

    #### SOCIAL

    def get_social(self, response, nft, telegram, twitter, instagram, wiki):
        tg_url = telegram
        tw_url = twitter
        ig_url = instagram
        wk_url = wiki
        if response != None:
            nft = response.meta["nft"]
            tg_url = response.meta["telegram"]
            tw_url = response.meta["twitter"]
            ig_url = response.meta["instagram"]
            wk_url = response.meta["wiki"]

        url = None
        if tg_url != None:
            url = tg_url
            tg_url = None

        if tw_url != None:
            url =  f'https://twiter.com/{tw_url}'
            tw_url = None

        if ig_url != None:
            url = f'https://instagram.com/{ig_url}'
            ig_url = None

        if wk_url != None:
            url = wk_url
            wk_url = None

        if url != None:
            request = scrapy.Request(
                url,
                callback=self.get_social,
                priority=2 # asset details = high prio!
            )
            request.meta["nft"] = nft
            if tg_url != None:
                request.meta["telegram"] = tg_url
            elif tw_url != None:
                request.meta["twitter"] = tw_url
            elif ig_url != None:
                request.meta["instagram"] = ig_url
            elif wk_url != None:
                request.meta["wiki"] = wk_url
        else:
            return nft

        if response == None:
            return request
        else:
            yield request

    # def parse_insta(reponse):
    # def parse_telegram(reponse):
    # def parse_twitter(reponse):


    #### PRICES

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

    #### DOWNLOAD

    def save_file(self, os_id, url, subfolder):
        filename = url.split('/')[-1]
        if self.file_ext_regex.search(filename) == None:
            filename = 'noext.png'

        path = Path(getcwd())
        filename = path.joinpath('data', subfolder, f'{os_id}_{filename}')
        r = requests.get(url)
        with open(filename,'wb') as output_file:
            output_file.write(r.content)

        self.log(f'Saved image {filename}')

        
    #### ERROR 

    def unexpected_response(self, response):
        page = response.url.split("/")[-2]
        filename = Path().joinpath('data', f'error-{page}.html')
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved error page {response.url} to {filename}')