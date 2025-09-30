#!/usr/bin/env python3
import tkinter as tk
from functioning_analyzer.gui import AnalyzerApp
from tkinter import ttk


def main():
    root = tk.Tk()
    app = AnalyzerApp(root)
    style = ttk.Style()
    style.theme_use('clam')
    root.mainloop()


if __name__ == "__main__":
    main()


