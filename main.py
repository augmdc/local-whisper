import os
import shutil
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

# Define directories
base_dir = os.path.expanduser("~/WhisperAudio")
audio_dir = os.path.join(base_dir, "audio")
processed_dir = os.path.join(base_dir, "processed")
text_dir = os.path.join(base_dir, "text")

# Create directories if they don't exist
os.makedirs(audio_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)
os.makedirs(text_dir, exist_ok=True)

processed_files = set()
monitoring = False

def process_audio_files():
    try:
        # List all audio files in the audio directory
        audio_files = [f for f in os.listdir(audio_dir) if os.path.isfile(os.path.join(audio_dir, f))]

        # Process each audio file
        for audio_file in audio_files:
            if audio_file not in processed_files:
                # Define the paths
                input_path = os.path.join(audio_dir, audio_file)
                output_base = os.path.join(base_dir, os.path.splitext(audio_file)[0])

                # Run Whisper command
                result = subprocess.run(["whisper", input_path, "--model", "base", "--output_dir", base_dir])
                
                if result.returncode != 0:
                    continue

                # Move the processed audio file
                shutil.move(input_path, processed_dir)
                processed_files.add(audio_file)

                # Move the text, srt, and json files to the text directory
                for ext in [".txt", ".srt", ".json"]:
                    output_file = f"{output_base}{ext}"
                    if os.path.exists(output_file):
                        shutil.move(output_file, text_dir)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def monitor_folder(interval):
    global monitoring
    while monitoring:
        process_audio_files()
        time.sleep(interval)

def start_monitoring(interval):
    global monitoring
    if not monitoring:
        monitoring = True
        threading.Thread(target=monitor_folder, args=(interval,)).start()
        messagebox.showinfo("Info", "Started monitoring folder for new files.")
    else:
        messagebox.showwarning("Warning", "Already monitoring.")

def stop_monitoring():
    global monitoring
    monitoring = False
    messagebox.showinfo("Info", "Stopped monitoring folder for new files.")

def upload_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        shutil.copy(file_path, audio_dir)
        messagebox.showinfo("Info", "File uploaded successfully")

def list_files():
    files = os.listdir(text_dir)
    file_list.delete(0, tk.END)
    for file in files:
        file_list.insert(tk.END, file)

def download_file():
    selected_file = file_list.get(tk.ACTIVE)
    if selected_file:
        file_path = os.path.join(text_dir, selected_file)
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=selected_file)
        if save_path:
            shutil.copy(file_path, save_path)
            messagebox.showinfo("Info", "File downloaded successfully")

# Set up GUI
root = tk.Tk()
root.title("Whisper Automation Script")

frame = tk.Frame(root)
frame.pack(pady=20)

interval_label = tk.Label(frame, text="Interval (seconds):")
interval_label.grid(row=0, column=0, padx=5, pady=5)

interval_entry = tk.Entry(frame)
interval_entry.grid(row=0, column=1, padx=5, pady=5)
interval_entry.insert(0, "10")

start_button = tk.Button(frame, text="Start Monitoring", command=lambda: start_monitoring(int(interval_entry.get())))
start_button.grid(row=1, column=0, padx=5, pady=5)

stop_button = tk.Button(frame, text="Stop Monitoring", command=stop_monitoring)
stop_button.grid(row=1, column=1, padx=5, pady=5)

upload_button = tk.Button(frame, text="Upload File", command=upload_file)
upload_button.grid(row=2, column=0, padx=5, pady=5)

list_button = tk.Button(frame, text="List Files", command=list_files)
list_button.grid(row=2, column=1, padx=5, pady=5)

download_button = tk.Button(frame, text="Download File", command=download_file)
download_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

file_list = tk.Listbox(frame, width=50)
file_list.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()