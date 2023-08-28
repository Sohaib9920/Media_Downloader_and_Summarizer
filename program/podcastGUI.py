import tkinter as tk
from tkinter import messagebox, filedialog
from program.podcast import Podcast  
import sys
import threading


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


class PodcastGUI:
    def __init__(self, root, podcast_tab):
        self.root = root
        self.podcast_tab = podcast_tab

        # Main Title Label
        self.title = tk.Label(self.podcast_tab, text="Podcast Downloader", font="bold 22", fg="white",
                         bg="#1C2321", width=600, pady=10)
        self.title.pack()

        # Frame
        self.main_frame = tk.Frame(self.podcast_tab, padx=20, pady=30)
        self.main_frame.pack()

        # Widgets in Frame
        self.rss_label = tk.Label(self.main_frame, text="RSS Feed URL:", font=("Arial", 12), pady=4)
        self.rss_label.grid(row=0, column=0, padx=5, sticky="e")
        self.rss_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=35, bd=2)
        self.rss_entry.grid(row=0, column=1)

        self.filter_label = tk.Label(self.main_frame, text="Search Filter (optional) :", font=("Arial", 12), pady=4)
        self.filter_label.grid(row=1, column=0, padx=5, sticky="e")
        self.filter_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=35, bd=2)
        self.filter_entry.grid(row=1, column=1)

        self.limit_label = tk.Label(self.main_frame, text="Limit (optional) :", font=("Arial", 12), pady=4)
        self.limit_label.grid(row=2, column=0, padx=5, sticky="e")
        self.limit_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=35, bd=2)
        self.limit_entry.grid(row=2, column=1)

        self.location_label = tk.Label(self.main_frame, text="Downloads Location:", font=("Arial", 12), pady=4)
        self.location_label.grid(row=3, column=0, padx=5, sticky="e")
        self.location_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=28, bd=2)
        self.location_entry.grid(row=3, column=1, sticky="w")
        self.browse_button = tk.Button(self.main_frame, text="Browse", command=self.browse, font=("Arial", 10))
        self.browse_button.grid(row=3, column=1, padx=(5,0), sticky="e")

        self.create_button = tk.Button(self.main_frame, text="Download Podcast", command=self.download_podcast, font=("Arial", 12))
        self.create_button.grid(row=4, columnspan=2, pady=15) 

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

    def download_podcast(self):
        # Making it equal to sys.stdout so that print statements (= sys.stdout.write()) write to text widget rather than console
        sys.stdout = self.console_redirector

        # Disbale the button 
        self.create_button.config(state=tk.DISABLED)

        rss_feed_url = self.rss_entry.get()
        filter = self.filter_entry.get()
        limit = self.limit_entry.get()
        download_directory = self.location_entry.get()

        if not filter:
            filter = None
        if not limit:
            limit = None
        else:
            try:
                limit = int(limit)
            except ValueError:
                messagebox.showwarning("Warning", "Limit should be an integer value.")
                self.create_button.config(state=tk.NORMAL)
                return
            
        if not rss_feed_url:
            messagebox.showwarning("Warning", "Please fill in the 'RSS Feed URL' field.")
            self.create_button.config(state=tk.NORMAL)
            return
        elif not download_directory:
            messagebox.showwarning("Warning", "Please provide the 'Location' of downloads.")
            self.create_button.config(state=tk.NORMAL)
            return
        else:
            try:
                podcast = Podcast(rss_feed_url, download_directory)
                items = podcast.get_items(limit=limit, filter=filter)
                episodes_metadata = Podcast.get_episodes_metadata(items)
                num_items = len(items)

                confirmation_message = f"Number of items to be downloaded: {num_items}\n\nDo you want to proceed?"
                confirmation_result = messagebox.askquestion("Confirmation", confirmation_message)
            
                if confirmation_result == "yes":
                    # Outer try/except will not catch exception inside thread so add try/except inside thread function
                    def download_thread():
                        try: 
                            self.root.geometry("600x530+500+150")
                            self.console_output.grid()

                            print("----------------------", flush=True)
                            print("Start!", flush=True)
                            podcast.download_episodes(episodes_metadata)
                            messagebox.showinfo("Success", "Podcast created and episode downloaded successfully!")
                        except Exception as e:
                            messagebox.showerror("Error", f"An error occurred: {e}")
                        finally:
                            self.create_button.config(state=tk.NORMAL)
                            self.root.geometry("600x320+500+150")
                            self.console_output.grid_remove()

                    thread = threading.Thread(target=download_thread)
                    thread.start()
                else:
                    self.create_button.config(state=tk.NORMAL)
                    self.root.geometry("600x320+500+150")
                    self.console_output.grid_remove()

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                self.root.geometry("600x320+500+150")
                self.console_output.grid_remove()
                self.create_button.config(state=tk.NORMAL)