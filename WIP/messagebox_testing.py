import tkinter as tk
import tkinter.ttk as ttk
import webbrowser # for opening links


class TkNewDialog(tk.Toplevel):
    def __init__(self, parent:tk.Tk, title:str=None):
        if not title:
            title = ""
        tk.Toplevel.__init__(self, parent)
        self.title(title)
        self.geometry("300x300")
        #self.attributes('-topmost', 'true')
        self.transient(parent)
        parent.eval(f'tk::PlaceWindow {str(self)} center')
    

class TkMessageDialog(TkNewDialog):
    def __init__(self, parent: tk.Tk, title: str = None, text:str=None):
        super().__init__(parent, title)
        if not text:
            text = ""
        self.grab_set()
        #TkCustomEntry(self, text=text).pack()


class TkCustomEntry(ttk.Entry):
    def __init__(self, parent:tk.Misc, text:str, *args, **kwargs) -> None:
        """A ttk.Entry that looks like a ttk.Message."""
        default_options = {
            'style': 'TLabel', # This means ttk.Label uses a 'TLabel' style
            'justify': 'center', # justify to emulate the Messagebox look (centered).
            'state': 'readonly'} # `readonly` to protect the Entry from being overwritten
        
        for key in default_options:
            if not key in kwargs:
                kwargs[key] = default_options[key]
        
        """ if not 'style' in kwargs:
            kwargs['style'] = 'TLabel'
        if not 'justify' in kwargs:
            kwargs['justify'] = 'center'
        if not 'state' in kwargs:
            kwargs['state'] = 'readonly' """
        
        self.variable = tk.StringVar(parent, value=text)
        self.variable.trace_add('write', lambda val, index, value: self.variable.get())

        if not 'textvariable' in kwargs:
            kwargs['textvariable'] = self.variable
        
        ttk.Entry.__init__(self, parent, *args, **kwargs)
        self.configure(width=len(text))
    
    
    def pack(self, *args, **kwargs):
        # expand and fill to emulate the Message look (centered).
        """ if not 'expand' in kwargs:
            kwargs['expand'] = True
        if not 'fill' in kwargs:
            kwargs['fill'] = tk.BOTH """
        super().pack(*args, **kwargs)

class TkWeblink(tk.Label):
    def __init__(self, parent:tk.Misc, text:str, link:str=None, *args, **kwargs) -> None:
        """A label that opens a web link when clicked.
        If no link is spesified, the label text will be used as the link."""

        if not 'fg' in kwargs:
            kwargs['fg'] = 'blue'
        if not 'cursor' in kwargs:
            kwargs['cursor'] = 'hand2'
        if not link:
            link = text
        self.link = link

        tk.Label.__init__(self, parent, text=text, *args, **kwargs)
        self.init_binds()

    def init_binds(self):
        self._entered = False
        self.bind("<ButtonRelease-1>", self._web_link)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _web_link(self, event):
        if self._entered:
            webbrowser.open_new(self.link)
    
    def _on_enter(self, event):
        self._entered = True
    def _on_leave(self, event):
        self._entered = False

class TkCopyableWeblink(TkCustomEntry, TkWeblink):
    def __init__(self, parent: tk.Misc, text: str,link:str=None, *args, **kwargs) -> None:
        """An Entry widget that opens a web link when clicked.
        If no link is spesified, the label text will be used as the link.
        It is possible to highlight the text.
        This class uses a ttk.Entry widget for its base class."""
        if 'fg' in kwargs:
            kwargs['foreground'] = kwargs.pop('fg')
        
        if not 'foreground' in kwargs:
            kwargs['foreground'] = 'blue'
        if not 'cursor' in kwargs:
            kwargs['cursor'] = 'hand2'
        if not link:
            link = text
        self.link = link
        super().__init__(parent, text, *args, **kwargs)

        self.init_binds()

parent = tk.Tk()

hei = TkMessageDialog(parent, title="Example", text="this is an example")
TkWeblink(hei, text="Click me", link="https://www.google.com").pack()
TkCopyableWeblink(hei, text="Click me", link="https://www.google.com").pack()
TkCustomEntry(hei, text="this is an example").pack()
#hei.center()
parent.mainloop()

from tkinter import Misc, messagebox
#messagebox.showinfo("Title", "a Tkinter messagebox 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1")