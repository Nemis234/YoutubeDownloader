import tkinter as tk
import tkinter.ttk as ttk
from tkinter.font import Font
import webbrowser # for opening links
from PIL import Image, ImageTk
from itertools import count

from typing import Callable, Type, TypeVar


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
    def __init__(self, parent:tk.Misc, options: list, initial_value: str="",font: Font|None =None )->None:
        """
        Constructor for dropdown entry

        :param parent: the tk parent frame
        :param options: a list containing the drop down options
        :param initial_value: the initial value of the dropdown
        :param font: a tuple containing options for a tk font
        """
        self.var = tk.StringVar(parent)
        self.var.set(initial_value if initial_value else options[0])

        tk.OptionMenu.__init__(self, parent, self.var,*options)
        if font:
            self.config(font=font)
            #helv20 = tkFont(family=font[0], size=font[1])
            menu:DropDown = parent.nametowidget(self.menuname)  # Get menu widget.
            menu.config(font=font)  # Set the dropdown menu's font

        self.callback = None

    def add_callback(self, callback: Callable):
        """
        Add a callback on change

        :param callback: a callable function
        :return: 
        """
        if not callable(callback):
            raise TypeError("callback must be callable")
        
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
        Updates the available options in the dropdown
        :param options: a list containing the drop down options
        :return:
        """
        self['menu'].delete(0, 'end')
        self.var.set(options[0])
        for x in options:
            self["menu"].add_command(label=x,command=tk._setit(self.var, x))

class TkCopyableLabel(ttk.Entry):
    """
    A ttk.Entry that looks like a ttk.Label, and can be copied.

    Example use:
        # create the label
        cl = TkCopyableLabel(root, 'This is a label')
        cl.pack()
    """
    def __init__(self, parent:tk.Misc, text:str, *args, **kwargs) -> None:
        """
        A ttk.Entry that looks like a ttk.Label.
        
        :param text: The text to display\n
        """
        style = ttk.Style()
        style.configure("CopyableLabel.TLabel")
        default_options = {
            'style': 'CopyableLabel.TLabel', # This means ttk.Label uses a 'TLabel' style
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

    def set(self, value:str) -> None:
        """
        Sets the text in the entry

        :param value: The text to set\n
        :return:\n
        """
        self.variable.set(value)

class TkCustomEntry(tk.Entry):
    """
    A tk.Entry that puts default text in the
    entry when it is empty and not focused.

    Example use:
        # create the entry
        foreground = "black"
        temp_color = "grey"
        ce = TkCustomEntry(root, 'Input here', foreground, temp_color)
        ce.pack()

        ce.get() # returns 'Input here' or user input if present

        ce.insert(0, 'This is an example') #Will be inserted as default text
        # at the spesified index, and will be temporarely removed when the user clicks on the entry

    """
    def __init__(self, parent:tk.Misc, text:str="Input here", 
            fg_color:str="black",temp_color:str ="grey", *args, **kwargs) -> None:
        """A tk.Entry that puts default text in the 
        entry when it is empty and not focused.
        
        The default text will be removed when the user clicks on the entry.
        If the user clicks outside the entry, the default text will be restored.

        :param text: The default text\n
        :param fg_color: The color of the user input text\n
        :param temp_color: The color of the default text\n
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
        self.bind('<FocusIn>', self._on_focusin)
        self.bind('<FocusOut>', self._on_focusout)

    def _on_focusin(self, event:tk.Event|None)->None:
        """
        Remove default text when the entry is focused

        To overwrite, bind <FocusIn> to another function

        :return:
        """
        if self.cget('fg') == self.temp_color:
            self.delete(0, tk.END) # delete all the text in the entry
            self.insert(0, '') #Insert blank for user input
            self.config(fg = self.fg_color)
    
    def _on_focusout(self, event:tk.Event|None)->None:
        """
        Add default text when the entry is not focused

        To overwrite, bind <FocusOut> to another function

        :return:
        """
        if len(self.get()) - self.get().count(' ') < 1:
            self.insert(0, self.text)
            self.config(fg = self.temp_color)

    def insert(self, index: str|int, string: str,
            as_default:bool=True,*args,**kwargs) -> None:
        """
        Insert text into the entry, in the color and maner as default text

        :param index: The index to insert the text at\n
        :param string: The text to insert\n
        :param as_default: If False, the text will be inserted as user input,
        and any default text already in the Entry box will change to user input color.
        If True, the text will be inserted as default text, 
        and any user input will change to default text color\n

        :return:
        """
        if as_default:
            self.config(fg = self.temp_color)
        else:
            self.config(fg = self.fg_color)
        
        tk.Entry.insert(self, index, string,*args,**kwargs)

    def get(self,get_default: bool = False,*args,**kwargs) -> str:
        """
        Get the text from the entry, excluding the default and inserted text
        Uses the default text color to determine if the text is default or user input
        
        :param get_default: If True, the default text will be returned if present, 
        if False it will return an empty string\n
        :return: The text in the entry\n
        """
        if self.cget('fg') == self.temp_color and not get_default:
            return ''
        return tk.Entry.get(self,*args,**kwargs)

class TkWeblink(tk.Label):
    """
    A label that opens a web link when clicked.

    Example use:
        # create the label
        wl = TkWeblink(root, 'Click me', 'https://www.google.com')
        wl.pack()
    """
    def __init__(self, parent:tk.Misc, text:str, link:str="", *args, **kwargs) -> None:
        """
        A label that opens a web link when clicked.
        If no link is spesified, the label text will be used as the link.

        :param text: The text to display\n
        :param link: The link to open when clicked\n
        """

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
        """
        Initialize the binds for the label
        Must be called after the label is initialized

        :return:
        """
        self._entered = False
        self.bind("<ButtonRelease-1>", self._web_link)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _web_link(self, event:tk.Event|None):
        """
        Internal function to open the web link
        """
        if self._entered:
            webbrowser.open_new(self.link)
    
    def _on_enter(self, event:tk.Event|None):
        """
        Internal function to set the _entered flag to True
        """
        self._entered = True
    def _on_leave(self, event:tk.Event|None):
        """
        Internal function to set the _entered flag to False
        """
        self._entered = False

class TkCopyableWeblink(TkCopyableLabel, TkWeblink):
    def __init__(self, parent: tk.Misc, text: str,link:str="", *args, **kwargs) -> None:
        """An Entry widget that opens a web link when clicked.
        If no link is spesified, the label text will be used as the link.
        It is possible to highlight the text.
        This class uses a ttk.Entry widget for its base class.
        
        :param text: The text to display\n
        :param link: The link to open when clicked\n
        """
        if 'fg' in kwargs:
            kwargs['foreground'] = kwargs.pop('fg')
        
        if not 'foreground' in kwargs:
            kwargs['foreground'] = 'blue'
        if not 'cursor' in kwargs:
            kwargs['cursor'] = 'hand2'
        if not link:
            link = text
        self.link = link

        #TkCopyableLabel.__init__(self, parent, text, *args, **kwargs)
        super().__init__(parent, text, *args, **kwargs)

        # Needed to initialized the binds from TkWeblink,
        # as TkWeblink.__init__ is not called
        self.init_binds()


class TkImageLabel(tk.Label):
    """
    A label that displays images, and plays them if they are GIFs

    Example use:
        # create the label
        il = TkImageLabel(root, 'image.gif')
        il.pack()

        # start the animation
        il.run()

        # resize the image
        il.resize((100, 100))

        # stop the animation
        il.stop()

        # put another image in the label
        il.set_img('image2.png')

        # start the animation again
        il.run() # this will set a still image as the image is not a GIF

    
    Edited code, added resizing, stopping, running and documentation
    Credit to Avishka Induwara on StackOverflow
    https://stackoverflow.com/questions/43770847/play-an-animated-gif-in-python-with-tkinter/77301483#77301483
    """
    
    def __init__(self, parent:tk.Misc,image:str|Image.Image|None=None, *args, **kwargs) -> None:
        """
        A label that displays images, and plays them if they are GIFs

        :param image: Path to the image or GIF to display or a Pillow(PIL) Image.Image object.
        Can be defined in set_img\n
        """
        super().__init__(parent, *args, **kwargs)
        self.size = (50,50)
        self.loc = 0 # The current frame index
        self.frames:list[ImageTk.PhotoImage] = []
        self.image = image # The image or GIF path ro Image to display
        self.delay = 100 # The delay between frames in the GIF, in ms. Default 100
        self.continue_animation = False

    def set_img(self, image:str|Image.Image, size:tuple[int,int]=(50,50))->None:
        """
        Sets the image or GIF to display

        :param image: Path to the image or GIF to display or a Pillow(PIL) Image.Image object\n
        :param size: The size to resize the image to in the format of a tuple,
        default (50,50)\n
        :return:
        """
        
        if not self.image == image:
            self.image = image
        if not self.size == size:
            self.size = size
        if isinstance(image, str):
            image = Image.open(image)
        
        self.loc = 0
        self.unload()

        try:
            for i in count(1): #Undefined length loop
                # Load the frames of the GIF into a list
                self.frames.append(ImageTk.PhotoImage(image.resize(size).copy()))
                image.seek(i)
        except EOFError: #End of file
            pass

        try:
            # Get the delay between frames in the GIF
            self.delay = image.info['duration']
        except:
            # If the information is not set, use the default delay
            self.delay = 100
    
    def unload(self)->None:
        """
        Stops animation and deletes the stored images from memory

        :return:
        """
        print("unloading")
        self.stop()
        self.frames = []
        self.image = None

    def run(self)->None:
        """
        Starts the animation or sets the image if it is not a GIF

        :return:
        """
        if len(self.frames) == 1:
            #If the image is not a GIF
            self.config(image=self.frames[0])
        else:
            self.continue_animation = True
            self.next_frame()

    def stop(self,freeze:bool=False)->None:
        """
        Stops the animation

        :param freeze: If True, the last frame will be displayed\n

        :return:
        """
        self.continue_animation = False
        if freeze:
            self.config(image=self.frames[self.loc])
            return
        self.config(image="")

    def next_frame(self)->None:
        """
        Displays the next frame of the animation.
        Will call itself after a delay.

        :return:
        """
        self.update() # Update the widget
        if self.frames and self.continue_animation:
            # If the animation is not stopped and there are frames to display
            self.loc += 1
            # Loop back to the first frame if the last frame is reached
            self.loc %= len(self.frames) 
            self.config(image=self.frames[self.loc])
            self.master.update_idletasks() # Update the master window
            self.master.after(self.delay, self.next_frame)
    
    def resize(self, size:tuple[int,int] | None=None)->tuple[int,int]|None:
        """
        Resizes the image or GIF.
        The image must be set before resizing.
        Will continue animation if it was running before resizing.
        If no size is passed, the current size will be returned.

        :param size: The size to resize the image to in the format of a tuple\n
        :return: The current size of the image or None\n
        """
        if not size:
            return self.size
        if not self.image:
            return None
        
        stopped = False
        if self.continue_animation:
            self.stop()
            stopped = True
        self.set_img(self.image,size)
        if stopped:
            self.run()
        return None


class TkNewDialog(tk.Toplevel):
    """
    A toplevel window that is centered on the screen and has a parent
    Is transient to the parent

    Example use:
        # create the dialog
        dialog = TkNewDialog(root, 'Dialog title')

        # add widgets to the dialog
        tk.Label(dialog, text='Dialog contents').pack()

    """
    def __init__(self, parent:tk.Tk|tk.Toplevel, title:str="",geometry:str="250x125",*args, **kwargs) -> None:
        """
        Makes a new toplevel window with the parent as the parent.
        The window will be centered on the user screen.

        :param title: The title of the window\n
        :param geometry: The geometry of the window\n
        """
        if not title:
            title = ""

        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.title(title)
        self.geometry(geometry)
        #self.attributes('-topmost', 'true')
        self.transient(parent)
        #parent.eval(f'tk::PlaceWindow {str(self)} center')
        self.center()
        self.grab_set()
    
    def center(self):
        """
        Centers a tkinter window on the monitor
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
    """
    A message dialog that displays text.
    The dialog has two buttons, OK and Cancel.
    The dialog will return True if OK was pressed, and False if Cancel was pressed.
    
    Example use:
        # create the dialog
        text = "This is a message dialog"
        website = "https://www.google.com"

        dialog = TkMessageDialog(root, text,website,'Dialog title')

        # get the result, True if OK was pressed, False if Cancel was pressed
        result = dialog.get()
    """
    def __init__(self, parent: tk.Tk|tk.Toplevel,website:str,code:str, 
                 title: str = "",font:Font|None=None,*args, **kwargs) -> None:
        """
        Makes a tkinter messagebox.showinfo lookalike with text and a link to a website.

        :param website: The website to link to\n
        :param text: The text to display\n
        :param title: The title of the window\n
        :param font: A tk.font.Font to use --Not in use\n
        """
        if not "background" in kwargs:
            kwargs["background"] = "white"
        super().__init__(parent, title, *args, **kwargs)

        """ if not font:
            font = Font(family="Helvetica", size=10) """
        style = ttk.Style()
        # Emulates the tk.Label look
        style.configure("TkMessageDialog.TLabel",background=kwargs["background"],)

        # The result of the dialog
        self.okorcancel = False

        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.focus_set()

        # Left of the dialog
        frame1 = ttk.Frame(self,style="TkMessageDialog.TLabel")
        # The informaton icon
        label=ttk.Label(frame1,image="::tk::icons::information",style="TkMessageDialog.TLabel")
        label.pack(side=tk.LEFT, anchor=tk.N)

        # Right of the dialog
        frame2 = ttk.Frame(self,style="TkMessageDialog.TLabel")
        ttk.Label(frame2, 
            text="Please go to this website\nand enter the following code:"
            ,anchor=tk.W, justify="left",style="TkMessageDialog.TLabel").pack(anchor="w")
        TkCopyableWeblink(frame2, text=website,font=font,style="TkMessageDialog.TLabel").pack()
        TkCopyableLabel(frame2, text=code,font=font,style="TkMessageDialog.TLabel").pack()

        # Bottom of the dialog
        frame3 = ttk.Frame(self)

        cancel_button=ttk.Button(frame3, text="Cancel", command=self._pressed_cancel)
        cancel_button.pack(side=tk.RIGHT, anchor=tk.E, padx=5, pady=5)

        ok_button=ttk.Button(frame3, text="OK", command=self._pressed_ok)
        ok_button.pack(side=tk.RIGHT, anchor=tk.E, padx=5, pady=5)

        frame1.grid(row=0, column=0, sticky=tk.N+tk.S+tk.W)
        frame2.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W,)
        frame3.grid(row=1, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

    def _pressed_ok(self):
        """
        Called when the OK button is pressed
        """
        self.okorcancel = True
        self.destroy()
    def _pressed_cancel(self):
        """
        Called when the Cancel button is pressed
        """
        self.okorcancel = False
        self.destroy()
    
    def get(self) -> bool:
        """
        Awaits user input and returns the result
        Returns True if OK was pressed, False if Cancel was pressed
        Must be called after the dialog is initialized

        :return: The result of the dialog\n
        """
        self.wait_window()
        return self.okorcancel

def message_dialog(parent: tk.Tk|tk.Toplevel,website:str,text:str, title: str = "",font:Font|None=None,*args, **kwargs) -> bool:
    """A message dialog that displays a code and a link to a website.
    The user can copy the code and click the link to go to the website.
    The dialog has two buttons, OK and Cancel.
    The dialog will return True if the OK button was pressed, and False if the Cancel button was pressed.
    
    :param parent: The parent window\n
    :param code: The text to display\n
    :param website: The website to link to\n
    :param title: The title of the window\n
    :param font: A tk.font.Font to use --Not in use\n

    :return: The result of the dialog\n
    """
    dialog = TkMessageDialog(parent, text, website, title, font, *args, **kwargs)#.show()
    
    return dialog.get()

if __name__ == "__main__":
    def testing():
        # Testing
        parent = tk.Tk()
        #tk.Text(parent).pack()
        def callback():
            
            from tkinter import messagebox
            hei = message_dialog(parent, "Hei der","https://www.google.com/devices", "Test")
            print(hei)
            #messagebox.askokcancel("Test", "Test\ntest\ntestTest\ntest\ntest")
        #TkWeblink(hei, text="Click me", link="https://www.google.com").pack()
        #TkCopyableWeblink(hei, text="Click me", link="https://www.google.com").pack()
        #TkCustomEntry(hei, text="this is an example").pack()
        #hei.center()

        tk.Button(parent, text="Click me", command=callback).pack()
        parent.mainloop()
    
    #testing()
    


