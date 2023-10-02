""" from moviepy.editor import *

from os.path import dirname
directory = dirname(__file__)+"/"
path1 = directory
path2 = directory
output = "testing.mp4"

videoclip = VideoFileClip(path1)
audioclip = AudioFileClip(path2)

new_audioclip = CompositeAudioClip([audioclip])
videoclip.audio = new_audioclip
videoclip.write_videofile(output)
b ruh

 """