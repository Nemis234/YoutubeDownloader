import tkinter as tk
import tkinter.ttk as ttk
from tkinter.font import Font as tkFont
#Images
#import requests --Deprecated
from PIL import Image,ImageTk
import urllib, io
#Errors
from urllib.error import URLError
#Pathing
from os.path import dirname


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
    def __init__(self, parent, options: list, initial_value: str=None,font: tkFont = None):
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
            menu = parent.nametowidget(self.menuname)  # Get menu widget.
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

        self.var.trace("w", internal_callback)

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

class WebImage:
    def __init__(self, url:str,size:tuple[int,int]):
        self.size = size
        self.url = url
        self._orig_img = None
        self._image = None
        self.tkImage = None
        self.set_img(url)
        self.resize(size)

    def get_tkImage(self):
        """Returns an ImageTk.PhotoImage object"""
        self.tkImage = tkImage = ImageTk.PhotoImage(self._image)
        return self.tkImage
    
    def set_img(self,url):
        """In-place function, no return value"""
        try:
            with urllib.request.urlopen(url) as u:
                raw_data = u.read()
            img = Image.open(io.BytesIO(raw_data))
        except URLError:
            print("whoops")
            defaultThumbnail = dirname(__file__)+"\\defaultThumbnail.jpg"
            with open(defaultThumbnail,"rb") as f:
                img = Image.open(io.BytesIO(f.read()))
                

        self._image=self._orig_img = img
        
    
    def resize(self,size:tuple[int,int]=None,use_previous:bool=False):
        """In-place function, if no arguments are passed,
          returns current size"""
        img = self._orig_img
        if img == None:
            raise TypeError
        
        if not use_previous:
            self.size = size
            if not size:
                return self.size
        else:
            size = self.size
        
        self._image = img.resize(size)