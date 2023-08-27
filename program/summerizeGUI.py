import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import sys
import threading
from program.transcriber import Transcriber
import os


class ConsoleRedirector:
    # Print output to text widget rather than console
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)

    def flush(self):
        self.text_widget.update_idletasks()


class SummarizeGUI:
    def __init__(self, root, summarize_tab):
        self.root = root
        self.summarize_tab = summarize_tab


        # Main Title Label
        self.title = tk.Label(self.summarize_tab, text="Video/Audio Summarizer", font="bold 22", fg="white",
                         bg="#721817", width=600, pady=10)
        self.title.pack()

        # Frame
        self.main_frame = tk.Frame(self.summarize_tab, padx=20, pady=30)
        self.main_frame.pack()

        # Media Location Widget
        self.location_label = tk.Label(self.main_frame, text="Media Location:", font=("Arial", 12), pady=8)
        self.location_label.grid(row=0, column=0, padx=5, sticky="e")
        self.location_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=28, bd=2)
        self.location_entry.grid(row=0, column=1, sticky="w")
        self.browse_button = tk.Button(self.main_frame, text="Browse", command=self.browse_media, font=("Arial", 10))
        self.browse_button.grid(row=0, column=2, padx=(5,0), sticky="e")

        # Output Location Widget
        self.outlocation_label = tk.Label(self.main_frame, text="Output Location:", font=("Arial", 12), pady=8)
        self.outlocation_label.grid(row=1, column=0, padx=5, sticky="e")
        self.outlocation_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=28, bd=2)
        self.outlocation_entry.grid(row=1, column=1, sticky="w")
        self.browse_button = tk.Button(self.main_frame, text="Browse", command=self.browse, font=("Arial", 10))
        self.browse_button.grid(row=1, column=2, padx=(5,0), sticky="e")

        # Summarization Type Label
        self.summarization_label = tk.Label(self.main_frame, text="Summarization Type:", font=("Arial", 12), pady=8)
        self.summarization_label.grid(row=2, column=0, padx=5, sticky="e")

        # Summarization Type Dropdown
        summarization_options = ["Summarize the whole", "Create summarized chapters"]
        self.summarization_type = tk.StringVar()
        self.summarization_type.set(summarization_options[0])
        self.summarization_dropdown = tk.OptionMenu(self.main_frame, self.summarization_type, *summarization_options)
        self.summarization_dropdown.grid(row=2, column=1, sticky="w", columnspan=2)
        
        # Submit Button
        self.create_button = tk.Button(self.main_frame, text="Summarize", command=self.summarize, font=("Arial", 12))
        self.create_button.grid(row=3, columnspan=3, pady=15) 

        # Text widget to display Console Ouput
        self.console_output = tk.Text(self.main_frame, wrap=tk.WORD, height=12, width=60)
        self.console_output.grid(row=4, columnspan=3, pady=10)
        self.console_output.grid_remove()

        # Console redirect
        self.console_redirector = ConsoleRedirector(self.console_output)
        sys.stdout = self.console_redirector


    def browse(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.outlocation_entry.delete(0,tk.END)
            self.outlocation_entry.insert(0, selected_directory)


    def browse_media(self):
        filetypes = [("Audio files", "*.mp3 *.wav *.ogg"), ("Video files", "*.mp4 *.webm *.mov")]
        selected_files = filedialog.askopenfilenames(filetypes=filetypes)
        if selected_files:
            self.location_entry.delete(0,tk.END)
            self.location_entry.insert(0, " ".join(selected_files))
            self.selected_files = selected_files


    def summarize(self):
        # Making it equal to sys.stdout so that print statements (= sys.stdout.write()) write to text widget rather than console
        sys.stdout = self.console_redirector

        # Disbale the button 
        self.create_button.config(state=tk.DISABLED)

        if hasattr(self, "selected_files"):
            selected_files = self.selected_files
        else:
            messagebox.showwarning("Warning", "Please select the files to be summarized.")
            self.create_button.config(state=tk.NORMAL)
            return
        
        output_directory = self.outlocation_entry.get()
        if not output_directory:
            messagebox.showwarning("Warning", "Please provide the output location.")
            self.create_button.config(state=tk.NORMAL)
            return

        if self.summarization_type.get() == "Summarize the whole":
            # payload of kwargs other ther than audio_url
            payload = {         
                "summarization": True,
                "summary_model": "informative",
                "summary_type": "bullets"
            }
        elif self.summarization_type.get() == "Create summarized chapters":
            payload = {
                "auto_chapters": True
            }
        else:
            messagebox.showerror("Error", "Nothing")
            return
        
        api_key = os.environ.get("ASSEMBLY_AI_KEY")
        if not api_key:
            api_key = simpledialog.askstring("API Key", "Please enter your AssemblyAI API key:")

        try:
            def summarize_thread():
                try:  
                    if api_key:
                        transcriber = Transcriber(api_key)

                        self.root.geometry("600x530+500+150")
                        self.console_output.grid()
                        print("----------------------", flush=True)
                        print("Start!", flush=True)

                        for file_path in selected_files:
                            filename = os.path.basename(file_path).split(".")[0]  # name without file extension i.e .txt
                            transcription_result = transcriber.transcribe(file_path, **payload, audio_start_from=600000, audio_end_at=660000)
                            Transcriber.save_output(output_directory, filename, transcription_result)
                        messagebox.showinfo("Success", "Summary successfully generated and saved!")

                except Exception as e:
                        messagebox.showerror("Error", f"An error occurred: {e}")

                finally:
                    self.create_button.config(state=tk.NORMAL)
                    self.root.geometry("600x320+500+150")
                    self.console_output.grid_remove()

            thread = threading.Thread(target=summarize_thread)
            thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.create_button.config(state=tk.NORMAL)
            self.root.geometry("600x320+500+150")
            self.console_output.grid_remove()


