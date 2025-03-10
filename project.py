import psutil
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import GPUtil

# Function to update system stats
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

# Function to update process list
def update_processes():
    for row in tree.get_children():
        tree.delete(row)
    
    for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        tree.insert('', tk.END, values=(process.info['pid'], process.info['name'], 
                                        f"{process.info['cpu_percent']}%", 
                                        f"{process.info['memory_percent']:.2f}%"))
    
    root.after(2000, update_processes)

# Function to update graphs
def update_graph():
    global cpu_data, memory_data, gpu_data
    cpu_data.append(psutil.cpu_percent())
    memory_data.append(psutil.virtual_memory().percent)
    
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu_data.append(gpus[0].load * 100)
    else:
        gpu_data.append(0)
    
    if len(cpu_data) > 20:
        cpu_data.pop(0)
        memory_data.pop(0)
        gpu_data.pop(0)
    
    ax1.clear()
    ax2.clear()
    ax3.clear()
    
    ax1.plot(cpu_data, label='CPU Usage (%)', color='blue')
    ax2.plot(memory_data, label='Memory Usage (%)', color='red')
    ax3.plot(gpu_data, label='GPU Usage (%)', color='green')
    
    ax1.legend()
    ax2.legend()
    ax3.legend()
    canvas.draw()
    root.after(2000, update_graph)

# Initialize GUI
root = tk.Tk()
root.title("Real-Time Process Monitoring Dashboard")
root.geometry("750x600")

system_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
system_label.pack(pady=5)
update_system_stats()

tree = ttk.Treeview(root, columns=("PID", "Process Name", "CPU %", "Memory %"), show='headings')
for col in ("PID", "Process Name", "CPU %", "Memory %"):
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Graph Section
cpu_data, memory_data, gpu_data = [], [], []
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

update_processes()
update_graph()
root.mainloop()
