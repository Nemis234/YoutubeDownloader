from VideoDownload import MainWindow

if __name__ == "__main__":
    width = 450
    height = 280
    scale = 1.5
    gu = MainWindow((width,height),scale)
    print("STARTING")
    gu.mainloop()