from VideoDownload import MainWindow

if __name__ == "__main__":
    width = 640
    height = 360
    scale = 1
    gu = MainWindow((width,height),scale)
    print("STARTING")
    gu.mainloop()