import tkinter as tk

from statex import use_state, def_sx, sx, SxField
from typing import Any


class State:
    f1: str = "val1"
    f2: str = "val2"

    @def_sx(["f1", "f2"])
    def label(self):
        return self.f1 + " " + self.f2


def bind(control: tk.Entry | tk.Label, sx: SxField):
    if isinstance(control, tk.Label):
        control.config(text=sx.get())

        def on_change(source: Any):
            control.config(text=sx.get())

        sx.on_change(on_change)

        return

    control.bind("<KeyRelease>", lambda _: sx.set(control.get()))
    control.insert(0, sx.get())

    def on_change(source: Any):
        control.delete(0, tk.END)
        control.insert(0, sx.get())

    sx.on_change(on_change)


class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Tkinter App")  # type: ignore
        self.state = use_state(State)
        # Create and place GUI elements
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Field 1:").pack()
        self.entry1 = tk.Entry(self.root)
        self.entry1.pack()
        bind(self.entry1, sx(self.state).f1)

        tk.Label(self.root, text="Field 2:").pack()
        self.entry2 = tk.Entry(self.root)
        self.entry2.pack()
        bind(self.entry2, sx(self.state).f2)

        self.label = tk.Label(self.root, text="")
        self.label.pack()
        bind(self.label, sx(self.state).label)


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
