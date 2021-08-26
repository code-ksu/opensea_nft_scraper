import scrapy
import urllib
import json
import math
from opensea.items import NFT


class OsCollectionSpider(scrapy.Spider):
    name = 'os-collection'
    allowed_domains = ['opensea.io']
    start_urls = ['https://opensea.io/collection/art-blocks']
    page_limit = 50

    def start_requests(self):
        return self.parse_os_assets(self, offset=0 - self.page_limit)

    def parse_os_assets(self, response = None, offset = 0, collection = 'art-blocks'):
        hasNext = True
        if (response != None):
            assets = json.load(response.body).assets
            hasNext = len(assets) == self.page_limit
            for asset in assets:
                yield self.parse_os_asset(self, response, asset)

        if (hasNext):
            url = "https://api.opensea.io/api/v1/assets"
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
                cb_kwargs=dict(offset=new_offset)
            )


    def parse_os_asset(self, response, os_item):
        # calculate the USD price
        amount = os_item.last_sale.total_price
        usd = os_item.last_sale.payment_token.usd_price
        decimals = os_item.last_sale.payment_token.decimals
        latest_price = amount / math.pow(10, decimals) * usd

        nft = NFT(
            os_id = os_item.id,
            token_id = os_item.token_id,
            name = os_item.name,
            description = os_item.description,
            image_url = os_item.image_url,
            image_original_url = os_item.image_original_url,
            animation_original_url = os_item.animation_original_url,
            external_link = os_item.external_link,
            permalink = os_item.permalink,
            collection_slug = os_item.collection.slug,
            creator = os_item.creator.user.username,
            latest_sale_usd = latest_price
        )
        # TODO: follow website
        # TODO: parse follower
        pass

    def unexpected_response(self, response):
        page = response.url.split("/")[-2]
        filename = f'data/error-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved error page {response.url} to {filename}')