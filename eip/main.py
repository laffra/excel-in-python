from ltk import later, find, on, HBox, Input, Text, VBox
from dag import Node, NotSet, memoize, clear
import re

ROW_COUNT = 5
COLUMN_COUNT = 5

def convert(cell):
    try:
        return float(cell)
    except:
        return cell

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
            value = value[1:]
        self.formula = value
        self.script = re.sub("([A-Z]+[0-9]+)", r"convert(SpreadsheetCellModel.models['\1'].get())", self.formula)
        inputs = [SpreadsheetCellModel.models[key] for key in re.findall("([A-Z]+[0-9]+)", value)]
        self.set_inputs(inputs)
        Node.set(self, value)
        for listener in self.listeners:
            listener()

    def get(self):
        try:
            self.error = False
            return eval(self.script) if self.script else ""
        except Exception as e:
            self.error = True
            return f"😞 {e}"
    def __repr__(self):
        return f"<Cell-{self.key}>"


class Blank(Text):
    classes = [ "spreadsheet-blank" ]
    

def resizable(element, handles, rowOrColumn, index):
    print('resizable', element, index)
    element.resizable()
    element.resizable("option", "handles", handles)
    element.resizable("option", "alsoResize", f".{rowOrColumn}-{index}")


class RowLabel(Text):
    classes = [ "spreadsheet-row-label" ]

    def __init__(self, value, index):
        Text.__init__(self, value)
        resizable(self.element, "s", "row", index)
    

class ColumnLabel(Text):
    classes = [ "spreadsheet-column-label" ]

    def __init__(self, value, index):
        Text.__init__(self, value)
        resizable(self.element, "e", "col", index)
    

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
        SpreadsheetCell.models[key] = self.model = SpreadsheetCellModel(key, value, self.model_changed)
        (self
            .on("focus", self.set_editor)
            .on("change", self.view_changed)
            .addClass(f"col-{column}")
            .addClass(f"row-{row}")
            .width(36)
            .height(34)
            .attr("id", key))
        self.model_changed()

    def set_editor(self):
        SpreadsheetCell.current = self
        find("#editor").val(self.model.formula or self.model.get())
        find("#value").text(self.model.get()).css("color", "#F99" if self.model.error else "#AAA")

    def model_changed(self):
        if self.updating: later(self.model_changed)
        try:
            self.updating = True
            self.element.val("😞" if self.model.error else self.model.get())
            self.element.css("color", "#F99" if self.model.error else "black")
        finally:
            self.updating = False

    def view_changed(self):
        if self.updating: return 
        try:
            self.updating = True
            self.model.set(self.element.val())
            self.set_editor()

        finally:
            self.updating = False


def create_row(row_index):
    row_label = RowLabel(row_index, row_index)
    cells = [ SpreadsheetCell("", row_index, column) for column in range(COLUMN_COUNT) ]
    return HBox(row_label, cells)

def update_cell():
    SpreadsheetCell.current.model.set(find("#editor").val())

def create_spreadsheet():
    editor = Input().attr("id", "editor")
    value = Text().css("border", "").attr("id", "value")
    blank = Blank()
    headers = HBox(blank, [ ColumnLabel(chr(ord('A') + column), column) for column in range(COLUMN_COUNT) ])
    rows = [ create_row(row) for row in range(1, COLUMN_COUNT) ]
    VBox(editor, value, headers, rows).render("#main")
    SpreadsheetCell.models["A1"].set("5")
    SpreadsheetCell.models["B1"].set("4")
    SpreadsheetCell.models["C1"].set("=A1+B1")
    SpreadsheetCell.models["A2"].set("'hello'")
    SpreadsheetCell.models["B2"].set("'world'")
    SpreadsheetCell.models["C2"].set("=A2.capitalize() + ' ' + B2.upper()")
    on(editor, "change", update_cell)

create_spreadsheet()