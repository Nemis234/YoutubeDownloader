class NoLink(Exception):
    def __init__(self) -> None:
        print("Input a valid link")
        super().__init__()

class NoConnection(Exception):
    def __init__(self) -> None:
        print("An error occured when connectiong to the internet")
        super().__init__()
