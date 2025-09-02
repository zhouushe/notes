## Redis Hot Data Cache
```python title="Redis hot data cache"
import logging
import time

from walrus import Database

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOGGER.addHandler(handler)


class HotDataCache(object):
    # Cache configuration
    DEFAULT_EXPIRE = 3600  # Default expiration time: 1 hour
    HOT_DATA_THRESHOLD = 100  # Data with accesses exceeding this threshold is considered hot

    def __init__(self, host='localhost', port=6379, db=0):
        """Initialize Redis connection and cache structure"""
        self.db = Database(host=host, port=port, db=db)

        # Create hash table to store hot data
        self.hot_data = self.db.Hash('hot_data')

        # Sorted set to record data access frequency
        self.access_frequency = self.db.ZSet('access_frequency')

    def get(self, key):
        """Get cached data and update access frequency if it exists"""
        data = self.hot_data.get(key)

        if data is not None:
            # Update access frequency (increment by 1)
            self.access_frequency.incr(key, 1)
            return data.decode('utf-8')  # Decode to string
        return None

    def set(self, key, value, expire=None):
        """Set cached data with support for custom expiration time"""
        expire = expire or self.DEFAULT_EXPIRE

        # Set data
        self.hot_data[key] = value

        # Set expiration time
        self.db.expire(key, expire)

        # Initial access count
        self.access_frequency.incr(key, 1)

    def delete(self, key):
        """Delete cached data"""
        if key in self.hot_data:
            del self.hot_data[key]
            self.access_frequency.remove(key)
            return True
        return False

    def get_hot_data(self, count=10):
        """Get the most frequently accessed hot data"""
        # Sort by access frequency in descending order, take first 'count' items
        return self.access_frequency.range(0, count - 1, with_scores=True, reverse=True)

    def clean_expired_data(self):
        """Clean up expired data (Redis usually handles this automatically, but can be triggered manually)"""
        # In practical applications, Redis automatically cleans up expired keys, this is just a demonstration
        expired_keys = []
        for key in self.hot_data:
            if not self.db.exists(key):
                expired_keys.append(key)

        for key in expired_keys:
            self.delete(key)

        return expired_keys


# Demonstration usage
if __name__ == '__main__':
    # Initialize cache
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

    # Simulate time passing (10 seconds)
    LOGGER.info('Waiting for 10 seconds...')
    time.sleep(10)

    # Clean up expired data (demonstration)
    expired = cache.clean_expired_data()
    LOGGER.info(f'Cleaned up expired data: {expired}')

    # Example of deleting data
    cache.delete('news:3001')
    LOGGER.info('After deleting news:3001, attempt to retrieve: {}'.format(cache.get('news:3001')))
```
