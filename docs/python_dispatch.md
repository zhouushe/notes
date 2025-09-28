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

    def __init__(self, platform_name, operation_name):
        self.platform_name = platform_name

        match = re.match(r'^(\w+)\.(\w+)$', operation_name)
        self.class_name, self.operation_name = match.groups() if match else (None, operation_name)

    def load_platform_operation(self):
        """load platform operation"""
        module = importlib.import_module(PLATFORM_OPERATION_MAPPING[self.platform_name])

        for _, cls in inspect.getmembers(module, predicate=inspect.isclass):
            members = inspect.getmembers(cls, predicate=DispatchFactory.is_method_or_function)
            names = [name for (name, _) in members if not DispatchFactory.is_inherited_member(cls, name)]
            for name in names:
                if name == self.operation_name and (self.class_name is None or self.class_name == cls.__name__):
                    return cls.__module__, cls.__name__, name

        raise RuntimeError('Not found platform {} operation {}'.format(self.platform_name, self.operation_name))

    def dispatch(self, **kwargs):
        """dispatch platform operation"""
        module, class_name, operation_name = self.load_platform_operation()
        platform_module = importlib.import_module(module)
        platform_class = getattr(platform_module, class_name)
        return getattr(platform_class(), operation_name)(**kwargs)

    @staticmethod
    def is_method_or_function(member):
        """check member is method or function"""
        return inspect.ismethod(member) or inspect.isfunction(member)

    @staticmethod
    def is_inherited_member(cls, member_name):
        """check member is inherited from parent"""
        member_id = id(getattr(cls, member_name))
        mro = inspect.getmro(cls)

        for parent in mro[1:]:
            if hasattr(parent, member_name) and id(getattr(parent, member_name)) == member_id:
                return True

        return False

```
