import tkinter as tk
from tkinter import messagebox, filedialog
import sys
import threading
from program.youtube import YoutubeDownloader


class ConsoleRedirector:
    # Print output to text widget rather than console
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        # print = stdout.write() 
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)

    def flush(self):
        # In order to flush the output present in buffer
        self.text_widget.update_idletasks()


class YoutubeGUI:
    def __init__(self, root, youtube_tab):
        self.root = root
        self.youtube_tab = youtube_tab

        # Main Title Label
        self.title = tk.Label(self.youtube_tab, text="Youtube Downloader", font="bold 22", fg="white",
                         bg="#001F54", width=600, pady=10)
        self.title.pack()

        # Frame
        self.main_frame = tk.Frame(self.youtube_tab, padx=20, pady=30)
        self.main_frame.pack()

        # Widgets in Frame
        self.url_label = tk.Label(self.main_frame, text="Youtube Video URL:", font=("Arial", 12))
        self.url_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.url_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=35, bd=2)
        self.url_entry.grid(row=0, column=1)

        self.location_label = tk.Label(self.main_frame, text="Download Location:", font=("Arial", 12))
        self.location_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.location_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=28, bd=2)
        self.location_entry.grid(row=1, column=1, sticky="w")
        self.browse_button = tk.Button(self.main_frame, text="Browse", command=self.browse, font=("Arial", 10))
        self.browse_button.grid(row=1, column=1, padx=(5,0), sticky="e")

        # Radio Buttons for selecting download type
        self.download_type = tk.StringVar()
        self.download_type.set("video")  # Default selection
        self.type_label = tk.Label(self.main_frame, text="Download Type:", font=("Arial", 12))
        self.type_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.video_radio = tk.Radiobutton(self.main_frame, text="Video", variable=self.download_type, value="video", font=("Arial", 10))
        self.video_radio.grid(row=2, column=1, padx=5, sticky="w")
        self.audio_radio = tk.Radiobutton(self.main_frame, text="Audio", variable=self.download_type, value="audio", font=("Arial", 10))
        self.audio_radio.grid(row=2, column=1, padx=(80, 0), sticky="w")

        self.create_button = tk.Button(self.main_frame, text="Download", command=self.download, font=("Arial", 12))
        self.create_button.grid(row=3, columnspan=2, pady=15) 

        # Text widget to display Console Ouput
        self.console_output = tk.Text(self.main_frame, wrap=tk.WORD, height=12, width=60)
        self.console_output.grid(row=4, columnspan=2, pady=10)
        self.console_output.grid_remove() # Remove initially

        # Creating a class with write method which writes to text widget
        self.console_redirector = ConsoleRedirector(self.console_output)

    def browse(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.location_entry.delete(0,tk.END)
            self.location_entry.insert(0, selected_directory)

    def download(self):
        # Making it equal to sys.stdout so that print statements (= sys.stdout.write()) write to text widget rather than console
        sys.stdout = self.console_redirector

        # Disbale the button 
        self.create_button.config(state=tk.DISABLED)

        url = self.url_entry.get()
        download_directory = self.location_entry.get()
        download_type = self.download_type.get()

        if not url or not download_directory:
            messagebox.showwarning("Warning", "Limit should be an integer value.")
            self.create_button.config(state=tk.NORMAL)
            return
        
        else:
            def download_thread():
                try: 
                    self.root.geometry("600x530+500+150")
                    self.console_output.grid()

                    print("----------------------", flush=True)
                    print("Start!", flush=True)

                    yt = YoutubeDownloader(url)
                    
                    if download_type == "video":
                        yt.download_video(download_directory)
                    elif download_type == "audio":
                        yt.download_audio(download_directory, format="mp3")
                    
                    messagebox.showinfo("Success", "Downloaded successfully!")

                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    self.create_button.config(state=tk.NORMAL)
                    self.root.geometry("600x320+500+150")
                    self.console_output.grid_remove()

            thread = threading.Thread(target=download_thread)
            thread.start()