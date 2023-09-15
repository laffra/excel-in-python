from ltk import later, find, on, HBox, Input, Text, VBox
from dag import Node, NotSet, memoize, clear
import re

ROW_COUNT = 5
COLUMN_COUNT = 5

class SpreadsheetCellModel(Node):
    models = {}
    script = None

    def __init__(self, key, value, listener):
        self.key = key
        self.models[key] = self
        Node.__init__(self, value, listener)

    def set(self, value):
        self.formula = None
        if value and value[0] == "=":
            self.formula = value
            self.script = re.sub("([A-Z]+[0-9]+)", r"float(SpreadsheetCellModel.models['\1'].get())", self.formula[1:])
            inputs = [SpreadsheetCellModel.models[key] for key in re.findall("([A-Z]+[0-9]+)", value)]
            self.set_inputs(inputs)
        Node.set(self, value)
        for listener in self.listeners:
            listener()

    def get(self):
        try:
            return eval(self.script) if self.formula else Node.get(self)
        except Exception as e:
            pass

    def __repr__(self):
        return f"<Cell-{self.key}>"


class RowLabel(Text):
    classes = [ "spreadsheet-row-label" ]
    

class ColumnLabel(Text):
    classes = [ "spreadsheet-column-label" ]
    

class SpreadsheetCell(Input):
    cells = {}
    models = {}
    model = NotSet()
    updating = False
    current = None

    def __init__(self, value, row, column):
        Input.__init__(self)
        self.column = column
        self.row = row
        key = f"{chr(ord('A') + column)}{row}"
        SpreadsheetCell.cells[key] = self
        SpreadsheetCell.models[key] = self.model = SpreadsheetCellModel(key, value, self.set_view)
        (self
            .on("focus", self.set_editor)
            .on("change", self.set_model)
            .on("blur", self.hide_formula)
            .attr("id", key))
        self.set_view()

    def set_editor(self):
        SpreadsheetCell.current = self
        find("#editor").val(self.model.formula or self.model.get())

    def hide_formula(self):
        if self.model.script:
            clear(self)
            self.set_view()
        self.set_editor()

    def set_view(self):
        if self.updating: later(self.set_view)
        try:
            self.updating = True
            self.element.val(self.model.get())
        finally:
            self.updating = False

    def set_model(self):
        if self.updating: return 
        try:
            self.updating = True
            self.model.set(self.element.val())
            later(self.set_view)
            self.set_editor()

        finally:
            self.updating = False


def create_row(row_index):
    row_label = RowLabel(row_index)
    cells = [ SpreadsheetCell("", row_index, column) for column in range(COLUMN_COUNT) ]
    return HBox(row_label, cells)

def update_cell():
    SpreadsheetCell.current.model.set(find("#editor").val())

def create_spreadsheet():
    editor = Input().attr("id", "editor")
    headers = HBox(ColumnLabel(), [ ColumnLabel(chr(ord('A') + column)) for column in range(COLUMN_COUNT) ])
    rows = [ create_row(row) for row in range(1, COLUMN_COUNT) ]
    VBox(editor, headers, rows).render("#main")
    SpreadsheetCell.models["A1"].set("5")
    SpreadsheetCell.models["B1"].set("4")
    SpreadsheetCell.models["C1"].set("=A1+B1")
    on(editor, "change", update_cell)

create_spreadsheet()