import scrapy
from items import DentalItem

class DentalSpider(scrapy.Spider):
    name = 'dental_stall'
    allowed_domains = ['dentalstall.com']

    def __init__(self,start_page, end_page, proxy=None, *args, **kwargs):
        super(DentalSpider, self).__init__(*args, **kwargs)
        self.start_page = int(start_page)
        self.end_page = int(end_page)
        self.proxy = proxy
        self.start_urls = [f'https://dentalstall.com/shop/page/{i}/' for i in range(self.start_page, self.end_page + 1)]
    
    def start_requests(self):
        # check the first page to get total number of pages available to scrape
        yield scrapy.Request('https://dentalstall.com/shop/page/1/', callback=self.check_total_pages, meta={'proxy': self.proxy})

    def check_total_pages(self, response):
        total_pages = self.parse_total_pages(response)

        if self.start_page > total_pages:
            self.logger.error(f"Requested pages {self.start_page} to {self.end_page} do not exist. Total available pages: {total_pages}.")
            return
        
        if self.end_page > total_pages:
            self.end_page = total_pages

        self.start_urls = [f'https://dentalstall.com/shop/page/{i}/' for i in range(self.start_page, self.end_page + 1)]
        
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'proxy': self.proxy})

    def parse_total_pages(self, response):
        total_pages = response.css('ul.page-numbers li a.page-numbers::text').re(r'\d+')
        if total_pages:
            return int(total_pages[-1])
        return 1

    def parse(self, response):
        products = response.css('div.product-inner')
        for product in products:
            item = DentalItem()
            try:
                item["product_title"] = product.css("img.attachment-woocommerce_thumbnail::attr(title)").get().strip()
            except Exception as e:
                self.logger.error(f"Error parsing product title: {e}")
                item["product_title"] = None

            try:
                product_price = product.css("span.woocommerce-Price-amount.amount bdi::text").get()
                symbol = product.css('span.woocommerce-Price-currencySymbol::text').get()
                item["product_price"] = symbol + product_price
            except Exception as e:
                self.logger.error(f"Error parsing product price: {e}")
                item["product_price"] = None

            try:
                image_url = product.css("img.attachment-woocommerce_thumbnail::attr(data-lazy-src)").get()
                item['image_url'] = image_url
            except Exception as e:
                self.logger.error(f"Error parsing product image URL: {e}")
                item['image_url'] = None

            yield item





