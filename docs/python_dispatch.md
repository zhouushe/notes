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

    @staticmethod
    def get_operation_and_class_name(operation):
        """get operations and class name"""
        match = re.match(r'^(\w+)\.(\w+)$', operation)
        class_name, operation = match.groups() if match else (None, operation)
        LOGGER.debug(f'class={class_name}, operation={operation}')
        return class_name, operation

    @staticmethod
    def get_platform_operations(clazz):
        """get platform operations"""
        members = inspect.getmembers(clazz, predicate=DispatchFactory.is_method_or_function)
        operations = [name for (name, _) in members if not DispatchFactory.is_inherited_member(clazz, name)]
        return operations

    @staticmethod
    def is_matched_operation(clazz, class_name, operation, target_operation):
        """check if matched operation"""
        return operation == target_operation and (class_name is None or class_name == clazz.__name__)

    @staticmethod
    def load_platform_operation(platform, class_name, target_operation):
        """load platform operation"""
        operation_list = list()

        module = importlib.import_module(PLATFORM_OPERATION_MAPPING[platform])

        for _, clazz in inspect.getmembers(module, predicate=inspect.isclass):
            operations = DispatchFactory.get_platform_operations(clazz)
            for operation in operations:
                if DispatchFactory.is_matched_operation(clazz, class_name, operation, target_operation):
                    operation_list.append((clazz.__module__, clazz.__name__, operation))

        assert operation_list, 'No operation {} in {} for {}'.format(target_operation, class_name, platform)
        assert len(operation_list) == 1, 'More than one operation in {} for {}'.format(operation_list, platform)

        return operation_list[0]

    @staticmethod
    def dispatch(platform, operation, **kwargs):
        """dispatch platform operation"""
        class_name, target_operation = DispatchFactory.get_operation_and_class_name(operation)
        module, class_name, _ = DispatchFactory.load_platform_operation(platform, class_name, target_operation)
        clazz = getattr(importlib.import_module(module), class_name)
        return getattr(clazz(), target_operation)(**kwargs)

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


if __name__ == '__main__':
    DispatchFactory.dispatch('platform1', 'demo_operation', name='dog', age=3)
    DispatchFactory.dispatch('platform2', 'demo_operation', name='dog', age=5)

```
