```python title="dispatch_factory.py"
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import importlib
import inspect
import logging
import re

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

PLATFORM_OPERATION_MAPPING = {
    'common': 'common.operation',
    'platform1': 'platform1.operation',
    'platform2': 'platform2.operation',
}


class DispatchFactory(object):
    """Dispatch factory class"""

    def __init__(self, platform, operation):
        self.platform = platform

        match = re.match(r'^(\w+)\.(\w+)$', operation)
        self.class_name, self.operation = match.groups() if match else (None, operation)

    @staticmethod
    def get_platform_operations(clazz):
        """get platform operations"""
        members = inspect.getmembers(clazz, predicate=DispatchFactory.is_method_or_function)
        operations = [name for (name, _) in members if not DispatchFactory.is_inherited_member(clazz, name)]
        return operations

    def is_matched_platform_operation(self, clazz, operation):
        """check if matched platform operation"""
        return self.operation == operation and (self.class_name is None or self.class_name == clazz.__name__)

    def load_platform_operation(self):
        """load platform operation"""
        module = importlib.import_module(PLATFORM_OPERATION_MAPPING[self.platform])

        for _, clazz in inspect.getmembers(module, predicate=inspect.isclass):
            operations = DispatchFactory.get_platform_operations(clazz)
            for operation in operations:
                if self.is_matched_platform_operation(clazz, operation):
                    return clazz.__module__, clazz.__name__, operation

        raise RuntimeError('Not found platform {} operation {}'.format(self.platform, self.operation))

    def dispatch(self, **kwargs):
        """dispatch platform operation"""
        module, class_name, operation = self.load_platform_operation()
        clazz = getattr(importlib.import_module(module), class_name)
        return getattr(clazz(), operation)(**kwargs)

    @staticmethod
    def is_method_or_function(member):
        """check member is method or function"""
        return inspect.ismethod(member) or inspect.isfunction(member)

    @staticmethod
    def is_inherited_member(obj, name):
        """check member is inherited from parent"""
        member_id = id(getattr(obj, name))
        mro = inspect.getmro(obj)

        for parent in mro[1:]:
            if hasattr(parent, name) and id(getattr(parent, name)) == member_id:
                return True

        return False

    def __enter__(self):
        # ToDo: will implement in future
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # ToDo: will implement in future
        pass

```
