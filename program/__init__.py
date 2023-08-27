import tkinter as tk
from tkinter import ttk
from program.podcastGUI import PodcastGUI
from program.summerizeGUI import SummarizeGUI

class Program:
    def __init__(self, root):
        # GUI BLOCK
        self.root = root
        self.root.title("Audio/Video Downloader & Summarizer")
        self.root.geometry("600x320+500+150")
        self.root.config(background="#f0f0f0")
        self.root.resizable(0,0)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Download tab
        download_tab = tk.Frame(self.notebook)
        download_gui = PodcastGUI(self.root, download_tab) # Add widgets to download_tab
        self.notebook.add(download_tab, text="Podcast")

        # Summarize tab
        summarize_tab = tk.Frame(self.notebook)
        summarize_gui = SummarizeGUI(self.root, summarize_tab) # Add widgets to summarize tab
        self.notebook.add(summarize_tab, text="Summarize")