import time
import random
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from twisted.internet.error import TimeoutError, TCPTimedOutError, DNSLookupError
from twisted.web._newclient import ResponseNeverReceived

class CustomRetryMiddleware(RetryMiddleware):

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1
        max_retries = self.max_retry_times

        if retries <= max_retries:
            #Using Exponential backoff with jitter
            retry_wait = (2 ** retries) + random.uniform(0, 1)  
            spider.logger.info(f"Retrying {request} (failed {retries} times): {reason} in {retry_wait:.2f} seconds")

            time.sleep(retry_wait)
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True

            return retryreq
        else:
            spider.logger.info(f"Gave up retrying {request} (failed {retries} times): {reason}")
            return None

    def process_response(self, request, response, spider):
        if response.status in [500, 502, 503, 504, 522, 524, 408, 429]:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, (TimeoutError, TCPTimedOutError, DNSLookupError, ResponseNeverReceived)):
            return self._retry(request, exception, spider)
        return None
