import scrapy

class DentalItem(scrapy.Item):
    product_title = scrapy.Field()
    product_price = scrapy.Field()
    path_to_image = scrapy.Field()
    image_url = scrapy.Field()

