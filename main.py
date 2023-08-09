# main.py

import os
import tkinter
from presenter import Presenter
from view import View

def main():
    window = tkinter.Tk()
    window.geometry("600x800")
    presenter = Presenter(None)
    view = View(window, presenter)
    presenter.view = view
    window.mainloop()

if __name__ == "__main__":
    print(os.getcwd())
    main()
