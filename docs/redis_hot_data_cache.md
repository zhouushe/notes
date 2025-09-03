## Prerequisites
### Redis Installation Release
[https://github.com/redis-windows/redis-windows/releases](https://github.com/redis-windows/redis-windows/releases)

## Redis Hot Data Cache
### Redis Global Environment Variable
```bash title=".env"
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

DEFAULT_EXPIRE=30
HOT_DATA_THRESHOLD=100
```
### Redis Hot Data Cache
```python title="redis_hot_data_cache.py"
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

    def __init__(self, host=None, port=None, db=None, password=None, expire=None, threshold=None):
        self.expire = self.get_hot_data_expire(expire)
        self.threshold = self.get_hot_data_threshold(threshold)
        self.db = self.get_redis_connection(host, port, db, password)

        self.access_data = self.db.Hash('access_data')
        self.hot_data = self.db.cache('hot_data', self.expire)
        self.access_frequency = self.db.ZSet('access_frequency')

    @staticmethod
    def get_redis_connection(host, port, db, password):
        """Get Redis connection"""
        return Database(
            host=host or os.getenv('REDIS_HOST', 'localhost'),
            port=port or int(os.getenv('REDIS_PORT', 6379)),
            db=db or int(os.getenv('REDIS_DB', 0)),
            password=password or os.getenv('REDIS_PASSWORD')
        )

    @staticmethod
    def get_hot_data_expire(expire=None):
        """Get hot data expiration time (seconds)"""
        return int(expire or os.getenv('DEFAULT_EXPIRE'))

    @staticmethod
    def get_hot_data_threshold(threshold=None):
        """Get hot data threshold"""
        return int(threshold or os.getenv('HOT_DATA_THRESHOLD'))

    def get(self, key):
        """Get cached data and update access frequency if it exists"""
        self.access_frequency.incr(key, 1)
        self.set_hot_data(key, self.access_data.get(key))
        return self.access_data.get(key)

    def set(self, key, value, expire=None, threshold=None):
        """Set cached data with support for custom expiration time"""
        self.access_frequency.incr(key, 1)
        self.access_data.expire(expire)
        self.access_data[key] = value
        self.set_hot_data(key, self.access_data.get(key))

    def set_hot_data(self, key, value):
        """Set hot data with key and value"""
        if self.get_access_score(key) >= self.threshold:
            self.hot_data.set(key, value)

    def get_access_data(self, count=5):
        """Get the most frequently accessed data which sorted by access frequency in descending order"""
        return self.access_frequency.range(0, count - 1, with_scores=True, reverse=True)

    def get_access_keys(self):
        """Get access keys with pattern"""
        return [key.decode('utf-8') for key in self.access_data.keys()]

    def get_hot_data(self, key=None):
        """Get hot data with specified key"""
        if key:
            return self.hot_data.get(key)
        return self.hot_data

    def get_access_score(self, key):
        """Get access frequency score"""
        return int(self.access_frequency.score(key) or 0)

    def get_expired_data(self):
        """Get expired data (Redis usually handles this automatically)"""
        expired_data = []

        for key in self.get_access_keys():
            if key not in self.hot_data:
                expired_data.append(key)

        return expired_data

    def clear_all_data(self, key=None):
        """Clear all data with specified key"""
        self.clear_hot_data(key)
        self.clear_access_data(key)
        self.reset_access_counter(key)

    def clear_hot_data(self, key=None):
        """Clear hot data with specified key"""
        if key:
            self.hot_data.delete(key)
        self.hot_data.flush()

    def clear_access_data(self, key=None):
        """Clear access data with specified key"""
        if key:
            del self.access_data[key]
        self.access_data.clear()

    def reset_access_counter(self, key=None):
        """Reset access counter with specified key"""
        if key:
            del self.access_frequency[key]
        self.access_frequency.clear()


if __name__ == '__main__':
    hot_data_cache = HotDataCache()

    LOGGER.info('Cleaning all data firstly...')
    hot_data_cache.clear_all_data()
    LOGGER.info('-------------------------------------------------------------')

    LOGGER.info('Setting access data...')
    hot_data_cache.set('user:1001', '{"name": "Alice", "age": 30}')
    hot_data_cache.set('product:2001', '{"name": "Laptop", "price": 999}')
    hot_data_cache.set('news:3001', '{"title": "Tech Conference 2025", "content": "Hello world!"}')
    LOGGER.info('-------------------------------------------------------------')

    LOGGER.info('Simulating access data...')
    for _ in range(50):
        hot_data_cache.get('user:1001')
    for _ in range(100):
        hot_data_cache.get('product:2001')
    for _ in range(150):
        hot_data_cache.get('news:3001')
    LOGGER.info('-------------------------------------------------------------')

    LOGGER.info('Retrieving access data...')
    access_data = hot_data_cache.get_access_data()
    for item in access_data:
        key, frequently = item[0].decode('utf-8'), int(item[1])
        LOGGER.info('Key: {}, Value: {}, Frequently: {}'.format(key, hot_data_cache.get(key), frequently))
    LOGGER.info('-------------------------------------------------------------')

    LOGGER.info('Waiting for {} seconds...'.format(int(hot_data_cache.expire / 2)))
    time.sleep(int(hot_data_cache.expire / 2))
    LOGGER.info('-------------------------------------------------------------')

    LOGGER.info('Retrieving hot data...')
    for key in hot_data_cache.get_access_keys():
        value = hot_data_cache.get_hot_data(key)
        value and LOGGER.info('Key: {}, Value: {}'.format(key, value))
    LOGGER.info('-------------------------------------------------------------')

    LOGGER.info('Cleaning hot data with specified key...')
    hot_data_cache.clear_hot_data('news:3001')
    LOGGER.info('Get news:3001 = {} after deleting'.format(hot_data_cache.get_hot_data('news:3001')))
    LOGGER.info('-------------------------------------------------------------')

    LOGGER.info('Waiting for {} seconds to expire...'.format(int(hot_data_cache.expire / 2) + 3))
    time.sleep(int(hot_data_cache.expire / 2) + 3)
    LOGGER.info('-------------------------------------------------------------')

    LOGGER.info('Retrieving hot data with specified key...')
    hot_data_cache.clear_hot_data('product:2001')
    LOGGER.info('Get product:2001 = {} after expire'.format(hot_data_cache.get_hot_data('product:2001')))
```
### Redis Hot Data Cache Output
```plaintext title="Redis hot data cache output"
2025-09-02 14:36:09,247 - __main__ - INFO - Cleaning all data firstly...
2025-09-02 14:36:09,267 - __main__ - INFO - -------------------------------------------------------------
2025-09-02 14:36:09,267 - __main__ - INFO - Setting access data...
2025-09-02 14:36:09,270 - __main__ - INFO - -------------------------------------------------------------
2025-09-02 14:36:09,270 - __main__ - INFO - Simulating access data...
2025-09-02 14:36:09,642 - __main__ - INFO - -------------------------------------------------------------
2025-09-02 14:36:09,642 - __main__ - INFO - Retrieving access data...
2025-09-02 14:36:09,644 - __main__ - INFO - Key: news:3001, Value: b'{"title": "Tech Conference 2025", "content": "Hello world!"}', Frequently: 151
2025-09-02 14:36:09,644 - __main__ - INFO - Key: product:2001, Value: b'{"name": "Laptop", "price": 999}', Frequently: 101
2025-09-02 14:36:09,645 - __main__ - INFO - Key: user:1001, Value: b'{"name": "Alice", "age": 30}', Frequently: 51
2025-09-02 14:36:09,645 - __main__ - INFO - -------------------------------------------------------------
2025-09-02 14:36:09,645 - __main__ - INFO - Waiting for 15 seconds...
2025-09-02 14:36:24,646 - __main__ - INFO - -------------------------------------------------------------
2025-09-02 14:36:24,646 - __main__ - INFO - Retrieving hot data...
2025-09-02 14:36:24,647 - __main__ - INFO - Key: product:2001, Value: b'{"name": "Laptop", "price": 999}'
2025-09-02 14:36:24,647 - __main__ - INFO - Key: news:3001, Value: b'{"title": "Tech Conference 2025", "content": "Hello world!"}'
2025-09-02 14:36:24,647 - __main__ - INFO - -------------------------------------------------------------
2025-09-02 14:36:24,647 - __main__ - INFO - Cleaning hot data with specified key...
2025-09-02 14:36:24,648 - __main__ - INFO - Get news:3001 = None after deleting
2025-09-02 14:36:24,648 - __main__ - INFO - -------------------------------------------------------------
2025-09-02 14:36:24,648 - __main__ - INFO - Waiting for 18 seconds to expire...
2025-09-02 14:36:42,648 - __main__ - INFO - -------------------------------------------------------------
2025-09-02 14:36:42,648 - __main__ - INFO - Retrieving hot data with specified key...
2025-09-02 14:36:42,649 - __main__ - INFO - Get product:2001 = None after expire
```
