import psutil
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import GPUtil
import threading
import time
from ttkthemes import ThemedTk

# Function to update system stats
def update_system_stats():
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    gpu_usage, gpu_memory, gpu_temp = "N/A", "N/A", "N/A"
    
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu_usage = f"{gpus[0].load * 100:.2f}%"
        gpu_memory = f"{gpus[0].memoryUtil * 100:.2f}%"
        gpu_temp = f"{gpus[0].temperature}°C" if hasattr(gpus[0], 'temperature') else "N/A"
    
    net_io = psutil.net_io_counters()
    upload_speed = f"{net_io.bytes_sent / 1024:.2f} KB/s"
    download_speed = f"{net_io.bytes_recv / 1024:.2f} KB/s"
    
    system_label.config(text=f"CPU: {cpu_usage}% | RAM: {memory_usage}% | GPU: {gpu_usage} | GPU Mem: {gpu_memory} | GPU Temp: {gpu_temp} | Up: {upload_speed} | Down: {download_speed}")
    
    root.after(2000, update_system_stats)

# Function to update process list
def update_processes():
    processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)
    
    for row in tree.get_children():
        tree.delete(row)
    
    for process in processes:
        tree.insert('', tk.END, values=(process.info['pid'], process.info['name'], 
                                        f"{process.info['cpu_percent']}%", 
                                        f"{process.info['memory_percent']:.2f}%"))
    
    root.after(2000, update_processes)

# Function to terminate a process
def terminate_process():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a process to terminate.")
        return
    
    pid = tree.item(selected_item)['values'][0]
    try:
        process = psutil.Process(pid)
        process.terminate()
        messagebox.showinfo("Success", f"Process {pid} terminated successfully.")
        update_processes()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to terminate process {pid}: {str(e)}")

# Function to kill a process
def kill_process():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a process to kill.")
        return
    
    pid = tree.item(selected_item)['values'][0]
    try:
        process = psutil.Process(pid)
        process.kill()
        messagebox.showinfo("Success", f"Process {pid} killed successfully.")
        update_processes()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to kill process {pid}: {str(e)}")

# Initialize GUI
root = ThemedTk(theme="breeze")
root.title("Real-Time Process Monitor")
root.geometry("1300x800")
root.configure(bg="#1e1e2e")

# Sidebar
sidebar = tk.Frame(root, bg="#2a2a40", width=250, height=800)
sidebar.pack(side=tk.LEFT, fill=tk.Y)

title_label = tk.Label(sidebar, text="Process Monitor", font=("Arial", 18, "bold"), fg="white", bg="#2a2a40")
title_label.pack(pady=20)

# Terminate and Kill buttons
terminate_button = tk.Button(sidebar, text="Terminate Process", command=terminate_process, bg="#ffcc00", fg="black", font=("Arial", 12, "bold"), relief="raised", bd=3)
terminate_button.pack(pady=10, padx=10, fill=tk.X)

kill_button = tk.Button(sidebar, text="Kill Process", command=kill_process, bg="#ff4444", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=3)
kill_button.pack(pady=10, padx=10, fill=tk.X)

# Tab Structure
tabs = ttk.Notebook(root)
process_tab = ttk.Frame(tabs)
graph_tab = ttk.Frame(tabs)

tabs.add(process_tab, text="Processes")
tabs.add(graph_tab, text="Graphs")
tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# System Info Label
system_label = tk.Label(root, text="", font=("Arial", 14, "bold"), fg="white", bg="#1e1e2e")
system_label.pack(pady=5)
update_system_stats()

# Process List
columns = ("PID", "Process Name", "CPU %", "Memory %")
tree = ttk.Treeview(process_tab, columns=columns, show='headings', style="Treeview")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=160)

style = ttk.Style()
style.configure("Treeview", background="#1e1e2e", foreground="white", rowheight=30, font=("Arial", 14, "bold"), fieldbackground="#1e1e2e")
style.configure("Treeview.Heading", background="#2a2a40", foreground="white", font=("Arial", 14, "bold"))
style.map("Treeview", background=[("selected", "#444466")], foreground=[("selected", "white")])

tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Graphs
cpu_data, memory_data, gpu_data = [], [], []
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8), dpi=100)
fig.patch.set_facecolor('#1e1e2e')
canvas = FigureCanvasTkAgg(fig, master=graph_tab)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

update_processes()
update_system_stats()
root.mainloop()
