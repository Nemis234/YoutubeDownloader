import tkinter as tk
import tkinter.ttk as ttk
from tkinter.font import Font
import webbrowser # for opening links
from PIL import Image, ImageTk
from itertools import count


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

class TkCopyableLabel(ttk.Entry):
    def __init__(self, parent:tk.Misc, text:str, *args, **kwargs) -> None:
        """A ttk.Entry that looks like a ttk.Label."""
        default_options = {
            'style': 'TLabel', # This means ttk.Label uses a 'TLabel' style
            'justify': 'left', # justify to emulate the Messagebox look (centered).
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

class TkCustomEntry(tk.Entry):
    def __init__(self, parent:tk.Misc, text:str="Input here", 
                 fg_color:str="black",temp_color:str ="grey", *args, **kwargs) -> None:
        """A tk.Entry that puts default text in the 
        entry when it is empty and not focused.
        
        The default text will be removed when the user clicks on the entry.
        If the user clicks outside the entry, the default text will be restored.
        The color of the user input can be changed by setting the fg_color parameter.
        The color of the default text can be changed by setting the temp_color parameter.
        """
        self.temp_color = temp_color
        self.fg_color = fg_color

        if not 'fg' in kwargs:
            kwargs['fg'] = temp_color
        else:
            self.temp_color = kwargs['fg']
        
        tk.Entry.__init__(self, parent, *args, **kwargs)
        self.text = text

        self.insert(0, text)
        self.bind('<FocusIn>', self.on_focusin)
        self.bind('<FocusOut>', self.on_focusout)

    def on_focusin(self, event)->None:
        """remove default text when the entry is focused"""
        if self.cget('fg') == self.temp_color:
            self.delete(0, tk.END) # delete all the text in the entry
            self.insert(0, '') #Insert blank for user input
            self.config(fg = self.fg_color)
    
    def on_focusout(self, event)->None:
        """add default text when the entry is not focused"""
        if len(self.get()) - self.get().count(' ') < 1:
            self.insert(0, self.text)
            self.config(fg = self.temp_color)

    def insert(self, index: int, string: str) -> None:
        """insert text into the entry, in the color and maner as default text"""
        #self.config(fg = self.temp_color)
        tk.Entry.insert(self, index, string)

    def get(self,get_default: bool = False) -> str:
        """get the text from the entry, excluding the default and inserted text"""
        if self.cget('fg') == self.temp_color and not get_default:
            return ''
        return tk.Entry.get(self)

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

class TkCopyableWeblink(TkCopyableLabel, TkWeblink):
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


class TkImageLabel(tk.Label):
    """a label that displays images, and plays them if they are gifs
    
    Edited code, added resizing.
    Credit to Avishka Induwara on StackOverflow
    https://stackoverflow.com/questions/43770847/play-an-animated-gif-in-python-with-tkinter/77301483#77301483"""
    
    def __init__(self, parent:tk.Misc, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.size = (50,50)
        self.loc = 0
        self.frames = []
        self.im = None
        self.delay = 100
        self.continue_animation = False

    def set_img(self, im, size=(50,50)):
        if isinstance(im, str):
            im = Image.open(im)
        
        if not self.im == im:
            self.im = im
        
        self.loc = 0
        self.unload()
        self.size = size

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.resize(size).copy()))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100
    
    def unload(self):
        print("unloading")
        self.stop()
        self.frames = []

    def run(self):
        """Starts the animation or sets the image if it is not a gif"""
        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.continue_animation = True
            self.next_frame()

    def stop(self):
        """Stops the animation"""
        self.continue_animation = False
        self.config(image="")

    def next_frame(self):
        self.update()
        if self.frames and self.continue_animation:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.master.update_idletasks()
            self.master.after(self.delay, self.next_frame)
    
    def resize(self, size:tuple[int,int]):
        stopped = False
        if self.continue_animation:
            self.stop()
            stopped = True
        self.set_img(self.im,size)
        if stopped:
            self.run()


class TkNewDialog(tk.Toplevel):
    def __init__(self, parent:tk.Tk, title:str=None,*args, **kwargs) -> None:
        if not title:
            title = ""
        #print(kwargs)

        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.title(title)
        self.geometry("250x125")
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
        if not "background" in kwargs:
            kwargs["background"] = "white"
        super().__init__(parent, title, *args, **kwargs)

        if not font:
            font = Font(family="Helvetica", size=10)
        ttk.Style().configure('TLabel', background=kwargs.pop("background"))
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.focus_set()

        frame1 = ttk.Frame(self,style="TLabel")
        label=ttk.Label(frame1,image="::tk::icons::information")
        label.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)

        frame2 = ttk.Frame(self,style="TLabel")
        ttk.Label(frame2, 
            text="Please go to this website\nand enter the following code:"
            ,font=font,anchor=tk.W, justify="left").pack(anchor="w")
        TkCopyableWeblink(frame2, text=website,font=font).pack()
        TkCopyableLabel(frame2, text=code,font=font).pack()

        frame3 = ttk.Frame(self)
        button=ttk.Button(frame3, text="OK", command=self.destroy)
        button.pack(side=tk.BOTTOM, anchor=tk.E, padx=5, pady=5)
        frame1.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W,padx=10)
        frame2.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W,)
        frame3.grid(row=1, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)


if __name__ == "__main__":
    def testing():
        # Testing
        parent = tk.Tk()
        #tk.Text(parent).pack()
        def callback():
            return
            from tkinter import messagebox
            hei = TkMessageDialog(parent, "https://www.google.com", "https://www.google.com", "Test")
            messagebox.showinfo("Test", "Test\ntest\ntestTest\ntest\ntest")
        #TkWeblink(hei, text="Click me", link="https://www.google.com").pack()
        #TkCopyableWeblink(hei, text="Click me", link="https://www.google.com").pack()
        #TkCustomEntry(hei, text="this is an example").pack()
        #hei.center()
        TkCustomEntry(parent, text="Input here").pack()

        tk.Button(parent, text="Click me", command=callback).pack()
        label = TkImageLabel(parent)
        label.pack()
        from os.path import dirname
        file = dirname(__file__)+"\\Assets\\LoadingAnimation.gif"
        label.set_img(file)
        label.run()
        parent.mainloop()
    
    testing()

