## Redis Hot Data Cache
```bash title="Redis global environment variable"
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

DEFAULT_EXPIRE=3600
HOT_DATA_THRESHOLD=100
```

```python title="Redis hot data cache"
import logging
import os
import time

from dotenv import load_dotenv
from walrus import Database

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOGGER.addHandler(handler)

load_dotenv()


class HotDataCache(object):
    """Redis hot data cache"""

    def __init__(self, host=None, port=None, db=None, password=None):
        """Initialize Redis connection and cache structure"""
        # Get redis connection
        self.db = self.get_redis_connection(host, port, db, password)

        # Create hash table to store hot data
        self.hot_data = self.db.Hash('hot_data')

        # Sorted set to record data access frequency
        self.access_frequency = self.db.ZSet('access_frequency')

    @staticmethod
    def get_redis_connection(host, port, db, password):
        return Database(
            host=host or os.getenv('REDIS_HOST', 'localhost'),
            port=port or int(os.getenv('REDIS_PORT', 6379)),
            db=db or int(os.getenv('REDIS_DB', 0)),
            password=password or os.getenv('REDIS_PASSWORD')
        )

    @staticmethod
    def get_hot_data_expire(expire=None):
        """Get hot data expiration time (seconds)"""
        return expire or os.getenv('DEFAULT_EXPIRE')

    @staticmethod
    def get_hot_data_threshold(threshold=None):
        """Get hot data threshold"""
        return threshold or os.getenv('HOT_DATA_THRESHOLD')

    def get(self, key):
        """Get cached data and update access frequency if it exists"""
        data = self.hot_data.get(key)

        if data is not None:
            # Update access frequency (increment by 1)
            self.access_frequency.incr(key, 1)
            return data.decode('utf-8')

        return None

    def set(self, key, value, expire=None):
        """Set cached data with support for custom expiration time"""
        # Set data
        self.hot_data[key] = value

        # Set expiration time
        self.db.expire(key, self.get_hot_data_expire(expire))

        # Initial access count
        self.access_frequency.incr(key, 1)

    def get_hot_data(self, count=10):
        """Get the most frequently accessed hot data. Sort by access frequency in descending order"""
        return self.access_frequency.range(0, count - 1, with_scores=True, reverse=True)

    def clean_expired_data(self):
        """Clean up expired data (Redis usually handles this automatically, but can be triggered manually)"""
        expired_keys = []

        for key in self.hot_data:
            if not self.db.exists(key):
                expired_keys.append(key)

        for key in expired_keys:
            self.delete(key)

        return expired_keys

    def delete(self, key):
        """Delete cached data"""
        if key in self.hot_data:
            del self.hot_data[key]
            self.access_frequency.remove(key)
            return True
        return False


if __name__ == '__main__':
    cache = HotDataCache()

    # Simulate writing some dynamic data
    cache.set('user:1001', '{"name": "Alice", "age": 30}', expire=1800)
    cache.set('product:2001', '{"name": "Laptop", "price": 999}', expire=3600)
    cache.set('news:3001', '{"title": "Tech Conference 2023", "content": "..."}', expire=1200)

    # Simulate hot data access
    LOGGER.info('Simulating hot data access...')
    for _ in range(150):  # Access 150 times, exceeding hot threshold
        cache.get('product:2001')

    for _ in range(80):  # Access 80 times, not exceeding hot threshold
        cache.get('user:1001')

    # Retrieve data
    LOGGER.info('Retrieving cached data:')
    LOGGER.info('User 1001: {}'.format(cache.get('user:1001')))
    LOGGER.info('Product 2001: {}'.format(cache.get('product:2001')))

    # View hot data
    LOGGER.info('Current hot data (access frequency):')
    hot_items = cache.get_hot_data()
    for item in hot_items:
        LOGGER.info('Key: {}, Access count: {}'.format(item[0].decode('utf-8'), int(item[1])))

    # Simulate time passing (5 seconds)
    LOGGER.info('Waiting for 5 seconds...')
    time.sleep(5)

    # Clean up expired data (demonstration)
    expired = cache.clean_expired_data()
    LOGGER.info(f'Cleaned up expired data: {expired}')

    # Example of deleting data
    cache.delete('news:3001')
    LOGGER.info('After deleting news:3001, attempt to retrieve: {}'.format(cache.get('news:3001')))
```
