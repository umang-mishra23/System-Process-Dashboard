import psutil
import GPUtil
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
from ttkthemes import ThemedTk

# Graph Data Variables
cpu_data, memory_data, gpu_data = [], [], []

# Function to update system stats
def update_system_stats():
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent

    # GPU Data
    gpu_usage = "N/A"
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu_usage = gpus[0].load * 100

    net_io = psutil.net_io_counters()
    upload_speed = f"{net_io.bytes_sent / 1024:.2f} KB/s"
    download_speed = f"{net_io.bytes_recv / 1024:.2f} KB/s"

    gpu_display = f"{gpu_usage:.2f}%" if isinstance(gpu_usage, (int, float)) else "N/A"
    system_label.config(text=f"CPU: {cpu_usage}% | RAM: {memory_usage}% | GPU: {gpu_display} | Up: {upload_speed} | Down: {download_speed}")

    # Graph Data Management
    cpu_data.append(cpu_usage)
    memory_data.append(memory_usage)
    gpu_data.append(gpu_usage)

    if len(cpu_data) > 50:
        cpu_data.pop(0)
        memory_data.pop(0)
        gpu_data.pop(0)

    update_graphs()

    root.after(1000, update_system_stats)

# Function to update graphs
def update_graphs():
    ax1.clear()
    ax2.clear()
    ax3.clear()

    ax1.plot(cpu_data, label='CPU Usage (%)', color='#00ADB5', linewidth=2)
    ax2.plot(memory_data, label='Memory Usage (%)', color='#FF5722', linewidth=2)
    ax3.plot(gpu_data, label='GPU Usage (%)', color='#FFC107', linewidth=2)

    for ax, label in zip([ax1, ax2, ax3], ['CPU', 'Memory', 'GPU']):
        ax.set_facecolor('#1e1e2e')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        ax.spines['top'].set_color('#00ADB5')
        ax.spines['bottom'].set_color('#00ADB5')
        ax.spines['left'].set_color('#00ADB5')
        ax.spines['right'].set_color('#00ADB5')

    canvas.draw()

# Initialize GUI
root = ThemedTk(theme="arc")
root.title("Modern Task Manager")
root.geometry("1600x1000")
root.configure(bg="#222831")

# System Info Label
system_label = tk.Label(root, text="", font=("Arial", 18, "bold"), fg="white", bg="#222831")
system_label.pack(pady=10)

style = ttk.Style()
style.configure("Treeview", font=("Segoe UI", 14))

# Graph Setup
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8), dpi=100)
fig.patch.set_facecolor('#1e1e2e')
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

update_system_stats()
root.mainloop()
