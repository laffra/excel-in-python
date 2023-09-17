from __future__ import annotations

import inspect
from dag import cache


class Node():
    inputs = []
    dependents = set()
    listeners = []
    error = False

    def __init__(self: Node, *args):
        self.dependents = set()
        self.set_inputs(set(arg for arg in args if isinstance(arg, Node)))
        self.set_listeners(set(arg for arg in args if inspect.ismethod(arg)))
        for value in set(args) - self.inputs - self.listeners:
            self.set(value)

    def set_inputs(self, inputs):
        self.inputs = inputs
        for input in inputs:
            input.dependents.add(self)

    def set_listeners(self, listeners):
        self.listeners = listeners

    @cache.memoize
    def get(self):
        pass

    def reset(self):
        self.clear()
        self.error = False
        self.notify_listeners()
    
    def clear(self):
        if self in cache.cache:
            del cache.cache[self]
            self.notify_dependents()

    def notify_dependents(self):
        for dependent in self.dependents:
            dependent.reset()

    def set(self, value):
        self.clear()
        cache.cache[self] = value
        self.notify_listeners()
        self.notify_dependents()

    def notify_listeners(self):
        for listener in self.listeners:
            listener()
        
    def __hash__(self):
        return id(self)
        
    def __repr__(self):
        return f"<{self.__class__.__name__}={cache.cache.get(self, '?')}>"


class NotSet(Node):
    pass