import tkinter as tk
from tkinter import messagebox, filedialog
import sys
import threading
from program.youtube import YoutubeDownloader
import pytube
import time

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

        self.button = tk.Button(self.main_frame, text="Download", command=self.download, font=("Arial", 12))
        self.button.grid(row=4, columnspan=2, pady=10) 

        # Text widget to display Console Ouput
        self.console_output = tk.Text(self.main_frame, wrap=tk.WORD, height=12, width=60)
        self.console_output.grid(row=5, columnspan=2, pady=10)
        self.console_output.grid_remove() # Remove initially

        # Creating a class with write method which writes to text widget
        self.console_redirector = ConsoleRedirector(self.console_output)

    def browse(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.location_entry.delete(0,tk.END)
            self.location_entry.insert(0, selected_directory)

    def download(self):
        sys.stdout = self.console_redirector

        self.url = self.url_entry.get()
        self.download_directory = self.location_entry.get()
        self.type = self.download_type.get()

        if not self.url or not self.download_directory:
            messagebox.showwarning("Warning", "Youtube URL and Download Location must be provided.")
            return
        
        else:
            self.button.config(state=tk.DISABLED)
            def download_thread():
                try:
                    self.yt = YoutubeDownloader(self.url) 
                    if self.type == "video":
                        self.open_resolution_dialog() 
                    else:
                        self.download_mp3()
                except pytube.exceptions.RegexMatchError:
                    messagebox.showerror("Error", "Invalid Youtube Video URL")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    self.button.config(state=tk.NORMAL)
                    self.root.geometry("600x320+500+150")
                    self.console_output.grid_remove()

            thread = threading.Thread(target=download_thread)
            thread.start()
    
    def download_mp3(self): 
        self.root.geometry("600x530+500+150")
        self.console_output.grid()
        print("----------------------", flush=True)
        print("Start!", flush=True)

        self.yt.download_mp3(self.download_directory)
        messagebox.showinfo("Success", "Download Successfully!")

    def open_resolution_dialog(self): 
        # Create new window above root window
        resolution_dialog = tk.Toplevel(self.root)
        resolution_dialog.title("Select Resolution")
        resolution_dialog.geometry("+740+380")
        # Make the dialog modal (user must interact with it)
        resolution_dialog.grab_set()

        resolutions = self.yt.availabe_resolutions()
        msg = tk.Label(resolution_dialog, text="Resolutions:")
        msg.pack()

        # Create radio buttons
        resolution_var = tk.StringVar()
        resolution_var.set(resolutions[0]) 
        for resolution in resolutions:
            tk.Radiobutton(resolution_dialog, text=resolution, variable=resolution_var, value=resolution, font=("Arial", 10)).pack()

        # Create a button to confirm resolution selection
        confirm_button = tk.Button(resolution_dialog, text="Confirm", command=lambda: self.download_video(resolution_dialog, resolution_var.get()))
        confirm_button.pack(pady=10)

    def download_video(self, dialog, res):
        # Video will only be downloaded when resolution dialog is closed with a resolution selected
        self.console_output.grid()
        self.root.geometry("600x530+500+150")
        self.button.config(state=tk.DISABLED)

        self.res = res
        dialog.destroy()

        # This function runs after the download_thread function in download function has completed, 
        # So in order to avoid not-responding, we need the download video in a new thread
        def download_video_thread():
            print("----------------------", flush=True)
            print("Start!", flush=True)
            try:
                stream, _ = self.yt.get_stream_by_resolution(self.res)
                self.yt.download_stream(stream, self.download_directory)
                messagebox.showinfo("Success", "Download Successfully!")
            except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                self.button.config(state=tk.NORMAL)
                self.root.geometry("600x320+500+150")
                self.console_output.grid_remove()
        
        thread = threading.Thread(target=download_video_thread)
        thread.start()