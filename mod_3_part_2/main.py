import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from itemadapter import ItemAdapter

class QuoteItem(Item):
    quote = Field()
    author = Field()
    tags = Field()

class AuthorItem(Item):
    fullname = Field()
    born_date = Field()
    born_location = Field()
    description = Field()

class DataPipeLine:
    quotes = []
    authors = []

    def process_item(self, item, spider):  #filling up the lists with parse information
        adapter = ItemAdapter(item)
        if "fullname" in adapter.keys():
            self.authors.append(dict(adapter))
        elif "quote" in adapter.keys():
            self.quotes.append(dict(adapter))
        return item                                                 # Must return item

    def close_spider(self, spider): #to write the collected data to files
        with open('quotes.json', 'w', encoding='utf-8') as fd:
            json.dump(self.quotes, fd, ensure_ascii=False, indent=2)
        with open('authors.json', 'w', encoding='utf-8') as fd:
            json.dump(self.authors, fd, ensure_ascii=False, indent=2)

class QuotesSpider(scrapy.Spider):
    name = "get_quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com/"]
    custom_settings = {"ITEM_PIPELINES": {DataPipeLine: 300}}

    def parse(self, response):
        for q in response.xpath("//div[@class='quote']"):
            quote = q.xpath("span[@class='text']/text()").get().strip()
            author = q.xpath("span/small[@class='author']/text()").get().strip()
            tags = q.xpath("div[@class='tags']/a/text()").extract()

            yield QuoteItem(tags=tags, author=author, quote=quote)

            author_link = q.xpath("span/a/@href").get()
            if author_link:
                yield response.follow(author_link, callback=self.parse_author)

        # for moving to next pages fix link
        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield response.follow(url=response.urljoin(next_link), callback=self.parse)

    def parse_author(self, response): #parsing the authors information
        content = response.xpath("//div[@class='author-details']")
        fullname = content.xpath("h3[@class='author-title']/text()").get().strip()
        born_date = content.xpath("p/span[@class='author-born-date']/text()").get().strip()
        born_location = content.xpath("p/span[@class='author-born-location']/text()").get().strip()
        description = content.xpath("div[@class='author-description']/text()").get().strip()

        yield AuthorItem(fullname=fullname, born_date=born_date, born_location=born_location, description=description)

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()
