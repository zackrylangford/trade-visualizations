import os
import sys
import psutil
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import pandas as pd

# Import the report modules from the reports directory
from reports import daily_profit_loss, trade_size_over_time, winning_percentage_by_hour

data_fetched = False

def check_if_running():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'python3' and 'main.py' in proc.info['cmdline'] and proc.info['pid'] != current_pid:
            print(f"Found another instance of main.py running with PID {proc.info['pid']}. Exiting.")
            sys.exit()

def fetch_and_process_data():
    global data_fetched
    try:
        api_endpoint = "https://adhp0jlvy5.execute-api.us-east-1.amazonaws.com/default/visualize-trade-data"
        response = requests.get(api_endpoint)
        data = response.json()

        if 'error' in data or 'message' in data:
            messagebox.showerror("Error", f"Error fetching data from API: {data.get('error', data.get('message'))}")
            return

        if isinstance(data, list):
            df = pd.DataFrame(data)
            update_charts(df)
            data_fetched = True
            messagebox.showinfo("Success", "Data fetched and reports generated successfully.")
        else:
            messagebox.showerror("Error", "Unexpected data format. Expected a list of dictionaries.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching data: {str(e)}")

def update_charts(df):
    update_chart(tab_winning_percentage, winning_percentage_by_hour.generate_winning_percentage_by_hour, df)
    update_chart(tab_daily_profit_loss, daily_profit_loss.generate_daily_profit_loss, df)
    update_chart(tab_trade_size, trade_size_over_time.generate_trade_size_over_time, df)

def update_chart(tab, generate_chart_func, df):
    for widget in tab.winfo_children():
        widget.destroy()
    
    fig = generate_chart_func(df)
    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=10, pady=10)

def on_closing(root):
    root.destroy()
    sys.exit()

def create_gui():
    global tab_winning_percentage, tab_daily_profit_loss, tab_trade_size
    root = tk.Tk()
    root.title("Trading Data Analysis")
    root.geometry("1300x800")

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

    notebook = ttk.Notebook(root)
    tab_winning_percentage = ttk.Frame(notebook)
    tab_daily_profit_loss = ttk.Frame(notebook)
    tab_trade_size = ttk.Frame(notebook)
    notebook.add(tab_winning_percentage, text="Winning % by Time of Day")
    notebook.add(tab_daily_profit_loss, text="Daily Profit/Loss")
    notebook.add(tab_trade_size, text="Trade Size Over Time")
    notebook.pack(expand=1, fill="both")

    refresh_button = tk.Button(root, text="Refresh Data", command=fetch_and_process_data)
    refresh_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    check_if_running()
    create_gui()
