import os
import sys
import psutil
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import pandas as pd
from utils.window_setup import *

# Import the report modules from the reports directory
from reports import daily_profit_loss, trade_size_over_time, winning_percentage_by_hour, grouped_winning_trades

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
    update_chart(tab_winning_percentage, grouped_winning_trades.generate_grouped_winning_trades, df)
    update_chart(tab_daily_profit_loss, daily_profit_loss.generate_daily_profit_loss, df)
    update_chart(tab_trade_size, trade_size_over_time.generate_trade_size_over_time, df)

def update_chart(tab, generate_chart_func, df):
    for widget in tab.winfo_children():
        widget.destroy()
    
    fig = generate_chart_func(df)
    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

def on_closing(root):
    root.destroy()
    sys.exit()

def create_gui():
    global tab_winning_percentage, tab_daily_profit_loss, tab_trade_size
    root = tk.Tk()
    root.title("Trading Data Analysis")
    root.geometry("1300x800")

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

    notebook, tab_winning_percentage, tab_daily_profit_loss, tab_trade_size, refresh_button = create_scrollable_window(root)
    refresh_button.config(command=fetch_and_process_data)

    root.mainloop()

if __name__ == "__main__":
    check_if_running()
    create_gui()
