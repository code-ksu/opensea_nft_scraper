# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class NFT(Item):
    # all from open sea
    os_id = Field()
    token_id = Field()
    name = Field()
    description = Field()
    image_url = Field()
    image_original_url = Field()
    animation_original_url = Field()
    external_link = Field()
    permalink = Field()
    collection_slug = Field()
    creator = Field()
    latest_sale_usd = Field()
    sell_order_usd = Field()
    # social
    instagram_follower = Field()
    twitter_follower = Field()
    medium_follower = Field()

