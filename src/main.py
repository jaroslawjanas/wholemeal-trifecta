import tkinter as tk
from tkinter import filedialog


def main():
    # Hide the root dialog window
    root = tk.Tk()
    root.withdraw()

    # Ask for file to open
    file_path = filedialog.askopenfilename()


if __name__ == '__main__':
    main()
