C:\ProgramData\Miniconda3\Scripts\activate.bat scraping

cd opensea

scrapy crawl os-collection -O ..\data\art-blocks-2021-08-31.json

cd ..