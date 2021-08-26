import scrapy


class OsCollectionSpider(scrapy.Spider):
    name = 'os-collection'
    allowed_domains = ['opensea.io']
    start_urls = ['https://opensea.io/collection/art-blocks']

    def start_requests(self):
        return [scrapy.FormRequest("http://www.example.com/login",
                                   formdata={'user': 'john', 'pass': 'secret'},
                                   callback=self.logged_in)]

    def parse(self, response):
        pass
