# Goal: Function which allows you to choose a file from a pop up window
# Tkinter

import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

print(file_path)
