import tkinter as tk
import tkinter.ttk as ttk
from tkinter.font import Font
import webbrowser # for opening links


class DropDown(tk.OptionMenu):
    """
    Classic drop down entry

    Example use:
        # create the dropdown and grid
        dd = DropDown(root, ['one', 'two', 'three'])
        dd.grid()

        # define a callback function that retrieves the currently selected option
        def callback():
            print(dd.get())

        # add the callback function to the dropdown
        dd.add_callback(callback)
    """
    def __init__(self, parent:tk.Tk, options: list, initial_value: str=None,font: Font = None):
        """
        Constructor for drop down entry

        :param parent: the tk parent frame
        :param options: a list containing the drop down options
        :param initial_value: the initial value of the dropdown
        :param font: a tuple containing options for a tk font
        """
        self.var = tk.StringVar(parent)
        self.var.set(initial_value if initial_value else options[0])

        self.option_menu = option_menu = tk.OptionMenu.__init__(self, parent, self.var,*options)
     
        if font:
            self.config(font=font)
            #helv20 = tkFont(family=font[0], size=font[1])
            menu:DropDown = parent.nametowidget(self.menuname)  # Get menu widget.
            menu.config(font=font)  # Set the dropdown menu's font

        self.callback = None

    def add_callback(self, callback: callable):
        """
        Add a callback on change

        :param callback: callable function
        :return: 
        """
        def internal_callback(*args):
            callback()

        #self.var.trace("w", internal_callback) --Deprecated
        self.var.trace_add("write", internal_callback)

    def get(self):
        """
        Retrieve the value of the dropdown

        :return: 
        """
        return self.var.get()

    def set(self, value: str):
        """
        Set the value of the dropdown

        :param value: a string representing the
        :return: 
        """
        self.var.set(value)

    def update_options(self,options:list):
        """
        Updates the 
        :param options: a list containing the drop down options
        """
        self['menu'].delete(0, 'end')
        self.var.set(options[0])
        for x in options:
            self["menu"].add_command(label=x,command=tk._setit(self.var, x))

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
        self.configure(width=len(text)+4)
    
    
    def pack(self, *args, **kwargs):
        # expand and fill to emulate the Message look (centered). --deprecated
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


class TkNewDialog(tk.Toplevel):
    def __init__(self, parent:tk.Tk, title:str=None,*args, **kwargs) -> None:
        if not title:
            title = ""
        
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.title(title)
        self.geometry("205x125")
        #self.attributes('-topmost', 'true')
        self.transient(parent)
        #parent.eval(f'tk::PlaceWindow {str(self)} center')
        self.center()
        self.grab_set()
    
    def center(self):
        """
        centers a tkinter window on the monitor
        """
        self.update_idletasks()
        width = self.winfo_width()
        frm_width = self.winfo_rootx() - self.winfo_x()
        win_width = width + 2 * frm_width
        height = self.winfo_height()
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.winfo_screenwidth() // 2 - win_width // 2
        y = self.winfo_screenheight() // 2 - win_height // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))


class TkMessageDialog(TkNewDialog):
    def __init__(self, parent: tk.Tk,website:str,code:str, title: str = None,font:Font=None,*args, **kwargs) -> None:
        super().__init__(parent, title, *args, **kwargs)
        if not font:
            font = Font(family="Helvetica", size=10)
        self.resizable(False, False)
        label=ttk.Label(self, text="Please go to this website\nand enter the following code:",font=font,padding=8).pack()
        TkCopyableWeblink(self, text=website,font=font).pack()
        TkCustomEntry(self, text=code,font=font).pack()
        button=ttk.Button(self, text="OK", command=self.destroy)
        button.pack(side=tk.BOTTOM, anchor=tk.E, padx=5, pady=5)


if __name__ == "__main__":
    # Testing
    parent = tk.Tk()
    #tk.Text(parent).pack()
    def callback():
        hei = TkMessageDialog(parent, "https://www.google.com", "https://www.google.com", "Test")
    #TkWeblink(hei, text="Click me", link="https://www.google.com").pack()
    #TkCopyableWeblink(hei, text="Click me", link="https://www.google.com").pack()
    #TkCustomEntry(hei, text="this is an example").pack()
    #hei.center()
    tk.Button(parent, text="Click me", command=callback).pack()
    parent.mainloop()
