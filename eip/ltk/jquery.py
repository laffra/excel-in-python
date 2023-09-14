import js # type: ignore
import pyodide # type: ignore


def find(selector):
    return js.jQuery(selector)

def later(function, timeout=1):
    js.setTimeout(pyodide.ffi.create_proxy(function), timeout)

def on(element, kind, handler):
    element.on(kind, pyodide.ffi.create_proxy(lambda event: handler()))