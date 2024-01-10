import xml.etree.ElementTree as ET
import os
import re
import requests
from tqdm import tqdm
import tkinter as tk
from tkinter import ttk, messagebox

downloadinstructions = "To install the update to rpcs3, install all updates until the desired version; then drag and drop them onto the main rpcs3 window."

class UpdateDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Update Downloader")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")

        self.style = ttk.Style()

        # Configure the style for TButton
        self.style.configure("TButton",
                             padding=5,
                             relief="flat",
                             font=("Work Sans", 12),
                             borderwidth=1)

        # Configure the style for TLabel
        self.style.configure("TLabel",
                             padding=5,
                             relief="flat",
                             font=("Work Sans", 12))

        # Configure the style for TEntry
        self.style.configure("TEntry",
                             padding=5,
                             relief="flat",
                             font=("Work Sans", 12))

        # Game title label
        self.game_title_label = ttk.Label(root, text="")
        self.game_title_label.pack(pady=5)

        # Create a frame for button styling
        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(pady=10)

        # Use a Canvas for background color
        canvas = tk.Canvas(self.button_frame, bg="#f0f0f0", highlightthickness=0)
        canvas.pack(expand="true", fill="both")

        # Listbox widget with scrollbar
        self.listbox = tk.Listbox(canvas, selectmode=tk.SINGLE, font=("Work Sans", 12), width=50, height=10)
        self.listbox.pack(side=tk.LEFT, pady=20, padx=10)

        scrollbar = ttk.Scrollbar(canvas, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Entry widget for custom ID
        self.custom_id_label = ttk.Label(root, text="Enter a custom ID:")
        self.custom_id_label.pack(pady=5)

        self.custom_id = tk.StringVar()
        default_id = "BLUS31426"
        self.custom_id.set(default_id)
        self.custom_id_entry = ttk.Entry(root, textvariable=self.custom_id)
        self.custom_id_entry.pack(pady=5)

        # Entry widget for download directory
        default_dir = "./rpcs3-{game-title}-updates"
        self.download_dir_label = ttk.Label(self.button_frame, text="Download Directory:")
        self.download_dir_label.pack(side=tk.LEFT, padx=5)

        self.download_dir = tk.StringVar()
        self.download_dir.set(default_dir)
        self.download_dir_entry = ttk.Entry(self.button_frame, textvariable=self.download_dir)
        self.download_dir_entry.pack(side=tk.LEFT, padx=5)

        # Load Updates button
        self.load_button = ttk.Button(root, text="Load Updates", command=self.load_updates)
        self.load_button.pack(pady=5)

        # Update Selected button
        ttk.Button(self.button_frame, text="Download Selected", command=self.update_selected).pack(side=tk.LEFT, padx=5)

        # Download All button
        ttk.Button(self.button_frame, text="Download All", command=self.download_all).pack(side=tk.LEFT, padx=5)

        self.updates = []

    def load_updates(self):
        custom_id = self.custom_id.get()
        url = f"https://a0.ww.np.dl.playstation.net/tpl/np/{custom_id}/{custom_id}-ver.xml"
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            xml_content = response.content
            root = ET.fromstring(xml_content)

            self.updates = []

            # Fetching the game title from <paramsfo>
            title = root.find(".//paramsfo/TITLE").text
            self.game_title_label.config(text=title)

            # Setting the default download directory
            default_dir = f"./rpcs3-{title}-updates"
            self.download_dir.set(default_dir)

            for package in root.findall(".//package"):
                version = package.get("version")
                size = int(package.get("size"))
                size_str = self.format_size(size)
                package_url = package.get("url")

                # Display name, version, and size in the listbox
                update_info = f"Version: {version} - Size: {size_str}"
                self.updates.append((version, package_url, update_info))

            self.update_listbox()
        else:
            messagebox.showerror("Error", f"Failed to retrieve data from {url}")

    def format_size(self, size_in_bytes):
        # Convert bytes to KB, MB, or GB
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024.0

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for _, _, update_info in self.updates:  # Unreverse the list
            self.listbox.insert(tk.END, update_info)

    def update_selected(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select an update. " + downloadinstructions)
            return

        download_dir = self.download_dir.get() or "."  # Use "." if the entry is empty
        for index in selected_indices:
            _, package_url, _ = self.updates[index]
            print(f"Downloading from {package_url} to {download_dir}")
            self.download_file(package_url, download_dir)

        messagebox.showinfo("Download Completed", "Selected updates have been downloaded. " + downloadinstructions)

    def download_all(self):
        download_dir = self.download_dir.get() or "."  # Use "." if the entry is empty
        for _, package_url, _ in self.updates:
            print(f"Downloading from {package_url} to {download_dir}")
            self.download_file(package_url, download_dir)

        messagebox.showinfo("Download Completed", "All updates have been downloaded.")

    def download_file(self, url, dest_folder):
        response = requests.get(url, stream=True, verify=False)
        file_size = int(response.headers.get('content-length', 0))
        filename = url.split('/')[-1]

        # Replace invalid characters in the filename
        invalid_chars = r'\/:*?"<>|'
        filename = ''.join(c if c not in invalid_chars else '_' for c in filename)

        # Remove special characters from the folder name
        dest_folder = re.sub(r'[^\w\s-]', '', dest_folder)

        # Create the destination folder if it doesn't exist
        dest_folder_path = os.path.join(os.getcwd(), dest_folder)
        os.makedirs(dest_folder_path, exist_ok=True)

        # Combine the folder path and filename
        full_path = os.path.join(dest_folder_path, filename)

        with open(full_path, 'wb') as file, tqdm(
                desc=filename,
                total=file_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)


def main():
    root = tk.Tk()
    downloader = UpdateDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
