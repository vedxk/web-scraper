from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.scrape_spider import DentalSpider
from typing import Union
from multiprocessing import Process, Queue
import configparser

# FastAPI instance
app = FastAPI()

class ScrapeRequest(BaseModel):
    start_page: int
    end_page: int
    proxy: Union[str, None]

class Product(BaseModel):
    product_title: str
    product_price: str
    path_to_image: str

class SpiderRunner:
    def run_spider(self, start_page, end_page, proxy, q):
        try:
            settings = get_project_settings()
            process = CrawlerProcess(settings)
            process.crawl(DentalSpider, start_page=start_page, end_page=end_page, proxy=proxy)
            process.start()
            q.put("completed")
        except Exception as e:
            q.put(f"failed: {str(e)}")

class TokenVerifier:
    # Token configuration for static token(hardcoded)
    config = configparser.ConfigParser()
    config.read('config.ini')

    STATIC_TOKEN = config['DEFAULT']['STATIC_TOKEN']
    def verify_token(self, request: Request):
        token = request.headers.get('Authorization')
        if token != self.STATIC_TOKEN:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
spider_runner = SpiderRunner()
token_verifier = TokenVerifier()

@app.post("/scrape", dependencies=[Depends(token_verifier.verify_token)])
def scrape(scrape_request: ScrapeRequest):
    start_page = scrape_request.start_page
    end_page = scrape_request.end_page
    proxy = scrape_request.proxy

    q = Queue()
    p = Process(target=spider_runner.run_spider, args=(start_page, end_page, proxy, q))
    p.start()
    p.join()
    result = q.get()

    if result != "completed":
        raise HTTPException(status_code=500, detail=f"Scraping failed: {result}")