# gui.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from scraper_logic import scrape_channel


class YouTubeScraperApp:

    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Transcript Scraper")
        self.root.geometry("750x650")
        self.root.resizable(False, False)

        self.create_widgets()

    # =========================
    # UI BUILD
    # =========================
    def create_widgets(self):

        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        # ---------- CONFIG SECTION ----------
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding=15)
        config_frame.pack(fill="x", pady=10)

        ttk.Label(config_frame, text="YouTube API Key:").grid(row=0, column=0, sticky="w", pady=5)
        self.api_entry = ttk.Entry(config_frame, width=60, show="*")
        self.api_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(config_frame, text="Channel URL:").grid(row=1, column=0, sticky="w", pady=5)
        self.channel_entry = ttk.Entry(config_frame, width=60)
        self.channel_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(config_frame, text="Max Videos:").grid(row=2, column=0, sticky="w", pady=5)
        self.video_entry = ttk.Entry(config_frame, width=10)
        self.video_entry.insert(0, "5")
        self.video_entry.grid(row=2, column=1, sticky="w", pady=5, padx=5)

        ttk.Label(config_frame, text="Save Folder:").grid(row=3, column=0, sticky="w", pady=5)

        folder_frame = ttk.Frame(config_frame)
        folder_frame.grid(row=3, column=1, sticky="w")

        self.folder_entry = ttk.Entry(folder_frame, width=45)
        self.folder_entry.pack(side="left", padx=5)

        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side="left")

        # ---------- ACTION SECTION ----------
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=10)

        self.start_button = ttk.Button(action_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(side="left", padx=5)

        self.progress = ttk.Progressbar(action_frame, mode="indeterminate", length=200)
        self.progress.pack(side="left", padx=15)

        # ---------- LOG SECTION ----------
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding=10)
        log_frame.pack(fill="both", expand=True)

        self.log_box = tk.Text(log_frame, height=18, wrap="word")
        self.log_box.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_box.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_box.config(yscrollcommand=scrollbar.set)

        # ---------- STATUS BAR ----------
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(fill="x", side="bottom")

    # =========================
    # HELPERS
    # =========================
    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    # =========================
    # MAIN ACTION
    # =========================
    def start_scraping(self):

        api_key = self.api_entry.get().strip()
        channel_url = self.channel_entry.get().strip()
        max_videos = self.video_entry.get().strip()
        save_path = self.folder_entry.get().strip()

        if not api_key or not channel_url or not max_videos or not save_path:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            max_videos = int(max_videos)
        except ValueError:
            messagebox.showerror("Error", "Max Videos must be a number.")
            return

        self.start_button.config(state=tk.DISABLED)
        self.progress.start()
        self.log_box.delete("1.0", tk.END)
        self.status_var.set("Scraping in progress...")

        def run():
            try:
                result = scrape_channel(
                    api_key,
                    channel_url,
                    save_path,
                    max_videos,
                    logger=self.log
                )

                if result:
                    messagebox.showinfo("Success", "Scraping completed successfully.")
                    self.status_var.set("Completed successfully.")
                else:
                    messagebox.showwarning("Finished", "No transcripts collected.")
                    self.status_var.set("No transcripts found.")

            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.status_var.set("Error occurred.")

            finally:
                self.progress.stop()
                self.start_button.config(state=tk.NORMAL)

        threading.Thread(target=run, daemon=True).start()


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeScraperApp(root)
    root.mainloop()




# Ranks the videos, fetches the transcripts, number of views each video gets