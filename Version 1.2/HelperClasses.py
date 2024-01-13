from pytube import YouTube
#Pathing
from os.path import exists, dirname
#Images
#import requests --Deprecated
from PIL import Image,ImageTk
import io
from urllib.request import urlopen
#Errors
from urllib.error import URLError

class Stream:
    def __init__(self,yt:YouTube,number:int, type:str="video", 
                 filename:str=None, prefix:str=None, postfix:str=None) -> None:
        self.yt = yt
        self.type = type
        self.number = number
        self.filename = filename
        self.prefix = prefix
        self.postfix = postfix
        self.directory = None

    def __str__(self) -> str:
        string = ""
        string += f"Yt object: {self.yt}\n"
        string += f"Type: {self.type}\n"
        string += f"Stream number: {self.number}\n"
        string += f"File name: {self.full_name}\n"
        string += f"Directory: {self.directory}\n"
        
        return string
    
    @property
    def full_name(self):
        name = ""
        if not self.prefix == None:
            name += self.prefix + " "
        name += self.filename
        if not self.postfix == None:
            name += "." + self.postfix
        
        return name

    def make_prefix(self):
        i = 0

        if exists(self.directory+self.full_name):
            while exists(self.directory + self.full_name):
                i += 1
                self.prefix = "" if i == 0 else "("+str(i)+")"
        
        return self.prefix
    
    def set_directory (self,directory:str):
        self.directory = directory
    
class WebImage:
    """Class for handling images from the web"""
    def __init__(self, url:str,size:tuple[int,int]):

        self.size = size
        self.url = url
        self._orig_img = None
        self._image = None
        self._tkImage = None
        self.set_img(url)
        self.resize(size)
    def __str__(self):
        string = ""
        string += f"URL: {self.url}\n"
        string += f"Size: {self.size}\n"
        return string
    @property
    def tkImage(self):
        """Returns an ImageTk.PhotoImage object"""
        
        self._tkImage = ImageTk.PhotoImage(self._image)
        return self._tkImage
    
    def set_img(self,url:str):
        """In-place function, no return value"""
        try:
            with urlopen(url) as web:
                raw_data = web.read()
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
