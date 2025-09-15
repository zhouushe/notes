## operation

### base_operation.py
```python title="base_operation.py"
#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class BaseOperation(object):
    """This a class for implementing the base operation"""

    def __init__(self, name=None):
        self.name = name
```

### snapshot_operation.py
```python title="snapshot_operation.py"
#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging

from operation.base_operation import BaseOperation

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class SnapshotOperation(BaseOperation):
    """This is a class for implementing the snapshot operation"""

    def __init__(self, name=None):
        super(SnapshotOperation, self).__init__(name)

    def create_snapshot(self, file_system=None, snap_param=None):
        LOGGER.info('%s create %s with param %s', self.name, file_system, snap_param)
```

### clone_operation.py
```python title="clone_operation.py"
#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging

from operation.base_operation import BaseOperation

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class CloneOperation(BaseOperation):
    """This is a class for implementing the clone operation"""

    def __init__(self, name=None):
        super(CloneOperation, self).__init__(name)

    def create_clone(self, file_system=None, clone_param=None):
        LOGGER.info('%s create %s with param %s', self.name, file_system, clone_param)
```

## aggregation

### file_system_aggregation.py
```python title="file_system_aggregation.py"
#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging

from operation.clone.clone_operation import CloneOperation
from operation.snapshot.snapshot_operation import SnapshotOperation

LOGGER = logging.getLogger(__name__)


class FilesystemAggregation(SnapshotOperation, CloneOperation):
    """This is a class for implementing the aggregated operation of filesystem"""
```

## worker

### base_worker.py
```python title="base_worker.py"
#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class BaseWorker(object):
    """This is a base class for implementing steps to run the operation"""

    def __init__(self):
        pass

    @abc.abstractmethod
    def run(self, *args):
        """abstract method"""
```

### step_worker.py
```python title="step_worker.py"
#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

import logging

from worker.base_worker import BaseWorker

LOGGER = logging.getLogger(__name__)


class StepWorker(BaseWorker):
    """This is a class for implementing steps to run the operation"""

    STEP = 1

    def __init__(self, desc):
        super().__init__()
        self.desc = desc
        self.step = StepWorker.STEP
        StepWorker.STEP += 1

    def run(self):
        LOGGER.info('[STEP {}]: {}'.format(self.step, self.desc))
```

## singleton

### singleton_meta.py
```python title="singleton_meta.py"
#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

import logging

import threading

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class SingletonMeta(type):
    """
    This is a metaclass for implementing the Singleton pattern, ensuring that only a single instance of each class is created.

    Usage:
        class MyClass(metaclass=SingletonMeta):
            ...
    """

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """
        Override the class instantiation process.

        Args:
            *args: Positional arguments for class initialization
            **kwargs: Keyword arguments for class initialization

        Returns:
            The singleton instance of the class
        """
        # First check (without lock) for performance
        if cls not in cls._instances:
            # Acquire lock for thread-safe instantiation
            with cls._lock:
                # Second check with lock to prevent race condition
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    @classmethod
    def get_instance(cls, target):
        """
        Get the singleton instance of a specific class.

        Args:
            target: The class whose singleton instance is requested

        Returns:
            The singleton instance if it exists, otherwise None
        """
        return cls._instances.get(target)

    @classmethod
    def reset_instance(cls, target):
        """
        Reset the singleton instance of a specific class.

        This allows creating a new instance on next instantiation attempt.

        Args:
            target: The class whose singleton instance should be reset
        """
        if target in cls._instances:
            del cls._instances[target]
```

## workflow

### base_workflow.py
```python title="base_workflow.py"
#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import abc
import functools
import logging

import six

from singleton.singleton_meta import SingletonMeta
from worker.step.step_worker import StepWorker

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseWorkflow(metaclass=SingletonMeta):
    """This is a base class for implementing filesystem workflow"""

    @property
    @abc.abstractmethod
    def operation_cls(self):
        pass

    def __init__(self, *args, **kwargs):
        self.operation_obj = self.operation_cls(*args, **kwargs)

    def __getattr__(self, item):
        """
        Transparently redirect an object's property and method calls to another object, while preserving the method metadata integrity.

        Args:
            item(text_type): property or method name

        Raises:
            AttributeError: if the property/method can't find from operation instance.
        """
        attr = getattr(self.operation_obj, item)
        return functools.wraps(attr)(lambda *args, **kwargs: attr(*args, **kwargs)) if callable(attr) else attr

    @staticmethod
    def log_step(desc):
        """
        logging immediately step description in log

        Args:
            desc(text_type): the step description
        """
        StepWorker(desc).run()
```

### filesystem_workflow.py
```python title="filesystem_workflow.py"
#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging

from aggregation.file_system_aggregation import FilesystemAggregation
from workflow.base_workflow import BaseWorkflow

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class FileSystemWorkflow(BaseWorkflow):
    """This is a class for implementing filesystem workflow and specify an aggregation class"""

    operation_cls = FilesystemAggregation
```

## testing

### workflow_test.py
```python title="workflow_test.py"
import logging

from workflow.filesystem.filesystem_workflow import FileSystemWorkflow

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    workflow = FileSystemWorkflow(name='file_system_workflow')

    workflow.log_step('create snapshot')
    workflow.create_snapshot(file_system='snapshot_file_system', snap_param={'name': 'lit_snap', 'count': 3})

    workflow.log_step('create clone')
    workflow.create_clone(file_system='clone_file_system', clone_param={'name': 'lit_clone', 'size_total': 100})
```
