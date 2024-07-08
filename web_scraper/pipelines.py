import json
import os
import redis
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem
from notification_handler import NotificationHandler

# Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

#Notification handler instance
notification_handler = NotificationHandler()

class ProductCache:
    def __init__(self):
        self.cached_products, self.cached_dict = self.get_cached_data()

    def get_cached_data(self):
        cached_data = redis_client.get('scraped_products')
        if cached_data:
            cached_products = json.loads(cached_data)
            cached_dict = {product['_values']['product_title']: product for product in cached_products}
            return cached_products, cached_dict
        else:
            # Set the 'scraped_products' key to an empty list initially if it doesn't exist
            redis_client.set('scraped_products', json.dumps([]))
            redis_client.set('updated_count', 0)
            return [], {}

class JsonWriterPipeline(object):

    def __init__(self):
        self.updated_count = 0
        self.cache = ProductCache()

    def open_spider(self, spider):
        if not os.path.exists('output'):
            os.makedirs('output')
        if not os.path.exists('output/products.json'):
            with open('output/products.json', 'w', encoding='utf-8') as f:
                f.write('[')
        self.file = open('output/products.json', 'a', encoding='utf-8') 

    def close_spider(self, spider):
        self.file.close()
        # Update Redis with new product data
        serializable_products = []
        for item in self.cache.cached_products:
            if isinstance(item, dict):
                serializable_products.append(item) 
            elif hasattr(item, '__dict__'):
                serializable_products.append(item.__dict__)
            else:
                print(f"Warning: Item {item} is not JSON serializable.")
        redis_client.set('scraped_products', json.dumps(serializable_products))
        redis_client.set('updated_count', self.updated_count)

    def process_item(self, item, spider):
        product_title = item['product_title']
        product_price = item['product_price']

        # Check if product exists in cache
        if product_title in self.cache.cached_dict:
            cached_product = self.cache.cached_dict[product_title]
            if product_price == cached_product['product_price']:
                return item
            else:
                # Update cached product price
                cached_product['product_price'] = product_price
                self.updated_count += 1
                with open('products.json', 'r+') as fwrite:
                    data = json.load(fwrite)
                    for product in data:
                        if product['product_title'] == product_title:
                            product['product_price'] = product_price
        
                    fwrite.seek(0)  
                    json.dump(data, fwrite, indent=4) 
                    fwrite.truncate() 
                return item

        else:
            # Add new product to cache
            self.cache.cached_products.append(item)
            self.cache.cached_dict[product_title] = item
            self.updated_count += 1

        try:
            if not self.file.tell() == 1:  # Check if file is not empty (2 accounts for initial [])
                if self.file.tell() > 0:
                    self.file.seek(self.file.tell() - 1)
                    self.file.truncate()
                    self.file.write(',\n')
                else:
                    self.file.write('[')
            line = json.dumps(dict(item), ensure_ascii=False, indent=4)
            self.file.write(line)
            self.file.write('\n]')
        except Exception as e:
            raise RuntimeError(f"Error writing to file: {e}")

        return item

class MyFilesPipeline(FilesPipeline):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = ProductCache()

    def get_media_requests(self, item, info):
        product_title = item['product_title']
        if product_title in self.cache.cached_dict:
            image_name = item['product_title'].replace('/', '_') + '.jpg'
            item['path_to_image'] = f'images/{image_name}'
            return []
        
        return [Request(item['image_url'], meta={'item': item})]

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        image_name = item['product_title'].replace('/', '_') + '.jpg'
        return f'images/{image_name}'

    def item_completed(self, results, item, info):
        product_title = item['product_title']
        if results:
            item['path_to_image'] = results[0][1]['path']
        elif product_title in self.cache.cached_dict:
            raise DropItem(f"Already scraped {product_title}")
        else:
            raise DropItem(f"Failed to download {item['product_title']}")
        item.pop('image_url', None)
        return item