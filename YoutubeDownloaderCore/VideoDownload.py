#Youtube downloader
from pytube import YouTube, request
#Pathing
from os import makedirs #,listdir --Deprecated
from os.path import dirname,exists
#Tkinter
import tkinter as tk
#import tkinter.ttk as ttk --Deprecated
from tkinter import messagebox, filedialog
from tkinter.font import Font as tkFont
#Processing
import multiprocess #Alternate to the default multiprocessing
import threading

#Custom tkinter widgets
from myCustomTkinter import DropDown, WebImage
#Oauth
from pytube.innertube import _cache_dir,_token_file,_client_id,_client_secret
import os,json,time
#Error handeling
from pytube import exceptions
from urllib.error import URLError
import http.client as httplib #Cheks for internet connection
#Other
from collections import defaultdict 

#Download GUI
from DownloadGUI import DownloadGUI


def cache_tokens(access_token, refresh_token, expires):
    """Cache an OAuth token. Modified method from pytube"""
    data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires': expires
    }

    if not os.path.exists(_cache_dir):
        os.mkdir(_cache_dir)
    with open(_token_file, 'w') as f:
        json.dump(data, f)

def fetch_bearer_token():
    """Fetch an OAuth token. Modified method from pytube\n\nWIP"""
    # Subtracting 30 seconds is arbitrary to avoid potential time discrepencies
    start_time = int(time.time() - 30)
    data = {
        'client_id': _client_id,
        'scope': 'https://www.googleapis.com/auth/youtube'
    }
    response = request._execute_request(
        'https://oauth2.googleapis.com/device/code',
        'POST',
        headers={
            'Content-Type': 'application/json'
        },
        data=data
    )
    response_data = json.loads(response.read())
    verification_url = response_data['verification_url']
    user_code = response_data['user_code']
    print(f'Please open {verification_url} and input code {user_code}')
    input('Press enter when you have completed this step.')

    data = {
        'client_id': _client_id,
        'client_secret': _client_secret,
        'device_code': response_data['device_code'],
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
    }
    response = request._execute_request(
        'https://oauth2.googleapis.com/token',
        'POST',
        headers={
            'Content-Type': 'application/json'
        },
        data=data
    )
    response_data = json.loads(response.read())

    access_token = response_data['access_token']
    refresh_token = response_data['refresh_token']
    expires = start_time + response_data['expires_in']
    cache_tokens(access_token=access_token, refresh_token=refresh_token, expires=expires)


class NoLink(Exception):
    def __init__(self) -> None:
        print("Input a valid link")
        super().__init__()

class NoConnection(Exception):
    def __init__(self) -> None:
        print("An error occured when connectiong to the internet")
        super().__init__()

class Size(tuple):
    def __init__(self) -> None:
        super().__init__()

class Stream:
    def __init__(self,yt:object,number:int, type:str="video", 
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
        string += f"File name: {self.get_full_name()}\n"
        string += f"Directory: {self.directory}\n"
        
        return string
    
    def set_directory (self,directory:str):
        self.directory = directory
    
    
    def make_prefix(self):
        i = 0

        if exists(self.directory+self.get_full_name()):
            while exists(self.directory + self.get_full_name()):
                i += 1
                self.prefix = "" if i == 0 else "("+str(i)+")"
                
        
        return self.prefix

    def get_full_name(self):
        name = ""
        if not self.prefix == None:
            name += self.prefix + " "
        name += self.filename
        if not self.postfix == None:
            name += "." + self.postfix
        
        return name

class WindowLayout(tk.Frame):
    def __init__(self,root:tk.Tk) -> tk.Frame:
        tk.Frame.__init__(self,root)
        self.root = root

        self.grid_columnconfigure(0, weight=1,uniform="fred")
        self.grid_columnconfigure(1, weight=1,uniform="fred")
        
        paddx = int(round(3))# * size_scale,0))
        paddy = int(round(4))# * size_scale,0))

        fontSize = int(round(15))# * size_scale,0))
        font = ("Arial",fontSize)
        
        url = "https://www.youtube.com/watch?v=0IhmkF50VgE"

        self.default_font = default_font = tkFont(font=font[0],size=fontSize)
        self.headline_font = headline_font = tkFont(font="Arial",size=int(round(fontSize*1.7,0)))
        self.path_font = path_font = tkFont(font=font[0],size=int(round(fontSize*0.7,0)))

        self.all_fonts = [default_font,headline_font,path_font]
        
        def type_dropdown_func(event=None,root:tk.Tk=None):
            key = dropdown_type.get()
            video_value = root.video_attributes[key]

            dropdown_aud.grid_remove()
            label_qual.grid_remove()

            root.audio_bool = False

            if key in list(root.audio_attributes.keys()):
                root.audio_bool = True

                audio_value = root.audio_attributes[key]
                numbers = [int("".join(x for x in hallo if x.isdigit())) for hallo in audio_value if hallo != None]
                numbers = list(dict.fromkeys(numbers))
                numbers.sort(reverse=True)
                audio_value = [str(x)+"kbps" for x in numbers]+["None"]
                dropdown_aud.update_options(audio_value)
                if len(audio_value) > 1:
                    dropdown_aud.config(state="normal")
                else:
                    dropdown_aud.config(state="disabled")

                dropdown_aud.grid()
                label_qual.grid()

            numbers = [int("".join(x for x in hallo if x.isdigit())) for hallo in video_value if hallo != None]
            numbers = list(dict.fromkeys(numbers))
            numbers.sort(reverse=True)

            video_value = [str(x)+"p" for x in numbers]
            video_value = video_value + ["None"] if root.audio_bool else video_value
            dropdown_vid_res.update_options(video_value)
            
            if len(video_value) > 1:
                dropdown_vid_res.config(state="normal")
            else:
                dropdown_vid_res.config(state="disabled")
    

        row = 1
        headline = tk.Label(self, text="YouTube nedlasting", font=headline_font)
        headline.grid(row=row,column=0,columnspan=2,pady=paddy,padx=paddx)
        
        row = 2
        video_label = tk.Label(self,text="Videolink eller ID: ", font=default_font)
        video_label.grid(row=row,column=0,pady=paddy,padx=paddx)

        self.yt_link_input = yt_link_input = root.yt_link_input = tk.Entry(self,font=default_font, width=20)
        yt_link_input.insert(0,"dQw4w9WgXcQ")#"0IhmkF50VgE")
        yt_link_input.grid(row=row,column=1,pady=paddy,padx=paddx)

        row = 3

        self.running_tasks = 0
        def do_tasks():
            if self.running_tasks > 1:
                return
            
            self.running_tasks += 1
            threading.Thread(target=root.submit_link, args=(None,self, )).start()
        
        self.submit_button = submit_button = tk.Button(self,text="Submit link",bg = MainWindow.button_color,font=default_font)
        submit_button.config(command=do_tasks)
        submit_button.grid(row=row,column=0,columnspan=2,pady=paddy,padx=paddx)
        
        frame=tk.Frame(self,highlightbackground="blue", highlightthickness=2)
        
        image_size = (int(round(192)),int(round(108)))
        imgUrl = f"https://img.youtube.com/vi/{url[url.find('watch?v=')+8:]}/maxresdefault.jpg"
        self.thumbnail_obj= WebImage(imgUrl,image_size)
        tk_thubmnail = self.thumbnail_obj.get_tkImage()

        self.thumbnail_label = thumbnail_label = tk.Label(frame,
                image=tk_thubmnail,highlightbackground="blue")#,width=image_size[0],height=image_size[1])
        thumbnail_label.image = tk_thubmnail
        thumbnail_label.pack()#anchor="nw",padx=1,pady=1)

        frame2 = tk.Frame(self, highlightbackground="blue")
        

        row = 1
        label = tk.Label(frame2,text="Filformat: ", font=default_font)
        label.grid(row=row,column=0,pady=paddy,padx=paddx)

        video_type_options = ["Placeholder"]

        self.dropdown_type = dropdown_type = DropDown(frame2,video_type_options,font=default_font)
        dropdown_type.add_callback(lambda: type_dropdown_func(root=root))
        dropdown_type.grid(row=row,column=1,pady=paddy,padx=paddx)
        

        row = 2
        label_res = tk.Label(frame2,text="Videooppløsning: ", font=default_font)
        label_res.grid(row=row,column=0,pady=paddy,padx=paddx)

        options_res = ["720p","480p","360p","240p","144p"]
        
        self.dropdown_vid_res=dropdown_vid_res = DropDown(frame2,options_res,font=default_font)
        dropdown_vid_res.grid(row=row,column=1,pady=paddy,padx=paddx)

        row = 3
        label_qual = tk.Label(frame2,text="Lydkvalitet: ", font=default_font)
        label_qual.grid(row=row,column=0,pady=paddy,padx=paddx)

        options_qual = ["70kbps","160kbps"]
        
        self.dropdown_aud = dropdown_aud = DropDown(frame2,options_qual,font=default_font)
        dropdown_aud.grid(row=row,column=1,pady=paddy,padx=paddx)

        frame.grid(row=4,column=1, sticky="n")#,pady=paddy*4)
        frame2.grid(row=4,column=0,columnspan=1)

        self.submit_button = submit_button = tk.Button(self, text="Submit", 
            command= lambda: root.start_download(frame=self), bg=MainWindow.button_color,font=default_font)
        submit_button.grid(row=5,column=0,pady=paddy,padx=paddx, columnspan=1)

        path_button = tk.Button(self, text="Change path", 
            command=lambda: root.change_path(frame=self), 
                bg=MainWindow.button_color,font=default_font)
        path_button.grid(row=5,column=0,pady=paddy,padx=paddx, columnspan=2)
        
        path_entry = tk.Entry(self,font=path_font, width=60)
        path_entry.insert(0,root.path)
        path_entry.config(state="readonly")
        
        path_entry.grid(row=6,column=0,pady=paddy,padx=paddx, columnspan=2)
        yt_link_input.focus_set()
        root.hide_show_widgets(True,self)

class MainWindow(tk.Tk):
    button_color = "#7b7b7b"
    size_scale = 1

    def __init__(self, size:tuple=(1920,1080),size_scale: float=0.4) -> tk.Tk:
        tk.Tk.__init__(self)

        self.x,self.y=x,y = size
        self.size = size_str = f"{int(round(x*size_scale,0))}x{int(round(y*size_scale,0))}"
        MainWindow.size_scale = size_scale
        
        directory = dirname(__file__)+"\\"

        if not exists(directory+"Downloads"):
            makedirs(directory+"Downloads")

        self.path = directory + "Downloads\\"

        self.layout = layout = WindowLayout(self)
        layout.pack(fill="both", expand=True)
        self = self.initPopup(self,size_str,focus=False, resizable=True)
        

        self.unbind_all("<Tab>")
        self.unbind_all("<<NextWindow>>")

        self.bind('<Return>', lambda event, arg1=layout: self.onKey(event, arg1))
        self.bind('<Tab>', lambda event, arg1=layout: self.onKey(event, arg1))
        self.bind('<Escape>', self.destroy_window)
        self.bind('<FocusIn>', self.raise_toplevel_windows)
        self.bind("<FocusOut>", self.raise_toplevel_windows)
                
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Configure>",lambda event, arg1=layout: self.window_state_changed(event,arg1))

        self.title("Download youtube")
        self.protocol('WM_DELETE_WINDOW',self.destroy_window)


        #Init all variables
        self.video_type_options = list()
        self.audio_type_quality = list()
        self.video_type_res = list()

        self.yt = None
        self.link = ""
        self.streams = None

        self.audio_bool = False

        self.focusedout = False
        self.window_configure_count = 0

        self.video_attributes = defaultdict(list)
        self.audio_attributes = defaultdict(list)

        if not self.have_internet(): 
            if messagebox.askretrycancel("No connection","No connection to YouTube found"):
                self.retry_setup(None,layout)
            else:
                self.destroy()
                return
    
    def change_path(self,event=None,frame:tk.Frame=None):
        path = filedialog.askdirectory()
        if path:
            self.path = path
            frame.path_entry.config(state="normal")
            frame.path_entry.delete(0, tk.END)  # Empty the path_entry
            frame.path_entry.insert(0, path)
            frame.path_entry.config(state="readonly")
        return
     
    def onKey(self,event=None,frame:tk.Frame=None):
        if not frame:
            return
        main_widgets = frame.winfo_children()
        iterate_widgets = []

        for widget in main_widgets:
            if not widget.winfo_ismapped():
                continue

            if "!frame" in str(widget):
                frame_widgets = widget.winfo_children()

                if len(frame_widgets) <= 1:
                    continue

                for sub_widget in frame_widgets:
                    if "!label" in str(sub_widget) or not sub_widget.winfo_ismapped():
                        continue
                    
                    iterate_widgets.append(sub_widget)
                
                continue
        
            if any([check in str(widget) for check in ["!label","!frame"]]):
                continue
            iterate_widgets.append(widget)  
            
        main_widgets = iterate_widgets
        focused_widget = frame.focus_get()
        print(focused_widget)

        if event.keysym == "Return":
            for widget in main_widgets:
                    if widget == focused_widget and "!button" in str(widget):
                        return widget.invoke()

        def nextToFocus(focused_widget,liste,event):
            for i in range(len(liste)):
                if focused_widget == liste[i]:
                    if event.state == 9:
                        if i == 0:
                            return -1
                        return i - 1
                
                    if liste[i] == liste[-1]:
                        return 0
                    return i+1

        return main_widgets[nextToFocus(focused_widget,main_widgets,event)].focus_set()
    
    def submit_link(self,event=None,frame:tk.Frame=None):
        yt_streams, yt, link = None,None,None
        def placeholder(*a,**kw):
            print("hi")
        
        def getYtObject():
            link = frame.yt_link_input.get()

            if link.lower() == "placeholder":
                frame.running_tasks -= 1
                raise NoLink
            
            valid = ["youtube.com/watch?v=",
                        "youtube.com/embed/",
                        "youtu.be/"]
            
            try:
                if not any([(True if x in link else False) for x in valid]):
                    link = "youtube.com/watch?v=" + link 
            except TypeError as error:
                frame.running_tasks -= 1
                raise NoLink
            try:
                if os.path.exists(_token_file):
                    with open(_token_file) as f:
                        data = json.load(f)
                        access_token = data['access_token']
                if not access_token:
                    fetch_bearer_token()
            except:
                print("Failed to fetch token")
            
            if not self.have_internet():
                raise NoConnection
            try:

                yt = YouTube(link,on_progress_callback=placeholder,on_complete_callback=placeholder,
                                use_oauth=True, allow_oauth_cache=True)
                streams = yt.streams
            
            except exceptions.RegexMatchError:
                raise NoLink
            except exceptions.AgeRestrictedError:
                messagebox.showwarning("Agerestricted","This video is age restricted\nDownload unavailable")
                raise Exception
            except exceptions.VideoUnavailable as e:
                messagebox.showwarning("Video unavailable",e.error_string())
                raise Exception
            except URLError as e:
                messagebox.showwarning("Network error",f"A network error has occured with the following exception:\n{e}")
                raise Exception
            except Exception as e:
                messagebox.showwarning("Unknown error",f"An unknown error has occured:\n{e}")
                raise Exception
            
            streams=yt.streams

            return yt,streams,link
        
        if not self.link or not self.link.split("?v=")[-1] == frame.yt_link_input.get().split("?v=")[-1]:
            try:
                yt_link_bundle = getYtObject()
                if not yt_link_bundle:
                    messagebox.showwarning("Unknown error",f"An unknown error has occured\n Please try again")
                    raise Exception
                self.yt,self.streams,self.link = yt,yt_streams,link = yt_link_bundle
            
            except NoLink:
                messagebox.showwarning("Invalid input","Invalid link submited\nPlease try again")
                frame.running_tasks -= 1
                return
            except NoConnection:
                messagebox.showerror("No connection","No connection to YouTube found\nTry again later")
                frame.running_tasks -= 1
                return
            except Exception:
                frame.running_tasks -= 1
                return
            
        else:
            yt_streams = self.streams
        streams = []
        if yt_streams == None or yt==None:
            return
        
        for x in yt_streams:
            single_stream = []

            try:
                single_stream.append(x.itag)
            except: single_stream.append(None)
            try:
                single_stream.append(tuple(x.mime_type.split("/")))
            except: single_stream.append(None)
            try:
                single_stream.append(x.resolution)
            except: single_stream.append(None)
            try:
                single_stream.append(x.abr)
            except: single_stream.append(None)
            """ try:
                hei.append(x.acodec)
            except: hei.append(None) """
            streams.append(single_stream)
        video_streams = [x for x in streams if x[1][0] == "video"]
                                            #Stream_number file_type video_quality audio_quality, only video         Video with audio
        self.video_type_res = video_type_res = [(x[0]      ,x[1][1],   x[2]) if       x[3] ==    None else (x[0],f"{x[1][1]} (w/audio)",x[2]) for x in video_streams]

        audio_streams = [x for x in streams if x[1][0] == "audio"]
        self.audio_type_quality = audio_type_quality = [(x[0],x[1][1],x[3]) for x in audio_streams]
        
        for number, types,res in video_type_res:
            self.video_attributes[types].append(res)
        for number,types,quality in audio_type_quality:
            self.audio_attributes[types].append(quality)

        self.audio_attributes = dict(self.audio_attributes)

        self.video_attributes = video_attributes = dict(self.video_attributes)            

        video_type_options = list(video_attributes.keys())
        video_type_options.sort()
        frame.dropdown_type.update_options(video_type_options)
        
        if not self.have_internet():
            messagebox.showerror("No connection","No connection to YouTube found\nTry again later")
            return
        url = self.link
        imgUrl = f"https://img.youtube.com/vi/{url[url.find('watch?v=')+8:]}/maxresdefault.jpg"
        frame.thumbnail_obj.set_img(imgUrl)
        frame.thumbnail_obj.resize(use_previous=True)
        thumbnail_photo = frame.thumbnail_obj.get_tkImage()
        thumbnail_label = frame.thumbnail_label
        thumbnail_label.config(image=thumbnail_photo)
        thumbnail_label.image = thumbnail_photo

        self.hide_show_widgets(False,frame)
        
        frame.running_tasks -= 1
        return 

    def start_download(self,event=None,frame:tk.Frame=None):
        vid_type = frame.dropdown_type.get()
        vid_qual = frame.dropdown_vid_res.get()
        aud_qual = frame.dropdown_aud.get()

        audio_number = video_number = will_concate = False

        dictionary = self.video_type_res


        if all(item == "None" for item in [vid_qual,aud_qual]):
            return messagebox.showerror("Option-error","No option selected\nSelect an option to proceed")

        yt = self.yt
        filename = yt.streams[0].title
        invalid = '<>:"/\|?*' #Invalid characters in windows filenames
        filename = "".join([x for x in filename if x not in invalid])
        stream_objects = []

        if vid_qual != "None":
            for number,string,quality in dictionary:
                if string == vid_type and quality == vid_qual:
                    video_number = number

            stream_objects.append(Stream(yt,video_number,"video",filename))

        if self.audio_bool and aud_qual != "None":
            dictionary = self.audio_type_quality

            for number,string,quality in dictionary:
                if string == vid_type and quality == aud_qual:
                    audio_number = number
            
            stream_objects.append(Stream(self.yt,audio_number,"audio","Audio "+filename))
            
            pass

            if video_number and audio_number:
                if False:
                    message = messagebox.askquestion("Two files", f"Two file-downloads detected\nDo you want to combine the files?")
                    will_concate = True if message == "yes" else False
                else:
                    will_concate = False
                
                #return self.initDownload(self.yt,video_number,audio_number,will_concate)
            if audio_number and not video_number:
                pass
                #return self.initDownload(self.yt,audio_stream_no=audio_number)
        
        if len(stream_objects) == 0:
            return -1
        
        return self.initDownload(self.yt,stream_objects,will_concate,self.path)

    def hide_show_widgets(self,hide=True,frame:tk.Frame=None):
        liste = frame.winfo_children()

        if hide:
            for i in range(len(liste)):
                if i > 3:
                    liste[i].grid_remove()
        else:
            for i in range(len(liste)):
                if i > 3:
                    liste[i].grid()


    def initPopup(self:object=None, root:tk.Tk = None,wid:str="300x400", focus:bool=False, title: str = "", resizable:bool = False):
        """Lager et tkinter vindu sentrert på skjermen, uansett størrelse. 
        Hvis root ikke er definert, leger et nytt vindu som blir lukket når hovedvinduet lukkes
        \n:focus: om vinduet skal lukkes når brukeren klikker av
        \n:root: tkinter vinduet som skal bli modifisert, ofte hovedvinduet
        \n:title: tittelen på vinduet"""

        def center(win:tk.Tk):
            """
            centers a tkinter window on the monitor
            :param win: the main window or Toplevel window to center
            """
            win.update_idletasks()
            width = win.winfo_width()
            frm_width = win.winfo_rootx() - win.winfo_x()
            win_width = width + 2 * frm_width
            height = win.winfo_height()
            titlebar_height = win.winfo_rooty() - win.winfo_y()
            win_height = height + titlebar_height + frm_width
            x = win.winfo_screenwidth() // 2 - win_width // 2
            y = win.winfo_screenheight() // 2 - win_height // 2
            win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            #win.deiconify()

        def lossfocus(event):
            """Lukker vinduet hvis brukeren klikker av tkinter-vinduet"""
            if event.widget is tkPopup:
                w = tkPopup.tk.call('focus')
                if not w:
                    tkPopup.destroy()
        
        if root == None:
            tkPopup = tk.Toplevel()
            tkPopup.title(title)
        else:
            tkPopup = root
            #self = tkPopup
        tkPopup.geometry(wid)
        tkPopup.resizable(resizable,resizable)
        center(tkPopup)
        if focus:
            tkPopup.bind('<FocusOut>', lossfocus)

        if root == None:
            return tkPopup

        return tkPopup

    def raise_toplevel_windows(self,event=None):
        if event == "<FocusIn>" and self.focusedout:
            self.focusedout = False
            for window in self.winfo_children():
                if isinstance(window, tk.Toplevel):
                    window.lift()
        if event == "<FocusOutn>":
            self.focusedout = True

    def destroy_window(self,event=None):
        children = multiprocess.active_children()

        if len(children) > 0:
            yes_no = messagebox.askyesno("Closing","Are you sure you want to end all processes?")
            if yes_no:
                print("Terminating")
                for child in multiprocess.active_children():
                    child.terminate()
                self.destroy()
            return
        self.destroy()
    
    def have_internet(self):
        conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
        try:
            conn.request("HEAD", "/")
            return True
        except Exception:
            return False
        finally:
            conn.close()
 
    def retry_setup(self,event=None,frame:tk.Frame=None):
        if not frame:
            return
        def destroy_widgets(frame):
            for widget in frame.winfo_children():
                if "!frame" in str(widget):
                    destroy_widgets(widget)
                else:
                    widget.destroy()

        #destroy_widgets(self)
        while not self.have_internet(): 
            if not messagebox.askretrycancel("No connection","No connection to YouTube found"):
                self.destroy()
                return
                
        #self.layout = WindowLayout(self,self.size_scale)
        #self.layout.pack()
        return

    def toggle_fullscreen(self, event=None):
        if self.state()=='zoomed':
            self.state('normal')
        else:
            self.state('zoomed')
        return

    def window_state_changed(self,event=None,frame:tk.Frame=None):
        def resize_text(i,k):
            i = int(i*k)
            if i == frame.default_font.config()["size"]:
                return
            
            for font in frame.all_fonts:
                font.config(size=i)
            
            frame.headline_font.config(size=int(round(i*1.7,0)))
            frame.path_font.config(size=int(round(i*0.7,0)))

        def resize_img(size,k):
            width, height = size
            new_size = (int(width*k),int(height*k))
            if frame.thumbnail_obj.size == new_size:
                return
            thumb_size = new_size
            frame.thumbnail_obj.resize(thumb_size)

            thumbnail_photo = frame.thumbnail_obj.get_tkImage()

            frame.thumbnail_label.config(image=thumbnail_photo)
            frame.thumbnail_label.image = thumbnail_photo
        
        if self.state() == "zoomed" and self.window_configure_count > 0:
            self.window_configure_count = 0
        if self.state() == "normal" and self.window_configure_count < 1:
            self.geometry(self.size)

            self.window_configure_count = 1
        
        i = 10/3
        w = self.winfo_width()
        h = self.winfo_height()
        k = 1 + min(w, h) / 100 
        size = (int(192/3),int(108/3))
        
        resize_text(i,k)
        resize_img(size,k)

    def initDownload(self,yt:object,stream_objects:list[Stream],will_concate:bool = False,path:str=""):
        
        if not path:
            directory = dirname(__file__)+"\\"

            if not exists(directory+"Downloads"):
                makedirs(directory+"Downloads")

            directory = directory + "Downloads\\"
        else:
            directory = path + "\\"
        
        for stream in stream_objects:
            stream.set_directory(directory)
        print(directory)
        print(stream_objects[0].directory)
        
        if not self.have_internet():
            if messagebox.askretrycancel("No connection","No connection to YouTube found\nTry again later"):
                return self.initDownload(yt,stream_objects,will_concate,directory)
            return
        
        print(f"Starting download, numbers :{stream_objects}")

        #Deprecated #threading.Thread(target=run_download,args=(None,stream_objects,will_concate)).start()
        new_process = multiprocess.Process(target=run_download,args=(None,stream_objects,will_concate,MainWindow.size_scale,MainWindow.button_color))
        new_process.start()


def run_download(root:tk.Tk=None,stream_objects:Stream=None,will_concate:bool=None,size_scale:float = 1, button_color:str = "white"):
    DownloadGUI(root,stream_objects,will_concate,size_scale,button_color)

if __name__ == "__main__":
    gu = MainWindow()
    print("STARTING")
    gu.mainloop()
    "https://www.youtube.com/watch?v=PAI9NIbNgk4"
    "linus"
    "https://www.youtube.com/watch?v=0IhmkF50VgE"