## Decorator
```python title="decorators.py"
#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from concurrent.futures import ThreadPoolExecutor
from functools import wraps


def conditional_execution(enable):
    """
    The decorated function will only be executed if the enable condition evaluates to True.
    The enable parameter can be either:
        - A boolean value (execution controlled at decoration time)
        - A callable that returns a boolean (execution controlled at call time)

    Args:
        enable (Union[bool, Callable[[], bool]]): Condition that determines whether
            the decorated function should execute. If callable, it will be evaluated
            each time the decorated function is called.

    Returns:
        Callable: A decorated function that will conditionally execute based on the enable condition.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            res = enable() if callable(enable) else enable
            if res:
                return func(*args, **kwargs)
            return None

        return wrapper

    return decorator


def parallel_iterator(func):
    """
    Multithreading decorator for parallel processing of each element in an iterable object.

    The decorated function will create a thread for each element to process them in parallel.
    Suitable for functions that process iterable objects, where the first parameter should be an iterable.
    """

    @wraps(func)
    def wrapper(items, *args, **kwargs):
        max_workers = min(kwargs.get('default_workers', 6), len(items)) if items else 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(func, [item], *args, **kwargs) for item in items]
            for future in futures:
                future.result()

    return wrapper
```
## Usage
```python title="decorator_test.py"
#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from decorators import conditional_execution
from decorators import parallel_iterator


@parallel_iterator
def check_container_runtime(hosts):
    # ToDo...

if __name__ == '__main__':
    conditional_execution(enable=True)(self.health_check)()
    check_container_runtime(hosts)
```
