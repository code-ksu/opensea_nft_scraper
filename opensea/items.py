# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class NFT(Item):
    # meta
    os_id = Field()
    token_id = Field()
    name = Field()
    description = Field()
    external_link = Field()
    permalink = Field()
    collection_slug = Field()
    creator = Field()
    is_animation = Field()
    # content
    image_preview_url = Field()
    image_url = Field()
    image_original_url = Field()
    animation_original_url = Field()
    # price
    latest_sale_usd = Field()
    sell_order_usd = Field()
    buy_order_usd = Field()
    # social
    instagram_follower = Field()
    twitter_follower = Field()
    medium_follower = Field()
    telegram_follower = Field()
    wiki_exists = Field()

