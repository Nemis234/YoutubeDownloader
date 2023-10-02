from pytube import request
#Pathing
from os import remove
from os.path import exists
#Tkinter windows
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
#Merging files
from moviepy.editor import *
import subprocess
#Other
import threading
import time
import sys

from proglog import default_bar_logger


class PrintLogger(): # create file like object
    def __init__(self, textbox): # pass reference to text widget
        self.textbox = textbox # keep ref

    def write(self, text):
        self.textbox.delete("1.0",tk.END)
        self.textbox.insert(tk.END, text) # write text to textbox
            # could also scroll to end of textbox here to make sure always visible

    def flush(self): # needed for file like object
        pass

from proglog import TqdmProgressBarLogger

class MyBarLogger(TqdmProgressBarLogger):
    percentage = 0
    def __init__(self,ui):
        super().__init__(init_state=None, bars=None, ignored_bars=("chunk"),print_messages=False,
                    logged_bars='all', min_time_interval=0.5, ignore_bars_under=100)
        self.ui = ui
    
    def callback(self, **changes):
        # Every time the logger is updated, this function is called
        try:
            if len(self.bars):
                x,y = (next(reversed(self.bars.items()))[1]['index']
                ,next(reversed(self.bars.items()))[1]['total'])
                print(x,y)
                self.percentage = percentage = (x/y)*100
                """ sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__ """
                self.ui.percent = percentage
                self.ui.update_progress()
                print(self.percentage)
                """ logging.basicConfig(level=logging.DEBUG)
                logging.basicConfig(level=logging.CRITICAL) """
                
        except KeyError:
            print("keyerror")
            pass
        except Exception:
            print("ops")


class DownloadGUI(): 
    num_bars = 0
    numb = 0
    def __init__(self,root:tk.Misc,package:tuple=(object,int|None,int|None,dir,str),will_concate:bool = False):
        ## Make the GUI
        if not root == None:
            self.size_scale = size_scale = root.size_scale
            self.root = tk.Toplevel(root)
            button_color = root.button_color
        else:
            self.size_scale = size_scale = 1
            self.root = tk.Tk()
            button_color = "white"
        
        self.root.title()
        x,y = int(round(210*size_scale,0)),int(round(60*size_scale,0))
        self.root.geometry(f"{x}x{y}")

        fontSize = int(round(10*size_scale,0))
        font = ("Arial",fontSize)

        self.style = style = ttk.Style(self.root)
        style.layout('text.Horizontal.TProgressbar',
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
        style.configure('text.Horizontal.TProgressbar', text='0 %', font=font)

        self.percent = 0
        self.progress = ttk.Progressbar(self.root,style='text.Horizontal.TProgressbar', orient = 'horizontal', length = int(round(200*size_scale,0)), mode = 'determinate', max = 100)
        DownloadGUI.num_bars += 1

        yt,video_stream_no,audio_stream_no,directory,filename = package
        self.package = package

        self.start = 2
        self.end = 2
        self.filesize = 0
        self.total_downloaded = 0

        if audio_stream_no == None or video_stream_no == None:
            self.start = 1
            self.end = 1

        self.stop = False
        self.cancel_all = False
        self.cancelled_count = self.end

        self.will_concate = will_concate
        self.concated = False
        self.paths = []
        

        ## Bind an event to trigger the update
        self.root.bind('<<MoveIt>>', self.update_progress)
        self.root.bind('<<Destroy_gui>>',self.destroy_gui)

        ## Pack the progress bar in to the GUI
        self.progress.pack()

        def canceled(event=None):
            self.stop = True
            s = "s" if len(self.paths) > 1 else ""
            yes_no = messagebox.askyesno("Cancelled",f"Download canceled\nDo you want to delete the file{s}?")
            if yes_no:
                self.cancel_all = True
                failsafe = 5
                while self.cancelled_count>0:
                    time.sleep(0.5)
                    if not failsafe > 0:
                        print("Something went wrong!")
                        sys.stdout = sys.__stdout__
                        sys.stderr = sys.__stderr__ 
                        self.root.destroy()
                        return
                    failsafe-=1
                for path in self.paths[1:]:
                    remove(path[0])
                self.root.destroy()

        button = tk.Button(self.root,text="Cancel",command=canceled,bg = button_color,font=font)
        button.pack()

        self.concate_thread=None


    def run(self):
        yt,video_stream_no,audio_stream_no,directory,filename = self.package

        isaudio = False
        DownloadGUI.numb = 1

        def make_prefix(directory,filename):
            #Makes prefix

            i = 0
            prefix = "" if i == 0 else "("+str(i)+") "

            if exists(directory+filename):
                while exists(directory + prefix + filename):
                    i += 1
                    prefix = "" if i == 0 else "("+str(i)+") "
            
            return prefix

        if not video_stream_no == None:
            stream = yt.streams.get_by_itag(video_stream_no)
            filetype = stream.mime_type.split("/")[1]
            print("vid type",filetype)
            video_filename = f"{filename}.{filetype}"

            video_prefix = make_prefix(directory,video_filename)

            vid_package = ((yt,video_stream_no,directory,video_prefix,isaudio,video_filename))
            vid_work = DownloadThread(self,vid_package,DownloadGUI.numb)
            DownloadGUI.numb+=1
            vid_work.start()

        if not audio_stream_no == None:
            isaudio=True

            stream = yt.streams.get_by_itag(audio_stream_no)
            filetype = stream.mime_type.split("/")[1]
            print("aud type",filetype)
            aud_filename = f"Audio {filename}.{filetype}"

            audio_prefix = make_prefix(directory,aud_filename)

            aud_package = ((yt,audio_stream_no,directory,audio_prefix,isaudio,aud_filename))
            aud_worker = DownloadThread(self,aud_package,DownloadGUI.numb)
            aud_worker.start()
        ## Enter the main GUI loop. this blocks the main thread
        #self.root.mainloop()

    ## Updates the progress bar
    def update_progress(self, event=None):

        ## If the new value is less than 100
        if self.percent <= 100:
            print('[main thread] New progress bar value is ' + str(self.percent))
            ## Update the progress bar value
            self.progress.config(value = self.percent)
            self.style.configure('text.Horizontal.TProgressbar',
                        text='{:g} %'.format(self.percent))

        ## If the new value is more than 10
        else:
            print('[main thread] Progress bar done. Exiting!')
            ## Exit the GUI (and terminate the script)
            if not self.will_concate:
                self.destroy_gui()

    def def_file_size(self,size):
        self.filesize += size

    def update_percent(self,downloaded=None):
            if downloaded:
                self.total_downloaded += downloaded
                current = self.total_downloaded/self.filesize
            else:
                current = 0
            
            percent = int(round(current*100,0))
            self.percent = percent

    def concate_files(self, event=None):
        if self.end > 0:
            return
        print("Merging")
        
        """ t = tk.Text(self.root, width=int(round(200*self.size_scale,0)))
        t.pack()
        pl = PrintLogger(t)
        sys.stderr = pl """

        paths = self.paths
        print(f"\nDownload has completed successfully, size: {round((self.filesize/1024)/1024,1)} MB")

        audioPath = paths[1][0]
        videoPath = paths[2][0]

        if paths[2][1]:
            audioPath,videoPath = videoPath,audioPath
        
        def moviepy_con(videoPath,audioPath, logger):
            videoclip = VideoFileClip(videoPath)
            audioclip = AudioFileClip(audioPath)

            new_audioclip = CompositeAudioClip([audioclip])

            videoclip.audio = new_audioclip

            videoclip.write_videofile(paths[0],threads=3, logger = logger)
            videoclip.close()
            audioclip.close()
            return True

        #videoclip.write_videofile()
        print("hei")
        """ f = open(os.devnull, 'w')
        sys.stdout = f
        sys.stderr = f """
        print("hade")
        #f.close()
        hei = MyBarLogger(self)

        running = True

        self.concate_thread= threading.Thread(target=moviepy_con,args=(videoPath,audioPath,hei))
        self.concate_thread.deamon = True
        self.concate_thread.start()
        while running:
            time.sleep(0.5)
        print("merged")
        
        self.concated = True


        self.destroy_gui()
        return

    def concatenate_files(video_file, audio_file, output_file):
        return
        # Run MoviePy command as a subprocess
        command = f'moviepy -i "{file1}" -i "{file2}" -filter_complex concat -c:v libx264 -crf 23 -c:a aac -b:a 192k "{output_file}"'
        process = subprocess.Popen(command, shell=True)

        # Wait for the process to finish (optional)
        process.wait()

        # Delete the unconcatenated files
        os.remove(file1)
        os.remove(file2)

        # Check if the process is still running
        if process.poll() is None:
            # Terminate the process
            process.terminate()


    def destroy_gui(self,event=None):
        if self.concated:
            paths = self.paths
            for i in paths[1:]:
                remove(i[0])
        self.root.destroy()


class DownloadThread(threading.Thread):
    """
    Threaded class. For downloading the specified download type, either video or audio
    """
    def __init__(self,ui:tk.Misc,package:tuple=(object,int|None,dir,tuple:=("",""),bool,str),numb:int = 0):
        threading.Thread.__init__(self)
        self.numb = numb
        self.daemon = True
        self.is_paused = self.is_cancelled = False

        self.ui = ui
        self.package = package

        self.ui.root.protocol("WM_DELETE_WINDOW", self.pause_thread)
        self.ui.root.bind("<<pause_thread>>",self.pause_thread)
        self.ui.root.bind("<<start_thread>>",self.resume_thread)

    def pause_thread(self,event=None):
        if not self.is_paused:
            self.is_paused = True
    def resume_thread(self,event=None):
        if self.is_paused:
            self.is_paused = False


    def run(self):
        yt,stream_numb,directory,prefix,isaudio,filename = self.package
        print(yt)
        self.is_paused = self.is_cancelled = False
        

        def progress_function(stream=None,chunk=None, bytes_remaining=None,total_downloaded = None,downloaded=None):
            self.ui.update_percent(downloaded)
            self.ui.root.event_generate('<<MoveIt>>')


        def complete_function(stream, path):
            time.sleep(1)
            self.ui.end -= 1
            if len(self.ui.paths) > 2 and self.ui.will_concate:
                print("concating")
                self.ui.concate_files()

        
        """ try:
            yt.register_on_progress_callback = progress_function
            yt.register_on_complete_callback = complete_function
        except:
            return print("Skriv en gyldig link") """

        print("Downloading...")

        progress_function(False)

        stream = yt.streams.get_by_itag(stream_numb)

        if stream == None:
            self.ui.root.destroy()
            raise TypeError("Download not found")

        if yt == None:
            self.ui.root.destroy()
            raise TypeError("Download not found")
        
        filetype = stream.mime_type.split("/")[1]

        self.filesize = stream.filesize
        print(f"Filstørrelse: {(self.filesize/1024)/1024} MB")
        #invalid = '<>:"/\|?* '
        #filename = "".join([x for x in filename if x not in invalid])
        
        filename = f"{prefix}{filename}"

        if not isaudio:
            path = f"{directory}{filename}"
            self.ui.paths.append(path)

            #prefix += "Video"
            #filename = f"{prefix}{s}.{filetype}"

        path = f"{directory}{filename}"

        self.ui.def_file_size(self.filesize)

        try:
            with open(path, 'wb') as f:
                stream = request.stream(url=stream.url) # get an iterable stream
                self.ui.paths.append((path,isaudio))
                downloaded = 0
                i = 0
                self.ui.start -= 1
                while True:
                    if self.is_cancelled or self.ui.cancel_all:
                        self.ui.cancelled_count -= 1
                        break
                    if self.ui.start > 0 or self.is_paused:

                        time.sleep(1)
                        continue
                    if self.ui.stop:
                        time.sleep(0.5)
                        continue
                    i += 1
                    chunk = next(stream,None) # get next chunk of video
                    if chunk:
                        downloaded = len(chunk)
                        progress_function(downloaded=downloaded)
                        f.write(chunk)
                    else:
                        # no more data
                        print("completed",prefix)
                        complete_function(stream,path)
                        break
            print(4)
                
            if self.is_cancelled:
                if messagebox.askokcancel("Canceled", "Download canceled\nDo you want to delete the file?"):
                    remove(path)

            if not self.ui.end > 0 and not self.ui.will_concate:
                print("destroying download bar")
                self.ui.destroy_gui()
        
        
        except KeyError as e:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__ 
            print("An error has occurred\n",e)
            h = "s" if len(self.ui.paths) > 1 else ""
            if messagebox.askokcancel("Error", f"An error has occured\nDo you want to delete the file{h}?"):
                for path,_ in self.ui.paths:
                    remove(path)

if __name__ == "__main__":

    from pytube import YouTube
    from os.path import dirname, exists
    from os import makedirs, listdir
    link = "dQw4w9WgXcQ"
    video_type_res = []
    audio_type_quality = []
    video_attributes = []
    audio_attributes = []
    yt_obj = None


    def submit_link(event=None):
        global yt_obj,link
        def placeholder(*a,**kw):
            print("hi")
        
        def getYtObject():
            print("uoahfiueiuf")
            
            ny_link = "youtube.com/watch?v=" + link


            print("WHYYY")
            yt = YouTube(ny_link,on_progress_callback=placeholder,on_complete_callback=placeholder)
            print("yptube",yt)
            streams=yt.streams
            try:
                pass

            except Exception as error:
                print("feil")

            return yt,streams
        
        yt_obj,yt_streams = getYtObject()
        


    def initDownload(yt:object,video_stream_no:int=None, audio_stream_no:int=None,will_concate:bool = False):
        directory = dirname(__file__)+"\\"

        if not exists(directory+"Downloads"):
            makedirs(directory+"Downloads")

        directory = directory + "Downloads\\"
        i = 0
        for file in listdir(directory):
            if exists(directory+file):
                i+=1
        
        prefix = "" if i == 0 else "("+str(i)+") "
        print("init",yt," directory:",directory, " file", prefix)
        DownloadGUI(None,(yt,video_stream_no,audio_stream_no,directory,prefix),will_concate).run()

    submit_link()
    initDownload(yt_obj,17,None,False)