## Prerequisites
- [Redis Installation Release](https://github.com/redis-windows/redis-windows/releases)
- pip install sqlite3

## Global Environment Variables
```bash title=".env"
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

DEFAULT_EXPIRE=30
HOT_DATA_THRESHOLD=100

PERSISTENT_DB=user_profile.db
CACHE_NAME=user_profile_cache
```

## Hybrid Storage
```python title="hybrid_storage.py"
import copy
import json
import os
import sqlite3

from walrus import Database

USER_PROFILE_CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS user_profile (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)'''
USER_PROFILE_INSERT_TABLE = 'INSERT OR REPLACE INTO user_profile (user_id, username, email, full_name) VALUES (?, ?, ?, ?)'
USER_PROFILE_SELECT_TABLE = 'SELECT user_id, username, email, full_name FROM user_profile WHERE user_id = ?'
USER_PROFILE_UPDATE_TABLE = 'UPDATE user_profile SET {} WHERE user_id = ?'


class HybridStorage(object):
    def __init__(self, persistent_db=None, cache_name=None, cache_expire=None):
        self.sqlite_connection = self.create_sqlite_connection(persistent_db)
        self.sqlite_cursor = self.create_sqlite_cursor()
        self.create_sqlite_user_profile_table()

        self.redis_db = self.create_redis_connection()
        self.cache = self.create_redis_cache(cache_name, cache_expire)

    @staticmethod
    def create_sqlite_connection(persistent_db):
        """Create SQLite3 connection (representing persistent storage)"""
        return sqlite3.connect(database=persistent_db or os.getenv('PERSISTENT_DB', 'user_profile.db'))

    def create_sqlite_cursor(self):
        """Create SQLite3 cursor"""
        return self.sqlite_connection.cursor()

    def create_sqlite_user_profile_table(self):
        """Create SQLite3 persistent user_profile table"""
        self.sqlite_cursor.execute(USER_PROFILE_CREATE_TABLE)
        self.sqlite_connection.commit()

    @staticmethod
    def create_redis_connection():
        """Create Redis connection using Walrus library (representing cache storage)"""
        return Database(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD') or None
        )

    def create_redis_cache(self, name, expire):
        """ Create Redis cache with expiration time"""
        return self.redis_db.cache(
            name=name or os.getenv('CACHE_NAME', 'user_profile_cache'),
            default_timeout=expire or os.getenv('DEFAULT_EXPIRE', 3600)
        )

    def add_user(self, user_id, username, email, full_name):
        """Add user to persistent storage and optionally cache"""
        self.sqlite_cursor.execute(USER_PROFILE_INSERT_TABLE, (user_id, username, email, full_name))
        self.sqlite_connection.commit()

        # Optionally cache partial data (e.g., only frequently used data)
        # cache_data = {'username': username, 'full_name': full_name}
        # self.cache.set(f'user:{user_id}', json.dumps(cache_data))

        return True

    def get_user(self, user_id):
        """Get user from cache preferentially"""
        cached_data = self.get_user_from_cache(user_id)
        if cached_data:
            return cached_data

        persistent_data = self.get_user_from_storage(user_id)
        if persistent_data:
            cache_data = copy.deepcopy(persistent_data)
            cache_data.pop('user_id', 'unknown')
            cache_data.pop('email', 'unknown')
            self.cache.set(f'user:{user_id}', json.dumps(cache_data))
            return persistent_data

        return None

    def get_user_from_cache(self, user_id):
        """Get user from cache"""
        cached_data = self.cache.get(f'user:{user_id}')

        if cached_data:
            print(f'Get user {user_id} from cache')
            return json.loads(cached_data)

        return None

    def get_user_from_storage(self, user_id):
        """Get user from persistent storage"""
        self.sqlite_cursor.execute(USER_PROFILE_SELECT_TABLE, (user_id,))
        persistent_data = self.sqlite_cursor.fetchone()

        if persistent_data:
            print(f'Get user {user_id} from persistent storage')
            user_id, username, email, full_name = persistent_data
            return {'user_id': user_id, 'username': username, 'email': email, 'full_name': full_name}

        return None

    def update_user(self, user_id, **kwargs):
        """Update user to persistent storage and cache"""
        if kwargs:
            columns = ', '.join([f'{key} = ?' for key in kwargs.keys()])

            values = list(kwargs.values())
            values.append(user_id)

            self.sqlite_cursor.execute(USER_PROFILE_UPDATE_TABLE.format(columns), values)
            self.sqlite_connection.commit()

            self.cache.delete(f'user:{user_id}')

            if 'username' in kwargs or 'full_name' in kwargs:
                cached_data = self.cache.get(f'user:{user_id}')
                if cached_data:
                    cache_dict = json.loads(cached_data)
                    cache_dict.update({key: value for key, value in kwargs.items() if key in ['username', 'full_name']})
                    self.cache.set(f'user:{user_id}', json.dumps(cache_dict))

    def clear_user_cache(self):
        """Clear Redis user cache"""
        self.cache.flush()

    def close_sqlite_connection(self):
        """Close SQLite3 connection"""
        self.sqlite_connection.close()


if __name__ == '__main__':
    hybrid_storage = HybridStorage()

    print('Clearing users cache...')
    hybrid_storage.clear_user_cache()
    print('-------------------------------------------------------------')

    print('Adding users (username, email, full_name)...')
    hybrid_storage.add_user(1, 'simon_zhou', 'john@example.com', 'Simon')
    hybrid_storage.add_user(2, 'jane_liu', 'jane@example.com', 'Jane Liu')
    print('-------------------------------------------------------------')

    print('Getting user1 from storage firstly...')
    persistent_user1 = hybrid_storage.get_user(1)
    print(persistent_user1)
    print('-------------------------------------------------------------')

    print('Getting user1 from cache secondly...')
    cached_user1 = hybrid_storage.get_user(1)
    print(cached_user1)
    print('-------------------------------------------------------------')

    print('Updating user1 full name...')
    hybrid_storage.update_user(1, full_name='Simon Zhou')
    print('-------------------------------------------------------------')

    print('Getting user1 again from storage (invalidated cache)...')
    updated_user1 = hybrid_storage.get_user(1)
    print(updated_user1)

    hybrid_storage.close_sqlite_connection()
```

## Hybrid Storage Output
```plaintext title="Hybrid storage output"
Clearing users cache...
-------------------------------------------------------------
Adding users (username, email, full_name)...
-------------------------------------------------------------
Getting user1 from storage firstly...
Get user 1 from persistent storage
{'user_id': 1, 'username': 'simon_zhou', 'email': 'john@example.com', 'full_name': 'Simon'}
-------------------------------------------------------------
Getting user1 from cache secondly...
Get user 1 from cache
{'username': 'simon_zhou', 'full_name': 'Simon'}
-------------------------------------------------------------
Updating user1 full name...
-------------------------------------------------------------
Getting user1 again from storage (invalidated cache)...
Get user 1 from persistent storage
{'user_id': 1, 'username': 'simon_zhou', 'email': 'john@example.com', 'full_name': 'Simon Zhou'}
```
