from VideoDownload import MainWindow

if __name__ == "__main__":
    width = 1920
    height = 1080
    scale = 0.4
    gu = MainWindow((width,height),scale)
    print("STARTING")
    gu.mainloop()