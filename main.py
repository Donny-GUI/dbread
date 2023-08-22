import tkinter as tk
from tkinter import ttk
import sqlite3
import sys 
import os




class Table(object):
    def __init__(self, name:str, file:str) -> None:
        self.name = name
        self.file = file
        
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info({self.name});")
        self.headers = [x[1] for x in cursor.fetchall()]
        try:
            self.headers = [x.decode() for x in self.headers]
        except:pass

        cursor.execute(f"SELECT * FROM {self.name};")
        self.values = [x for x in cursor.fetchall()]
        for value in self.values:
            try: value = [x.decode() for x in value]
            except:pass
        connection.close()


class ExcelTableApp:
    def __init__(self, root, table:Table):

        self.data = table
        self.root = root
        print(table.headers)
        indexes = [index for index, x in enumerate(self.data.headers)]
        self.table = ttk.Treeview(root, show=["headings"], columns=indexes)
        
        for index, head in enumerate(self.data.headers):
            self.table.column(index, anchor="nw")
            self.table.heading(index, text=head, anchor="nw")
        for i, row in enumerate(self.data.values): 
            tags = () if i % 2 == 0 else ("no_color",)
            self.table.insert("", i, values=row, tags=tags)

        self.table.pack(fill="both", expand=True)


def load_tables(filepath):
    connection = sqlite3.connect(filepath)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [row[0] for row in cursor.fetchall()]
    try:
        table_names = [x.decode() for x in table_names]
    except:pass

    tables = []
    connection.close()
    for tablename in table_names:
        tables.append(Table(name=tablename, file=filepath))
    return tables

def show_table_contents(table_name):
    # Add your logic to display table contents here
    pass

def on_tab_selected(event):
    tab = event.widget.tab(event.widget.select(), "text")
    show_table_contents(tab)

class KeyValuePair(object):
    def __init__(self,root,  key, value) -> None:
        self.key = key 
        self.value = value
        self.frame = tk.Frame(root)
        self.kpad = (20-len(self.key))*" "
        self.vpad = (100-len(self.value))*" "

        self.keylabel = tk.Label(self.frame, text=self.key, font="italicubuntu 12", justify="left")
        self.valuelabel = tk.Label(self.frame, text=self.kpad+" "+self.vpad+self.value, justify="left")
        self.keylabel.grid(columnspan=2, row=0, column=0, padx=0)
        self.valuelabel.grid(columnspan=2, row=0, column=2, padx=0)
        self.frame.pack(fill="both", expand=True)

def main(filepath):
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview.Heading", background="light green", foreground="gray", font="ubuntu 12")
    root.title("SQLite Table Viewer")
    kv_file = KeyValuePair(root, "File", os.path.basename(file))
    kv_dir = KeyValuePair(root, "Directory", os.path.dirname(file))
    
    def load_tables_and_display(filepath):
        tables = load_tables(filepath)
        create_tabs(root, tables)

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    def create_tabs(parent, tables:list[Table]):
        for table in tables:
            tab = ttk.Frame(tab_control)
            tab_control.add(tab, text=table.name)
            tab_control.bind("<<NotebookTabChanged>>", on_tab_selected)
            tree = ExcelTableApp(tab, table)
    load_tables_and_display(filepath)
    style.configure("Treeview.no_color", background="#C6E1B5", foreground="black")
    root.mainloop()


if __name__ == "__main__":
    try:
        file = sys.argv[1]
        print(file)
    except IndexError:
        print("no filename given")

    if os.path.exists(file):
        try:
            main(file)
        except: print("could not read this db")

