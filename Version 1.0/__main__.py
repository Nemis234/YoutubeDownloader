from VideoDownload import MainWindow

if __name__ == "__main__":
    width = 1920*40/100
    height = 1080*40/100
    scale = 1
    gu = MainWindow((width,height),scale)
    print("STARTING")
    gu.mainloop()