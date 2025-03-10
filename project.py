import psutil
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import csv
import GPUtil

def update_system_stats():
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    gpu_usage = "N/A"
    gpu_memory = "N/A"
    
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu_usage = f"{gpus[0].load * 100:.2f}%"
        gpu_memory = f"{gpus[0].memoryUtil * 100:.2f}%"
    
    system_label.config(text=f"CPU: {cpu_usage}% | RAM: {memory_usage}% | GPU: {gpu_usage} | GPU Mem: {gpu_memory}")
    root.after(2000, update_system_stats)

def update_processes():
    for row in tree.get_children():
        tree.delete(row)
    
    for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        tree.insert('', tk.END, values=(process.info['pid'], process.info['name'], 
                                        f"{process.info['cpu_percent']}%", 
                                        f"{process.info['memory_percent']:.2f}%"))
    
    root.after(2000, update_processes)

def search_process():
    query = search_entry.get().lower()
    for row in tree.get_children():
        values = tree.item(row, 'values')
        if query in values[1].lower() or query in values[0]:
            tree.selection_set(row)
            tree.focus(row)
            return
    messagebox.showinfo("Search", "Process not found")

def sort_tree(col, reverse):
    items = [(tree.set(k, col), k) for k in tree.get_children('')]
    items.sort(reverse=reverse)
    for index, (_, k) in enumerate(items):
        tree.move(k, '', index)
    tree.heading(col, command=lambda: sort_tree(col, not reverse))

def kill_process():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a process to kill")
        return
    
    pid = tree.item(selected_item, 'values')[0]
    try:
        p = psutil.Process(int(pid))
        p.terminate()
        messagebox.showinfo("Success", f"Process {pid} terminated successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Could not terminate process: {e}")

def export_to_csv():
    with open("process_log.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["PID", "Process Name", "CPU %", "Memory %"])
        for row in tree.get_children():
            writer.writerow(tree.item(row, 'values'))
    messagebox.showinfo("Export", "Process list exported successfully")

def update_graph():
    global cpu_data, memory_data
    cpu_data.append(psutil.cpu_percent())
    memory_data.append(psutil.virtual_memory().percent)
    if len(cpu_data) > 20:
        cpu_data.pop(0)
        memory_data.pop(0)
    ax1.clear()
    ax2.clear()
    ax1.plot(cpu_data, label='CPU Usage (%)', color='blue')
    ax2.plot(memory_data, label='Memory Usage (%)', color='red')
    ax1.legend()
    ax2.legend()
    canvas.draw()
    root.after(2000, update_graph)

root = tk.Tk()
root.title("Real-Time Process Monitoring Dashboard")
root.geometry("700x550")

system_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
system_label.pack(pady=5)
update_system_stats()

title_label = tk.Label(root, text="Process Monitor", font=("Arial", 14, "bold"))
title_label.pack(pady=5)

search_frame = tk.Frame(root)
search_frame.pack(pady=5)
search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)
search_button = tk.Button(search_frame, text="Search", command=search_process)
search_button.pack(side=tk.LEFT)

tree = ttk.Treeview(root, columns=("PID", "Process Name", "CPU %", "Memory %"), show='headings')
for col in ("PID", "Process Name", "CPU %", "Memory %"):
    tree.heading(col, text=col, command=lambda _col=col: sort_tree(_col, False))
    tree.column(col, width=120)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)
refresh_button = tk.Button(button_frame, text="Refresh", command=update_processes)
refresh_button.grid(row=0, column=0, padx=5)
kill_button = tk.Button(button_frame, text="Kill Process", command=kill_process)
kill_button.grid(row=0, column=1, padx=5)
export_button = tk.Button(button_frame, text="Export CSV", command=export_to_csv)
export_button.grid(row=0, column=2, padx=5)

cpu_data, memory_data = [], []
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

update_processes()
update_graph()
root.mainloop()
