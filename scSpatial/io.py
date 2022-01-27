def select_file() -> str:
    """Opens a file select window and return the path to selected file"""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()

    return file_path


if __name__ == "__main__":
    path = select_file()
    print(path)
