from typing import Any
import js # type: ignore
import pyodide # type: ignore
from typing import Iterable


class Element(object):
    classes = []
    element = None
    tag = "div"

    def __init__(self, *children):
        self.element = js.jQuery(f"""
            <{self.tag} class='{" ".join(self.classes)}'>
        """).append(*self.expand(children))

    def expand(self, children_list):
        result = []
        for item in children_list:
            try:
                if isinstance(item, (Element, pyodide.ffi.JsProxy)):
                    result.append(item)
                elif isinstance(item, Iterable):
                    result.extend(item)
            except Exception as e:
                print(f"{e}: Argument should be an Element or a list, not {type(item)}, {item}")
        return result

    def render(self, element_id):
        self.element.appendTo(js.jQuery(element_id))

    def on(self, kind, handler):
        self.element.on(kind, pyodide.ffi.create_proxy(lambda event: handler()))
        return self

    def __getattribute__(self, name: str) -> Any:
        try:
            return object.__getattribute__(self, name)
        except:
            return getattr(self.element, name)
