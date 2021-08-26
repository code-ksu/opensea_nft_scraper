import scrapy


class OsCollectionSpider(scrapy.Spider):
    name = 'os-collection'
    allowed_domains = ['opensea.io']
    start_urls = ['http://opensea.io/']

    def parse(self, response):
        pass
