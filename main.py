import os
import sys
import psutil
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import pandas as pd
from utils.window_setup import create_scrollable_window
from matplotlib.figure import Figure

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
    add_chart_to_tab(tab_winning_percentage, winning_percentage_by_hour.generate_winning_percentage_by_hour, df)
    add_chart_to_tab(tab_winning_percentage, grouped_winning_trades.generate_grouped_winning_trades, df)
    add_chart_to_tab(tab_daily_profit_loss, daily_profit_loss.generate_daily_profit_loss, df)
    add_chart_to_tab(tab_trade_size, trade_size_over_time.generate_trade_size_over_time, df)
    update_overview(tab_overview, df)

def add_chart_to_tab(tab, generate_chart_func, df):
    chart_frame = tk.Frame(tab)
    chart_frame.pack(fill=tk.BOTH, expand=True)

    fig = generate_chart_func(df)
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

def update_overview(tab, df):
    for widget in tab.winfo_children():
        widget.destroy()
    
    overview_frame = tk.Frame(tab)
    overview_frame.pack(fill=tk.BOTH, expand=True)

    # Add PnL calendar table
    pnl_table_frame = tk.Frame(overview_frame)
    pnl_table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    create_pnl_table(pnl_table_frame, df)

    # Add line graph for account balance
    balance_graph_frame = tk.Frame(overview_frame)
    balance_graph_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    create_balance_graph(balance_graph_frame, df)

def create_pnl_table(frame, df):
    df['CustomTradeDay'] = pd.to_datetime(df['CustomTradeDay'])
    pnl_summary = df.groupby(df['CustomTradeDay'].dt.date).agg({
        'NetPnL': 'sum'
    }).reset_index()
    
    for index, row in pnl_summary.iterrows():
        day_label = tk.Label(frame, text=f"{row['CustomTradeDay']}\n{row['NetPnL']:.2f}",
                             bg="green" if row['NetPnL'] > 0 else "red",
                             fg="white", padx=5, pady=5)
        day_label.grid(row=index // 7, column=index % 7, padx=5, pady=5, sticky="nsew")

def create_balance_graph(frame, df):
    df['CustomTradeDay'] = pd.to_datetime(df['CustomTradeDay'])
    pnl_summary = df.groupby(df['CustomTradeDay'].dt.date).agg({
        'NetPnL': 'sum'
    }).reset_index()
    pnl_summary = pnl_summary.sort_values(by='CustomTradeDay')
    pnl_summary['CumulativePnL'] = pnl_summary['NetPnL'].cumsum()
    pnl_summary['AccountBalance'] = 50000 + pnl_summary['CumulativePnL']

    fig = Figure(figsize=(10, 4))
    ax = fig.add_subplot(111)
    ax.plot(pnl_summary['CustomTradeDay'], pnl_summary['AccountBalance'], marker='o')
    ax.set_title('Account Balance Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Account Balance ($)')
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

def on_closing(root):
    root.destroy()
    sys.exit()

def create_gui():
    global tab_overview, tab_winning_percentage, tab_daily_profit_loss, tab_trade_size
    root = tk.Tk()
    root.title("Trading Data Analysis")
    root.geometry("1300x800")

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

    notebook, tab_overview, tab_winning_percentage, tab_daily_profit_loss, tab_trade_size, refresh_button = create_scrollable_window(root)
    refresh_button.config(command=fetch_and_process_data)

    root.mainloop()

if __name__ == "__main__":
    check_if_running()
    create_gui()
