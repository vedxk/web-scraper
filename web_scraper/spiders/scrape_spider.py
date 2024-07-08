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
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'proxy': self.proxy})

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





