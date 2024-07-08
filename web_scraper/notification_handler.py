import redis

class NotificationHandler:
    def __init__(self):
        self.updated_count = 0
    
    def send_notification(self, updated_count: int):
        self.updated_count = updated_count
        return f"Scraping completed. Updated {updated_count} products in the database."
    
    def get_count(self):
        # Redis client
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        count = redis_client.get('updated_count')
        if count is not None:
            count = int(count.decode('utf-8'))
        return self.send_notification(count)

    
