from ltk.element import Element


class HBox(Element):
    classes = [ "hbox" ]


class VBox(Element):
    classes = [ "vbox" ]

    
class Text(Element):
    classes = [ "text" ]

    def __init__(self, html=""):
        Element.__init__(self)
        self.element.html(html)
    
    
class Input(Element):
    classes = [ "input" ]
    tag = "input"
    
    def __init__(self, value=""):
        Element.__init__(self)
        self.element.val(value)